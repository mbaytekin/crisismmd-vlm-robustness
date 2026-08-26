#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${V3_PYTHON:-$PROJECT_ROOT/.venv-mac/bin/python}"
MODEL_PROTOCOL="${V3_FINAL_PROTOCOL:-configs/v3/final_analysis_protocol.yaml}"
DATASET_PROTOCOL="${V3_DATASET_PROTOCOL:-configs/v3/dataset_evaluation.yaml}"
PROMPT="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
PORT="${V3_CLEAN_PORT:-8094}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
START_TIMEOUT="${V3_SERVER_START_TIMEOUT:-3600}"
STOP_TIMEOUT="${V3_SERVER_STOP_TIMEOUT:-90}"
MAX_KV_SIZE="${V3_MAX_KV_SIZE:-4096}"
COHORT="both"
DRY_RUN=0
LIST_ONLY=0
CONTINUE_ON_ERROR=1
REQUESTED_MODELS=()
SERVER_PID=""
CURRENT_MODEL_ID=""
CURRENT_SERVER_LOG=""

usage() {
  cat <<'EOF'
Usage:
  scripts/run_v3_clean_benchmarks.sh [options]

Options:
  --model NAME          Select a locally cached model; repeat for a queue.
  --cohort NAME         natural, official, or both (default: both).
  --port PORT           Managed MLX server port (default: 8094).
  --dry-run             Print the plan without loading a model.
  --list                List configured models and local cache status.
  --stop-on-error       Stop after the first failed model.
  --continue-on-error   Continue to the next model (default).
  -h, --help            Show this help.

Aliases:
  qwen27       qwen35_27b_bf16
  mistral      mistral31_24b_8bit
  qwen32       qwen3vl_32b_bf16
  qwen32_8bit  qwen3vl_32b_8bit
  qwen36       qwen36_27b_bf16
  qwen235      qwen3vl_235b_a22b_4bit
  qwen397      qwen35_397b_a17b_4bit

Natural runs 3,474 exact-SHA-unique severity rows. Official runs the exact
published 529-row test split. Both are clean-only. Qwen 9B is not configured.
The script never downloads a model and stops only the server PID it starts.
EOF
}

normalize_model() {
  case "$1" in
    qwen27) echo "qwen35_27b_bf16" ;;
    mistral) echo "mistral31_24b_8bit" ;;
    qwen32) echo "qwen3vl_32b_bf16" ;;
    qwen32_8bit) echo "qwen3vl_32b_8bit" ;;
    qwen36) echo "qwen36_27b_bf16" ;;
    qwen235) echo "qwen3vl_235b_a22b_4bit" ;;
    qwen397) echo "qwen35_397b_a17b_4bit" ;;
    *) echo "$1" ;;
  esac
}

while (( $# )); do
  case "$1" in
    --model)
      [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }
      REQUESTED_MODELS+=("$(normalize_model "$2")")
      shift 2
      ;;
    --cohort)
      [[ $# -ge 2 ]] || { echo "--cohort requires a value" >&2; exit 2; }
      COHORT="$2"
      shift 2
      ;;
    --port)
      [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    --dry-run) DRY_RUN=1; shift ;;
    --list) LIST_ONLY=1; shift ;;
    --stop-on-error) CONTINUE_ON_ERROR=0; shift ;;
    --continue-on-error) CONTINUE_ON_ERROR=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$COHORT" in natural|official|both) ;; *) echo "Invalid cohort: $COHORT" >&2; exit 2 ;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT > 0 && PORT < 65536 )) || { echo "Invalid port: $PORT" >&2; exit 2; }
[[ "$CONCURRENCY" =~ ^[0-9]+$ ]] && (( CONCURRENCY > 0 )) || { echo "V3_CONCURRENCY must be positive" >&2; exit 2; }

cd "$PROJECT_ROOT"
[[ -x "$PYTHON_BIN" ]] || { echo "Python environment not found: $PYTHON_BIN" >&2; exit 1; }

model_cli=("$PYTHON_BIN" -m src.v3_final_analysis list-models --protocol "$MODEL_PROTOCOL" --format tsv)
if (( ${#REQUESTED_MODELS[@]} == 0 )); then
  model_cli+=(--defaults)
else
  for slug in "${REQUESTED_MODELS[@]}"; do model_cli+=(--model "$slug"); done
fi

if (( LIST_ONLY )); then
  "$PYTHON_BIN" -m src.v3_final_analysis list-models --protocol "$MODEL_PROTOCOL" --format tsv
  exit 0
fi

if ! model_output="$("${model_cli[@]}" 2>&1)"; then
  echo "$model_output" >&2
  exit 2
fi
MODEL_RECORDS=()
while IFS= read -r record; do [[ -n "$record" ]] && MODEL_RECORDS+=("$record"); done <<< "$model_output"
(( ${#MODEL_RECORDS[@]} > 0 )) || { echo "No models selected" >&2; exit 3; }

cohort_plan() {
  case "$1" in
    natural) echo $'natural_clean_all\t3474\tdata/v3/manifests/natural_clean_all.csv' ;;
    official) echo $'official_test\t529\tdata/v3/manifests/official_test_clean.csv' ;;
  esac
}

SELECTED_COHORTS=()
if [[ "$COHORT" == "both" ]]; then
  SELECTED_COHORTS=(natural official)
else
  SELECTED_COHORTS=("$COHORT")
fi

if (( DRY_RUN )); then
  echo "V3 clean benchmark dry-run"
  echo "Model protocol: $MODEL_PROTOCOL"
  echo "Dataset protocol: $DATASET_PROTOCOL"
  echo "Prompt: $PROMPT"
  echo "Port: $PORT"
  echo "Offline model loading: enabled"
  echo
  while IFS=$'\t' read -r slug model_id local_path precision canonical default_run result_dir role cache_complete cache_status; do
    echo "[$slug] $model_id ($precision; cache=$cache_status)"
    if [[ "$cache_complete" != "true" ]]; then
      echo "  action: SKIP (checkpoint is not complete locally)"
      continue
    fi
    for cohort_name in "${SELECTED_COHORTS[@]}"; do
      IFS=$'\t' read -r split_name expected manifest <<< "$(cohort_plan "$cohort_name")"
      echo "  $cohort_name: $expected clean rows from $manifest"
    done
  done <<< "$model_output"
  echo
  echo "No server, inference, download, or analysis was started."
  exit 0
fi

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This runner requires native Apple Silicon macOS." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -m src.v3_dataset_protocol validate; then
  echo "Build the clean manifests first:" >&2
  echo "  $PYTHON_BIN -m src.v3_dataset_protocol build" >&2
  exit 1
fi
if ! "$PYTHON_BIN" scripts/freeze_v3_artifacts.py check --prompt-config "$PROMPT"; then
  echo "Frozen V3 artifacts or prompt do not match their lock." >&2
  exit 1
fi
if ! "$PYTHON_BIN" scripts/patch_mlx_vlm_mac_thread_stream.py; then
  echo "MLX-VLM macOS compatibility check failed." >&2
  exit 1
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT is already in use; no process was stopped." >&2
  exit 1
fi

existing_mlx="$(pgrep -f 'mlx_vlm\.server' 2>/dev/null | paste -sd' ' - || true)"
if [[ -n "$existing_mlx" ]]; then
  echo "Notice: another MLX-VLM server is already running (PID(s): $existing_mlx)."
  echo "This clean queue uses port $PORT and stops only its own PID; monitor unified memory."
fi

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_ROOT="$PROJECT_ROOT/logs/v3/clean_benchmarks/$RUN_ID"
SUMMARY="$LOG_ROOT/summary.tsv"
mkdir -p "$LOG_ROOT"
printf "slug\tcohort\tmodel_id\tprecision\tstatus\texit_code\tresult_dir\n" > "$SUMMARY"

stop_server() {
  local pid="$SERVER_PID"
  [[ -n "$pid" ]] || return 0
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping clean-benchmark MLX server PID $pid..."
    local children=()
    while IFS= read -r child; do [[ -n "$child" ]] && children+=("$child"); done < <(pgrep -P "$pid" 2>/dev/null || true)
    (( ${#children[@]} )) && kill -TERM "${children[@]}" 2>/dev/null || true
    kill -TERM "$pid" 2>/dev/null || true
    local deadline=$((SECONDS + STOP_TIMEOUT))
    while kill -0 "$pid" 2>/dev/null && (( SECONDS < deadline )); do sleep 1; done
    if kill -0 "$pid" 2>/dev/null; then
      kill -KILL "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
    echo "Model offloaded; checkpoint remains in the local cache."
  fi
  SERVER_PID=""
  sleep 2
}
trap 'stop_server' EXIT
trap 'stop_server; exit 130' INT TERM

wait_for_server() {
  local deadline=$((SECONDS + START_TIMEOUT))
  while (( SECONDS < deadline )); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "Server exited while loading $CURRENT_MODEL_ID." >&2
      tail -n 100 "$CURRENT_SERVER_LOG" >&2 || true
      return 1
    fi
    if "$PYTHON_BIN" - "$CURRENT_MODEL_ID" "$PORT" >/dev/null 2>&1 <<'PY'
import json, sys, urllib.request
expected, port = sys.argv[1:]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
    health = json.load(response)
if health.get("status") != "healthy" or health.get("loaded_model") != expected:
    raise SystemExit(1)
PY
    then
      return 0
    fi
    sleep 5
  done
  echo "Timed out loading $CURRENT_MODEL_ID after ${START_TIMEOUT}s." >&2
  tail -n 100 "$CURRENT_SERVER_LOG" >&2 || true
  return 1
}

start_server() {
  local model_log_dir="$1"
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $PORT became occupied; no process was stopped." >&2
    return 1
  fi
  CURRENT_SERVER_LOG="$model_log_dir/server.log"
  echo "Loading $CURRENT_MODEL_ID on 127.0.0.1:$PORT"
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
    "$PYTHON_BIN" -m mlx_vlm.server \
      --model "$CURRENT_MODEL_ID" --host 127.0.0.1 --port "$PORT" \
      --max-kv-size "$MAX_KV_SIZE" --vision-cache-size 1 --trust-remote-code \
      > "$CURRENT_SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$model_log_dir/server.pid"
  wait_for_server
}

output_complete() {
  local predictions="$1" expected="$2"
  if ! "$PYTHON_BIN" -m src.v3_final_analysis check-output \
    --predictions "$predictions" --n-per-condition "$expected" --conditions clean \
    >/dev/null 2>&1; then
    return 1
  fi
  "$PYTHON_BIN" - "$predictions" "$CURRENT_MODEL_ID" >/dev/null <<'PY'
import json, sys
from pathlib import Path

path, expected = Path(sys.argv[1]), sys.argv[2]
models = {
    json.loads(line).get("model_id", "")
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
}
raise SystemExit(0 if models == {expected} else 1)
PY
}

run_cohort() {
  local slug="$1" cohort_name="$2" model_log_dir="$3"
  local split_name expected manifest
  IFS=$'\t' read -r split_name expected manifest <<< "$(cohort_plan "$cohort_name")"
  local result_dir="$PROJECT_ROOT/results/v3/clean_benchmarks/$slug/$cohort_name"
  local predictions="$result_dir/predictions.jsonl"
  local analysis_dir="$PROJECT_ROOT/reports/v3/clean_benchmarks/$slug/$cohort_name"
  local rc=0
  if output_complete "$predictions" "$expected"; then
    echo "Resume: $slug/$cohort_name already has $expected parsed clean predictions."
  else
    VLM_BASE_URL="http://127.0.0.1:$PORT/v1" V3_EXPECTED_MODEL_ID="$CURRENT_MODEL_ID" \
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      "$PYTHON_BIN" -m src.v3_inference run \
        --run-id "${RUN_ID}__${slug}__${cohort_name}" \
        --split "$split_name" --conditions clean --concurrency "$CONCURRENCY" \
        --prompt-config "$PROMPT" --manifest "$manifest" --output-dir "$result_dir" \
        --smoke-report-path "$result_dir/smoke_test.json" \
        2>&1 | tee "$model_log_dir/${cohort_name}_inference.log"
    rc="${PIPESTATUS[0]}"
  fi
  if (( rc == 0 )); then
    "$PYTHON_BIN" -m src.v3_final_analysis analyze-clean \
      --predictions "$predictions" --manifest "$manifest" \
      --output-dir "$analysis_dir" --model-slug "$slug" --cohort "$cohort_name" \
      --dataset-protocol "$DATASET_PROTOCOL" \
      2>&1 | tee "$model_log_dir/${cohort_name}_analysis.log"
    rc="${PIPESTATUS[0]}"
  fi
  local status=completed
  (( rc == 0 )) || status=failed
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$slug" "$cohort_name" "$CURRENT_MODEL_ID" "$CURRENT_PRECISION" \
    "$status" "$rc" "$result_dir" >> "$SUMMARY"
  return "$rc"
}

completed=0
failed=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug CURRENT_MODEL_ID local_path CURRENT_PRECISION canonical default_run result_dir role cache_complete cache_status <<< "$record"
  model_log_dir="$LOG_ROOT/$slug"
  mkdir -p "$model_log_dir"
  echo
  echo "================================================================"
  echo "Clean benchmarks: $slug | $CURRENT_MODEL_ID | $CURRENT_PRECISION"
  echo "Local cache: $cache_status"
  echo "================================================================"
  if [[ "$cache_complete" != "true" ]]; then
    echo "Skipping $slug: local checkpoint is incomplete; no download attempted."
    for cohort_name in "${SELECTED_COHORTS[@]}"; do
      printf "%s\t%s\t%s\t%s\tskipped_cache\t3\t-\n" \
        "$slug" "$cohort_name" "$CURRENT_MODEL_ID" "$CURRENT_PRECISION" >> "$SUMMARY"
    done
    failed=$((failed + 1))
    (( CONTINUE_ON_ERROR )) && continue || break
  fi
  if ! start_server "$model_log_dir"; then
    failed=$((failed + 1))
    stop_server
    (( CONTINUE_ON_ERROR )) && continue || break
  fi
  model_failed=0
  for cohort_name in "${SELECTED_COHORTS[@]}"; do
    if run_cohort "$slug" "$cohort_name" "$model_log_dir"; then
      completed=$((completed + 1))
    else
      failed=$((failed + 1))
      model_failed=1
      (( CONTINUE_ON_ERROR )) || break
    fi
  done
  stop_server
  if (( model_failed && ! CONTINUE_ON_ERROR )); then break; fi
done

trap - EXIT INT TERM
echo
echo "Clean benchmark queue finished: completed=$completed failed_or_skipped=$failed"
echo "Summary: $SUMMARY"
echo "Analysis: $PROJECT_ROOT/reports/v3/clean_benchmarks"
(( failed == 0 ))
