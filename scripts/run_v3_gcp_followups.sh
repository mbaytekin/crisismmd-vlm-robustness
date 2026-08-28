#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${V3_PYTHON:-$HOME/venvs/crisismmd-py312/bin/python}"
MODEL_CONFIG="${V3_GCP_CONFIG:-configs/v3/gcp_a100_models.yaml}"
FOLLOWUP_CONFIG="${V3_FOLLOWUP_CONFIG:-configs/v3/followup_ablation_protocol.yaml}"
PROMPT="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
PORT="${V3_GCP_PORT:-8000}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
SHUTDOWN_ON_EXIT="${V3_SHUTDOWN_ON_EXIT:-0}"
MODEL=""
KIND="both"
DRY_RUN=0
SERVER_PID=""
MODEL_ID=""
MODEL_SLUG=""
JOB_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
START_EPOCH="$(date -u +%s)"

usage() {
  cat <<'EOF'
Usage: scripts/run_v3_gcp_followups.sh --model NAME [options]

Options:
  --model NAME   Model alias from configs/v3/gcp_a100_models.yaml.
  --kind KIND    text, size, or both (default: both).
  --port PORT    Managed vLLM port (default: 8000).
  --dry-run      Prepare/audit manifests and print the request counts only.
  -h, --help     Show this help.

Set V3_SHUTDOWN_ON_EXIT=1 for detached cloud jobs. The runner records elapsed
time, resumes from SQLite caches, and stops only the vLLM server it starts.
EOF
}

while (( $# )); do
  case "$1" in
    --model) [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }; MODEL="$2"; shift 2 ;;
    --kind) [[ $# -ge 2 ]] || { echo "--kind requires a value" >&2; exit 2; }; KIND="$2"; shift 2 ;;
    --port) [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }; PORT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$MODEL" ]] || { echo "--model is required" >&2; exit 2; }
case "$KIND" in text|size|both) ;; *) echo "Invalid --kind: $KIND" >&2; exit 2 ;; esac
[[ -x "$PYTHON_BIN" ]] || { echo "Python environment missing: $PYTHON_BIN" >&2; exit 1; }

MODEL_RECORD="$($PYTHON_BIN - "$MODEL_CONFIG" "$MODEL" <<'PY'
import sys, yaml
config = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
requested = sys.argv[2]
for model in config["models"]:
    if requested == model["slug"] or requested in model.get("aliases", []):
        print("\t".join((model["slug"], model["model_id"], model["precision"], model["role"])))
        break
else:
    raise SystemExit(f"Unknown model: {requested}")
PY
)" || exit 2
IFS=$'\t' read -r MODEL_SLUG MODEL_ID PRECISION ROLE <<< "$MODEL_RECORD"

stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    for _ in $(seq 1 60); do kill -0 "$SERVER_PID" 2>/dev/null || break; sleep 1; done
    kill -0 "$SERVER_PID" 2>/dev/null && kill -KILL "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=""
}

finish() {
  local rc="$1" end_epoch duration timing_dir
  stop_server
  end_epoch="$(date -u +%s)"
  duration=$((end_epoch - START_EPOCH))
  timing_dir="logs/v3/gcp_a100/timed_jobs/${JOB_STAMP}__${MODEL_SLUG}__followup_${KIND}"
  mkdir -p "$timing_dir"
  "$PYTHON_BIN" - "$timing_dir/timing.json" "$MODEL_SLUG" "$MODEL_ID" "$KIND" "$START_EPOCH" "$end_epoch" "$duration" "$rc" <<'PY'
import json, platform, sys
path, slug, model_id, kind, start, end, duration, rc = sys.argv[1:]
payload = {
    "schema_version": 1, "model": slug, "model_id": model_id,
    "stage": "supervisor_followup", "kind": kind, "hostname": platform.node(),
    "start_epoch": int(start), "end_epoch": int(end),
    "duration_seconds": int(duration), "return_code": int(rc),
}
open(path, "w", encoding="utf-8").write(json.dumps(payload, indent=2) + "\n")
PY
  echo "Follow-up duration: ${duration}s; return_code=$rc"
  if [[ "$SHUTDOWN_ON_EXIT" == "1" ]]; then
    sudo shutdown -h now || true
  fi
}
trap 'rc=$?; finish "$rc"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "Checking frozen follow-up artifacts before model load..."
if "$PYTHON_BIN" -m src.v3_followup_ablations --config "$FOLLOWUP_CONFIG" check --kind "$KIND" >/dev/null 2>&1; then
  echo "Resume: follow-up artifacts already exist and passed audit."
else
  echo "Preparing missing or incomplete follow-up artifacts..."
  "$PYTHON_BIN" -m src.v3_followup_ablations --config "$FOLLOWUP_CONFIG" prepare --kind "$KIND"
fi

read_conditions() {
  "$PYTHON_BIN" - "$FOLLOWUP_CONFIG" "$1" <<'PY'
import sys, yaml
config = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
kind = sys.argv[2]
if kind == "text":
    values = config["text_rhetoric"]["conditions"]
else:
    points = config["size_response_pt"]["nominal_points"]
    values = ["clean"] + [f"{semantic}_pt{int(point):02d}" for semantic in ("benign", "direct", "misleading") for point in points]
print("\n".join(values))
PY
}

if (( DRY_RUN )); then
  for current in text size; do
    [[ "$KIND" != both && "$KIND" != "$current" ]] && continue
    mapfile -t conditions < <(read_conditions "$current")
    sources=120; [[ "$current" == size ]] && sources=60
    echo "$current: $sources sources x ${#conditions[@]} conditions = $((sources * ${#conditions[@]})) requests"
  done
  exit 0
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use; no process was stopped." >&2
  exit 5
fi

LOG_ROOT="logs/v3/gcp_a100/$JOB_STAMP/$MODEL_SLUG/followups"
mkdir -p "$LOG_ROOT"
vllm_args=(serve "$MODEL_ID" --served-model-name "$MODEL_ID" --host 127.0.0.1 --port "$PORT"
  --dtype bfloat16 --gpu-memory-utilization 0.92 --max-model-len 4096 --max-num-seqs 1
  --limit-mm-per-prompt '{"image":1}' --trust-remote-code)
if [[ "$MODEL_SLUG" == mistral31_24b_bf16 ]]; then
  vllm_args+=(--tokenizer-mode mistral --config-format mistral --load-format mistral)
fi
VLLM_USE_FLASHINFER_SAMPLER=0 "$PYTHON_BIN" -m vllm.entrypoints.cli.main "${vllm_args[@]}" \
  > "$LOG_ROOT/server.log" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 720); do
  kill -0 "$SERVER_PID" 2>/dev/null || { tail -n 120 "$LOG_ROOT/server.log" >&2; exit 6; }
  if "$PYTHON_BIN" - "$MODEL_ID" "$PORT" <<'PY' >/dev/null 2>&1
import json, sys, urllib.request
with urllib.request.urlopen(f"http://127.0.0.1:{sys.argv[2]}/v1/models", timeout=5) as response:
    ids = {item.get("id") for item in json.load(response).get("data", [])}
raise SystemExit(0 if sys.argv[1] in ids else 1)
PY
  then break; fi
  sleep 5
done

run_kind() {
  local current="$1" split manifest sources result_dir report_dir run_id
  local conditions=()
  mapfile -t conditions < <(read_conditions "$current")
  if [[ "$current" == text ]]; then
    split=text_rhetoric_ablation
    manifest=data/v3/manifests/text_rhetoric_ablation_conditions.csv
    sources=120
  else
    split=size_response_pt
    manifest=data/v3/manifests/size_response_pt_conditions.csv
    sources=60
  fi
  result_dir="results/v3/gcp_a100/$MODEL_SLUG/followups/$current"
  report_dir="reports/v3/gcp_a100/models/$MODEL_SLUG/followups/$current"
  run_id="${JOB_STAMP}__${MODEL_SLUG}__followup_${current}__gcp_a100"
  mkdir -p "$result_dir" "$report_dir"
  if "$PYTHON_BIN" -m src.v3_final_analysis check-output \
      --predictions "$result_dir/predictions.jsonl" --n-per-condition "$sources" \
      --conditions "${conditions[@]}" >/dev/null 2>&1; then
    echo "Resume: complete $current follow-up already exists for $MODEL_SLUG"
  else
    VLM_BASE_URL="http://127.0.0.1:$PORT/v1" \
    V3_EXPECTED_MODEL_ID="$MODEL_ID" \
    V3_EXECUTION_ENVIRONMENT="gcp_a100_80gb_vllm" \
    V3_ACCELERATOR="NVIDIA A100-SXM4-80GB" \
    V3_OPENAI_TIMEOUT_SECONDS="${V3_OPENAI_TIMEOUT_SECONDS:-300}" \
      "$PYTHON_BIN" -m src.v3_inference run \
        --run-id "$run_id" --split "$split" --conditions "${conditions[@]}" \
        --concurrency "$CONCURRENCY" --prompt-config "$PROMPT" --manifest "$manifest" \
        --output-dir "$result_dir" --smoke-report-path "$result_dir/smoke_test.json" \
        2>&1 | tee "$LOG_ROOT/$current.log"
    (( ${PIPESTATUS[0]} == 0 )) || return 7
  fi
  "$PYTHON_BIN" -m src.v3_followup_ablations --config "$FOLLOWUP_CONFIG" analyze \
    --kind "$current" --predictions "$result_dir/predictions.jsonl" --manifest "$manifest" \
    --output-dir "$report_dir" --model-slug "${MODEL_SLUG}__gcp_a100"
}

rc=0
if [[ "$KIND" == text || "$KIND" == both ]]; then run_kind text || rc=$?; fi
if (( rc == 0 )) && [[ "$KIND" == size || "$KIND" == both ]]; then run_kind size || rc=$?; fi
exit "$rc"
