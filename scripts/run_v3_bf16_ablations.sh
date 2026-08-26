#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${V3_PYTHON:-$PROJECT_ROOT/.venv-mac/bin/python}"
CONFIG="${V3_ABLATION_PROTOCOL:-configs/v3/ablation_protocol.yaml}"
PROMPT="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
PORT="${V3_ABLATION_PORT:-8093}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
MAX_KV_SIZE="${V3_MAX_KV_SIZE:-4096}"
START_TIMEOUT="${V3_SERVER_START_TIMEOUT:-3600}"
KIND="both"
DRY_RUN=0
LIST_ONLY=0
REQUESTED_MODELS=()
SERVER_PID=""
CURRENT_MODEL_ID=""
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

STYLE_CONDITIONS=(clean benign_simple benign_news benign_camouflage direct_simple direct_news direct_camouflage misleading_simple misleading_news misleading_camouflage)
SIZE_CONDITIONS=(clean benign_small benign_medium benign_large direct_small direct_medium direct_large misleading_small misleading_medium misleading_large)

usage() {
  cat <<'EOF'
Usage: scripts/run_v3_bf16_ablations.sh [options]

Options:
  --model NAME       Select a verified local model or alias; repeat for a queue.
  --kind KIND        style, size, or both (default: both).
  --port PORT        Managed MLX server port (default: 8093).
  --dry-run          Validate data/cache/RAM and print the plan only.
  --list             List configured ablation models and cache status.
  -h, --help         Show this help.

Defaults: qwen35_27b_bf16, mistral31_24b_8bit, qwen3vl_32b_8bit.
Explicit-only aliases: qwen36, mistral, gemma12, qwen36_moe, qwen32, gemma31.

The runner never downloads a checkpoint and never stops unrelated processes.
Other training or inference processes are reported as resource warnings.
EOF
}

while (( $# )); do
  case "$1" in
    --model)
      [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }
      REQUESTED_MODELS+=("$2")
      shift 2
      ;;
    --kind)
      [[ $# -ge 2 ]] || { echo "--kind requires a value" >&2; exit 2; }
      KIND="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    --list) LIST_ONLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$KIND" in style|size|both) ;; *) echo "Invalid --kind: $KIND" >&2; exit 2 ;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT > 0 && PORT < 65536 )) || { echo "Invalid port: $PORT" >&2; exit 2; }
[[ "$CONCURRENCY" =~ ^[0-9]+$ ]] && (( CONCURRENCY > 0 )) || { echo "V3_CONCURRENCY must be positive" >&2; exit 2; }
[[ -x "$PYTHON_BIN" ]] || { echo "Python environment not found: $PYTHON_BIN" >&2; exit 1; }

model_records() {
  "$PYTHON_BIN" - "$CONFIG" "$LIST_ONLY" ${REQUESTED_MODELS[@]+"${REQUESTED_MODELS[@]}"} <<'PY'
import sys
from pathlib import Path
import yaml

config_path = Path(sys.argv[1])
list_only = sys.argv[2] == "1"
requested = sys.argv[3:]
config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
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
    selected = []
    seen = set()
    for name in requested:
        model = by_name[name]
        if model["slug"] not in seen:
            selected.append(model)
            seen.add(model["slug"])
else:
    selected = models if list_only else [model for model in models if model.get("default_run")]

cache_root = Path.home() / ".cache" / "huggingface" / "hub"
for model in selected:
    repo_dir = cache_root / ("models--" + model["model_id"].replace("/", "--"))
    snapshots = sorted((repo_dir / "snapshots").glob("*")) if (repo_dir / "snapshots").is_dir() else []
    candidates = [path for path in snapshots if (path / "config.json").is_file() and list(path.glob("*.safetensors"))]
    incomplete = list(repo_dir.rglob("*.incomplete")) if repo_dir.exists() else []
    complete = bool(candidates) and not incomplete
    snapshot = str(candidates[-1]) if complete else "-"
    status = "complete" if complete else (f"partial:{len(incomplete)}" if repo_dir.exists() else "missing")
    print("\t".join([
        model["slug"], model["model_id"], snapshot, str(model["expected_peak_gib"]),
        str(model.get("default_run", False)).lower(), model["role"], status,
    ]))
PY
}

if (( LIST_ONLY )); then
  printf "%-28s %-8s %-14s %s\n" "SLUG" "PEAK_GIB" "CACHE" "MODEL_ID"
  while IFS=$'\t' read -r slug model_id snapshot peak default_run role status; do
    printf "%-28s %-8s %-14s %s\n" "$slug" "$peak" "$status" "$model_id"
  done < <(model_records)
  exit 0
fi

if ! MODEL_OUTPUT="$(model_records 2>&1)"; then
  echo "$MODEL_OUTPUT" >&2
  exit 2
fi
MODEL_RECORDS=()
while IFS= read -r record; do [[ -n "$record" ]] && MODEL_RECORDS+=("$record"); done <<< "$MODEL_OUTPUT"
(( ${#MODEL_RECORDS[@]} > 0 )) || { echo "No models selected" >&2; exit 3; }

AVAILABLE_GIB="$($PYTHON_BIN - <<'PY'
import re
import subprocess
text = subprocess.check_output(["vm_stat"], text=True)
page_match = re.search(r"page size of (\d+) bytes", text)
page_size = int(page_match.group(1)) if page_match else 16384
values = {}
for line in text.splitlines():
    match = re.match(r"([^:]+):\s+([0-9.]+)", line)
    if match:
        values[match.group(1)] = float(match.group(2).rstrip("."))
available_pages = sum(values.get(name, 0) for name in (
    "Pages free", "Pages inactive", "Pages speculative", "Pages purgeable"
))
print(f"{available_pages * page_size / (1024**3):.1f}")
PY
)"
RESERVE_GIB="$($PYTHON_BIN - "$CONFIG" <<'PY'
import sys, yaml
print(yaml.safe_load(open(sys.argv[1]))["runtime"]["minimum_post_load_reserve_gib"])
PY
)"

echo "V3 ablation preflight"
echo "  available/reclaimable memory: ${AVAILABLE_GIB} GiB"
echo "  required post-load reserve: ${RESERVE_GIB} GiB"
echo "  selected port: $PORT"
echo "  concurrent requests per model: $CONCURRENCY"

BUSY_PROCESSES="$(ps -axo pid=,rss=,command= | awk '/mlx_vlm\.server|src\.v3_inference|train_vlm_lora\.py/ && $0 !~ /awk/ {print}')"
if [[ -n "$BUSY_PROCESSES" ]]; then
  echo
  echo "Resource warning: other VLM work is active. It will not be stopped:"
  echo "$BUSY_PROCESSES"
fi

if ! "$PYTHON_BIN" -m src.v3_ablation_protocol --check-only >/dev/null; then
  echo "Ablation dataset audit failed; inference will not start." >&2
  exit 4
fi

if (( DRY_RUN )); then
  echo
  echo "Dry-run model plan:"
  for record in "${MODEL_RECORDS[@]}"; do
    IFS=$'\t' read -r slug model_id snapshot peak default_run role status <<< "$record"
    required=$((peak + RESERVE_GIB))
    echo "  $slug: cache=$status, expected_peak=${peak} GiB, required_available=${required} GiB"
    echo "    style: 120 sources x 10 conditions = 1200 predictions"
    echo "    size:   60 sources x 10 conditions = 600 predictions"
  done
  exit 0
fi

port_is_free() {
  ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1
}

stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Stopping managed MLX server PID $SERVER_PID"
    kill "$SERVER_PID" 2>/dev/null || true
    for _ in $(seq 1 30); do
      kill -0 "$SERVER_PID" 2>/dev/null || break
      sleep 1
    done
  fi
  SERVER_PID=""
  CURRENT_MODEL_ID=""
}
trap stop_server EXIT INT TERM

wait_for_server() {
  local model_id="$1" log_path="$2" elapsed=0
  while (( elapsed < START_TIMEOUT )); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "MLX server exited while loading $model_id" >&2
      tail -n 80 "$log_path" >&2 || true
      return 1
    fi
    if V3_HEALTH_URL="http://127.0.0.1:$PORT/v1/models" V3_HEALTH_MODEL="$model_id" \
      "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import json, os, urllib.request
with urllib.request.urlopen(os.environ["V3_HEALTH_URL"], timeout=2) as response:
    payload = json.load(response)
served = {item.get("id") for item in payload.get("data", [])}
raise SystemExit(0 if os.environ["V3_HEALTH_MODEL"] in served else 1)
PY
    then
      return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  echo "Timed out waiting for $model_id" >&2
  tail -n 80 "$log_path" >&2 || true
  return 1
}

output_complete() {
  local predictions="$1" n="$2"; shift 2
  "$PYTHON_BIN" -m src.v3_final_analysis check-output \
    --predictions "$predictions" --n-per-condition "$n" --conditions "$@" >/dev/null 2>&1
}

run_kind() {
  local slug="$1" kind="$2" result_dir="$3" log_path="$4"
  local split manifest n analysis_dir
  local conditions=()
  if [[ "$kind" == "style" ]]; then
    split="style_ablation"
    manifest="data/v3/manifests/style_ablation_conditions.csv"
    n=120
    conditions=("${STYLE_CONDITIONS[@]}")
  else
    split="size_ablation"
    manifest="data/v3/manifests/size_ablation_conditions.csv"
    n=60
    conditions=("${SIZE_CONDITIONS[@]}")
  fi
  analysis_dir="reports/v3/final_analysis/models/$slug/secondary/$kind"
  mkdir -p "$result_dir" "$(dirname "$log_path")"
  if output_complete "$result_dir/predictions.jsonl" "$n" "${conditions[@]}"; then
    echo "Resume: complete $kind output already exists for $slug"
  else
    VLM_BASE_URL="http://127.0.0.1:$PORT/v1" V3_EXPECTED_MODEL_ID="$CURRENT_MODEL_ID" \
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      "$PYTHON_BIN" -m src.v3_inference run \
        --run-id "${RUN_STAMP}__${slug}__${kind}_ablation" \
        --split "$split" --conditions "${conditions[@]}" --concurrency "$CONCURRENCY" \
        --prompt-config "$PROMPT" --manifest "$manifest" --output-dir "$result_dir" \
        --smoke-report-path "$result_dir/smoke_test.json" 2>&1 | tee "$log_path"
    local inference_rc="${PIPESTATUS[0]}"
    (( inference_rc == 0 )) || return "$inference_rc"
  fi
  "$PYTHON_BIN" -m src.v3_final_analysis analyze-ablation \
    --protocol configs/v3/final_analysis_protocol.yaml \
    --predictions "$result_dir/predictions.jsonl" --manifest "$manifest" \
    --output-dir "$analysis_dir" --model-slug "$slug" --kind "$kind" 2>&1 | tee -a "$log_path"
  return "${PIPESTATUS[0]}"
}

completed=0
failed=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug model_id snapshot peak default_run role status <<< "$record"
  echo
  echo "[$slug] $model_id"
  if [[ "$status" != "complete" ]]; then
    echo "Skipping $slug because cache status is $status"
    failed=$((failed + 1))
    continue
  fi
  AVAILABLE_NOW="$($PYTHON_BIN - <<'PY'
import re, subprocess
text=subprocess.check_output(["vm_stat"],text=True)
page=int(re.search(r"page size of (\d+) bytes",text).group(1))
values={m.group(1):float(m.group(2).rstrip('.')) for line in text.splitlines() if (m:=re.match(r"([^:]+):\s+([0-9.]+)",line))}
pages=sum(values.get(k,0) for k in ("Pages free","Pages inactive","Pages speculative","Pages purgeable"))
print(f"{pages*page/(1024**3):.1f}")
PY
)"
  if ! "$PYTHON_BIN" - "$AVAILABLE_NOW" "$peak" "$RESERVE_GIB" <<'PY'
import sys
available, peak, reserve = map(float, sys.argv[1:])
raise SystemExit(0 if available >= peak + reserve else 1)
PY
  then
    echo "Skipping $slug: available ${AVAILABLE_NOW} GiB is below peak+reserve $((peak + RESERVE_GIB)) GiB" >&2
    failed=$((failed + 1))
    continue
  fi
  if ! port_is_free; then
    echo "Port $PORT is already in use; no process was stopped." >&2
    exit 5
  fi
  model_log_dir="logs/v3/ablations/$RUN_STAMP/$slug"
  mkdir -p "$model_log_dir"
  server_log="$model_log_dir/server.log"
  CURRENT_MODEL_ID="$model_id"
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
    "$PYTHON_BIN" -m mlx_vlm.server --model "$model_id" --host 127.0.0.1 --port "$PORT" \
      --max-kv-size "$MAX_KV_SIZE" --vision-cache-size 1 --trust-remote-code \
      > "$server_log" 2>&1 &
  SERVER_PID=$!
  if ! wait_for_server "$model_id" "$server_log"; then
    failed=$((failed + 1))
    stop_server
    continue
  fi

  model_root="results/v3/final_ablation/$slug/ablations"
  rc=0
  if [[ "$KIND" == "style" || "$KIND" == "both" ]]; then
    run_kind "$slug" style "$model_root/style" "$model_log_dir/style.log" || rc=$?
  fi
  if (( rc == 0 )) && [[ "$KIND" == "size" || "$KIND" == "both" ]]; then
    run_kind "$slug" size "$model_root/size" "$model_log_dir/size.log" || rc=$?
  fi
  stop_server
  if (( rc == 0 )); then
    completed=$((completed + 1))
  else
    echo "$slug failed with exit code $rc; the next model will still be attempted." >&2
    failed=$((failed + 1))
  fi
done

echo
echo "V3 ablation queue finished: completed=$completed failed_or_skipped=$failed"
echo "Reports: reports/v3/final_analysis/models/<model>/secondary/{style,size}"
(( failed == 0 ))
