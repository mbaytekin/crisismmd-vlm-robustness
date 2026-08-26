#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

CONFIG="${V3_GCP_CONFIG:-configs/v3/gcp_a100_models.yaml}"
PROMPT="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
ANALYSIS_PROTOCOL="${V3_FINAL_PROTOCOL:-configs/v3/final_analysis_protocol.yaml}"
DATASET_PROTOCOL="${V3_DATASET_PROTOCOL:-configs/v3/dataset_evaluation.yaml}"
PYTHON_BIN="${V3_PYTHON:-$HOME/venvs/crisismmd-py312/bin/python}"
HF_HOME="${HF_HOME:-$HOME/hf-cache}"
export HF_HOME
PORT="${V3_GCP_PORT:-8000}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
STAGE="ablation"
KIND="both"
COHORT="both"
DRY_RUN=0
LIST_ONLY=0
REQUESTED_MODELS=()
SERVER_PID=""
CURRENT_MODEL_ID=""
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

MAIN_CONDITIONS=(clean benign_image benign_text benign_joint direct_image direct_text direct_joint misleading_image misleading_text misleading_joint)
STYLE_CONDITIONS=(clean benign_simple benign_news benign_camouflage direct_simple direct_news direct_camouflage misleading_simple misleading_news misleading_camouflage)
SIZE_CONDITIONS=(clean benign_small benign_medium benign_large direct_small direct_medium direct_large misleading_small misleading_medium misleading_large)

usage() {
  cat <<'EOF'
Usage: scripts/run_v3_gcp_a100.sh [options]

Options:
  --model NAME     Select a model or alias; repeat to build a queue.
  --stage STAGE    main, ablation, clean, or all (default: ablation).
  --kind KIND      style, size, or both (default: both; ablation only).
  --cohort NAME    natural, official, or both (default: both; clean only).
  --port PORT      Managed vLLM port (default: 8000).
  --dry-run        Validate inputs and print the execution plan.
  --list           List configured CUDA models.
  -h, --help       Show this help.

No --model means all configured models in file order. The runner downloads
public upstream checkpoints on the GCP VM, serves one model at a time, resumes
from each result directory's SQLite cache, and never touches MLX result paths.
EOF
}

while (( $# )); do
  case "$1" in
    --model) [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }; REQUESTED_MODELS+=("$2"); shift 2 ;;
    --stage) [[ $# -ge 2 ]] || { echo "--stage requires a value" >&2; exit 2; }; STAGE="$2"; shift 2 ;;
    --kind) [[ $# -ge 2 ]] || { echo "--kind requires a value" >&2; exit 2; }; KIND="$2"; shift 2 ;;
    --cohort) [[ $# -ge 2 ]] || { echo "--cohort requires a value" >&2; exit 2; }; COHORT="$2"; shift 2 ;;
    --port) [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }; PORT="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    --list) LIST_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$STAGE" in main|ablation|clean|all) ;; *) echo "Invalid --stage: $STAGE" >&2; exit 2 ;; esac
case "$KIND" in style|size|both) ;; *) echo "Invalid --kind: $KIND" >&2; exit 2 ;; esac
case "$COHORT" in natural|official|both) ;; *) echo "Invalid --cohort: $COHORT" >&2; exit 2 ;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT > 0 && PORT < 65536 )) || { echo "Invalid port: $PORT" >&2; exit 2; }
[[ "$CONCURRENCY" =~ ^[0-9]+$ ]] && (( CONCURRENCY > 0 )) || { echo "V3_CONCURRENCY must be positive" >&2; exit 2; }
[[ -x "$PYTHON_BIN" ]] || { echo "Python environment not found: $PYTHON_BIN" >&2; exit 1; }
command -v nvidia-smi >/dev/null || { echo "NVIDIA runtime not found" >&2; exit 1; }
command -v ninja >/dev/null || { echo "ninja-build is required for FlashInfer JIT kernels" >&2; exit 1; }

model_records() {
  "$PYTHON_BIN" - "$CONFIG" ${REQUESTED_MODELS[@]+"${REQUESTED_MODELS[@]}"} <<'PY'
import sys
from pathlib import Path
import yaml

config = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
requested = sys.argv[2:]
models = config["models"]
by_name = {}
for model in models:
    by_name[model["slug"]] = model
    for alias in model.get("aliases", []):
        by_name[alias] = model
if requested:
    unknown = [name for name in requested if name not in by_name]
    if unknown:
        raise SystemExit("Unknown model(s): " + ", ".join(unknown))
    selected, seen = [], set()
    for name in requested:
        model = by_name[name]
        if model["slug"] not in seen:
            selected.append(model)
            seen.add(model["slug"])
else:
    selected = models
for model in selected:
    print("\t".join((model["slug"], model["model_id"], model["precision"], model["role"])))
PY
}

if ! MODEL_OUTPUT="$(model_records 2>&1)"; then echo "$MODEL_OUTPUT" >&2; exit 2; fi
MODEL_RECORDS=()
while IFS= read -r record; do [[ -n "$record" ]] && MODEL_RECORDS+=("$record"); done <<< "$MODEL_OUTPUT"
(( ${#MODEL_RECORDS[@]} > 0 )) || { echo "No models selected" >&2; exit 3; }

if (( LIST_ONLY )); then
  printf "%-24s %-8s %-48s %s\n" SLUG PRECISION MODEL_ID ROLE
  for record in "${MODEL_RECORDS[@]}"; do
    IFS=$'\t' read -r slug model_id precision role <<< "$record"
    printf "%-24s %-8s %-48s %s\n" "$slug" "$precision" "$model_id" "$role"
  done
  exit 0
fi

for path in "$PROMPT" "$ANALYSIS_PROTOCOL" \
  data/v3/manifests/all_conditions.csv \
  data/v3/manifests/style_ablation_conditions.csv \
  data/v3/manifests/size_ablation_conditions.csv \
  data/v3/manifests/natural_clean_all.csv \
  data/v3/manifests/official_test_clean.csv; do
  [[ -f "$path" ]] || { echo "Required artifact missing: $path" >&2; exit 4; }
done

if (( DRY_RUN )); then
  echo "GCP A100 dry-run: stage=$STAGE kind=$KIND port=$PORT concurrency=$CONCURRENCY"
  nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
  for record in "${MODEL_RECORDS[@]}"; do
    IFS=$'\t' read -r slug model_id precision role <<< "$record"
    echo "  $slug: $model_id ($precision; $role)"
    [[ "$STAGE" == main || "$STAGE" == all ]] && echo "    main: 720 x 10 = 7200 predictions"
    [[ "$STAGE" == ablation || "$STAGE" == all ]] && [[ "$KIND" != size ]] && echo "    style: 120 x 10 = 1200 predictions"
    [[ "$STAGE" == ablation || "$STAGE" == all ]] && [[ "$KIND" != style ]] && echo "    size: 60 x 10 = 600 predictions"
    [[ "$STAGE" == clean || "$STAGE" == all ]] && [[ "$COHORT" != official ]] && echo "    natural clean: 3474 predictions"
    [[ "$STAGE" == clean || "$STAGE" == all ]] && [[ "$COHORT" != natural ]] && echo "    official clean: 529 predictions"
  done
  exit 0
fi

port_is_free() { ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; }

stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Stopping managed vLLM server PID $SERVER_PID"
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    for _ in $(seq 1 60); do kill -0 "$SERVER_PID" 2>/dev/null || break; sleep 1; done
    kill -0 "$SERVER_PID" 2>/dev/null && kill -KILL "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  SERVER_PID=""
  CURRENT_MODEL_ID=""
  sleep 3
}
trap stop_server EXIT INT TERM

wait_for_server() {
  local expected="$1" log_path="$2" elapsed=0 timeout=3600
  while (( elapsed < timeout )); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "vLLM exited while loading $expected" >&2
      tail -n 120 "$log_path" >&2 || true
      return 1
    fi
    if "$PYTHON_BIN" - "$expected" "$PORT" <<'PY' >/dev/null 2>&1
import json, sys, urllib.request
expected, port = sys.argv[1:]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=5) as response:
    served = {item.get("id") for item in json.load(response).get("data", [])}
raise SystemExit(0 if expected in served else 1)
PY
    then return 0; fi
    sleep 5
    elapsed=$((elapsed + 5))
  done
  echo "Timed out waiting for $expected" >&2
  tail -n 120 "$log_path" >&2 || true
  return 1
}

output_complete() {
  local predictions="$1" n="$2"; shift 2
  "$PYTHON_BIN" -m src.v3_final_analysis check-output \
    --predictions "$predictions" --n-per-condition "$n" --conditions "$@" >/dev/null 2>&1
}

run_inference() {
  local run_id="$1" split="$2" manifest="$3" result_dir="$4" log_path="$5"; shift 5
  mkdir -p "$result_dir" "$(dirname "$log_path")"
  VLM_BASE_URL="http://127.0.0.1:$PORT/v1" \
  V3_EXPECTED_MODEL_ID="$CURRENT_MODEL_ID" \
  V3_EXECUTION_ENVIRONMENT="gcp_a100_80gb_vllm" \
  V3_ACCELERATOR="NVIDIA A100-SXM4-80GB" \
  V3_OPENAI_TIMEOUT_SECONDS="${V3_OPENAI_TIMEOUT_SECONDS:-300}" \
    "$PYTHON_BIN" -m src.v3_inference run \
      --run-id "$run_id" --split "$split" --conditions "$@" \
      --concurrency "$CONCURRENCY" --prompt-config "$PROMPT" --manifest "$manifest" \
      --output-dir "$result_dir" --smoke-report-path "$result_dir/smoke_test.json" \
      2>&1 | tee "$log_path"
  return "${PIPESTATUS[0]}"
}

run_track() {
  local slug="$1" kind="$2" model_root="$3" log_root="$4"
  local split manifest n result_dir analysis_dir
  local conditions=()
  case "$kind" in
    main)
      split=main; manifest=data/v3/manifests/all_conditions.csv; n=720
      result_dir="$model_root/main"; analysis_dir="reports/v3/gcp_a100/models/$slug/main"
      conditions=("${MAIN_CONDITIONS[@]}") ;;
    style)
      split=style_ablation; manifest=data/v3/manifests/style_ablation_conditions.csv; n=120
      result_dir="$model_root/ablations/style"; analysis_dir="reports/v3/gcp_a100/models/$slug/secondary/style"
      conditions=("${STYLE_CONDITIONS[@]}") ;;
    size)
      split=size_ablation; manifest=data/v3/manifests/size_ablation_conditions.csv; n=60
      result_dir="$model_root/ablations/size"; analysis_dir="reports/v3/gcp_a100/models/$slug/secondary/size"
      conditions=("${SIZE_CONDITIONS[@]}") ;;
    natural)
      split=natural_clean_all; manifest=data/v3/manifests/natural_clean_all.csv; n=3474
      result_dir="$model_root/clean_benchmarks/natural"; analysis_dir="reports/v3/gcp_a100/models/$slug/clean_benchmarks/natural"
      conditions=(clean) ;;
    official)
      split=official_test; manifest=data/v3/manifests/official_test_clean.csv; n=529
      result_dir="$model_root/clean_benchmarks/official"; analysis_dir="reports/v3/gcp_a100/models/$slug/clean_benchmarks/official"
      conditions=(clean) ;;
  esac
  if output_complete "$result_dir/predictions.jsonl" "$n" "${conditions[@]}"; then
    echo "Resume: complete $kind output already exists for $slug"
  else
    run_inference "${RUN_STAMP}__${slug}__${kind}__gcp_a100" "$split" "$manifest" \
      "$result_dir" "$log_root/$kind.log" "${conditions[@]}" || return $?
  fi
  mkdir -p "$analysis_dir"
  if [[ "$kind" == main ]]; then
    "$PYTHON_BIN" -m src.v3_final_analysis analyze \
      --protocol "$ANALYSIS_PROTOCOL" --predictions "$result_dir/predictions.jsonl" \
      --manifest "$manifest" --output-dir "$analysis_dir" --model-slug "${slug}__gcp_a100"
  elif [[ "$kind" == style || "$kind" == size ]]; then
    "$PYTHON_BIN" -m src.v3_final_analysis analyze-ablation \
      --protocol "$ANALYSIS_PROTOCOL" --predictions "$result_dir/predictions.jsonl" \
      --manifest "$manifest" --output-dir "$analysis_dir" --model-slug "${slug}__gcp_a100" --kind "$kind"
  else
    "$PYTHON_BIN" -m src.v3_final_analysis analyze-clean \
      --predictions "$result_dir/predictions.jsonl" --manifest "$manifest" \
      --output-dir "$analysis_dir" --model-slug "${slug}__gcp_a100" --cohort "$kind" \
      --dataset-protocol "$DATASET_PROTOCOL"
  fi
}

completed=0
failed=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug model_id precision role <<< "$record"
  echo
  echo "================================================================"
  echo "Model: $slug"
  echo "Upstream ID: $model_id"
  echo "Runtime: GCP A100 80GB / vLLM / $precision"
  echo "================================================================"
  if ! port_is_free; then echo "Port $PORT is already in use; nothing was stopped." >&2; exit 5; fi
  log_root="logs/v3/gcp_a100/$RUN_STAMP/$slug"
  model_root="results/v3/gcp_a100/$slug"
  mkdir -p "$log_root" "$model_root"
  CURRENT_MODEL_ID="$model_id"

  vllm_args=(serve "$model_id" --served-model-name "$model_id" --host 127.0.0.1 --port "$PORT"
    --dtype bfloat16 --gpu-memory-utilization 0.92 --max-model-len 4096 --max-num-seqs 1
    --limit-mm-per-prompt '{"image":1}' --trust-remote-code)
  if [[ "$slug" == mistral31_24b_bf16 ]]; then
    vllm_args+=(--tokenizer-mode mistral --config-format mistral --load-format mistral)
  fi
  VLLM_USE_FLASHINFER_SAMPLER=0 \
    "$PYTHON_BIN" -m vllm.entrypoints.cli.main "${vllm_args[@]}" >"$log_root/server.log" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$log_root/server.pid"
  if ! wait_for_server "$model_id" "$log_root/server.log"; then
    failed=$((failed + 1)); stop_server; continue
  fi
  "$PYTHON_BIN" - "$model_id" "$slug" "$log_root/runtime.json" <<'PY'
import json, platform, subprocess, sys
from importlib.metadata import version
model_id, slug, output = sys.argv[1:]
gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], text=True).strip()
payload = {"model_slug": slug, "model_id": model_id, "gpu": gpu, "platform": platform.platform(),
           "python": platform.python_version(), "packages": {name: version(name) for name in ("vllm", "torch", "transformers")}}
open(output, "w", encoding="utf-8").write(json.dumps(payload, indent=2) + "\n")
PY

  rc=0
  if [[ "$STAGE" == main || "$STAGE" == all ]]; then run_track "$slug" main "$model_root" "$log_root" || rc=$?; fi
  if (( rc == 0 )) && [[ "$STAGE" == ablation || "$STAGE" == all ]] && [[ "$KIND" != size ]]; then
    run_track "$slug" style "$model_root" "$log_root" || rc=$?
  fi
  if (( rc == 0 )) && [[ "$STAGE" == ablation || "$STAGE" == all ]] && [[ "$KIND" != style ]]; then
    run_track "$slug" size "$model_root" "$log_root" || rc=$?
  fi
  if (( rc == 0 )) && [[ "$STAGE" == clean || "$STAGE" == all ]] && [[ "$COHORT" != official ]]; then
    run_track "$slug" natural "$model_root" "$log_root" || rc=$?
  fi
  if (( rc == 0 )) && [[ "$STAGE" == clean || "$STAGE" == all ]] && [[ "$COHORT" != natural ]]; then
    run_track "$slug" official "$model_root" "$log_root" || rc=$?
  fi
  stop_server
  if (( rc == 0 )); then completed=$((completed + 1)); else failed=$((failed + 1)); fi
done

echo
echo "GCP A100 queue finished: completed=$completed failed=$failed"
echo "Predictions: results/v3/gcp_a100/<model>/"
echo "Reports: reports/v3/gcp_a100/models/<model>/"
(( failed == 0 ))
