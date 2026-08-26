#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${V3_PYTHON:-$PROJECT_ROOT/.venv-mac/bin/python}"
PROTOCOL="${V3_FINAL_PROTOCOL:-configs/v3/final_analysis_protocol.yaml}"
PROMPT="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
P7_PROMPT="configs/prompts/p7_modality_neutral_sensitivity.yaml"
MANIFEST="data/v3/manifests/all_conditions.csv"
REPORT_ROOT="reports/v3/final_analysis"
PORT="${V3_MLX_PORT:-8091}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
START_TIMEOUT="${V3_SERVER_START_TIMEOUT:-3600}"
STOP_TIMEOUT="${V3_SERVER_STOP_TIMEOUT:-90}"
MAX_KV_SIZE="${V3_MAX_KV_SIZE:-4096}"
STAGE="all"
DRY_RUN=0
LIST_ONLY=0
CONTINUE_ON_ERROR=1
INCLUDE_SECONDARY=0
REQUESTED_MODELS=()
SERVER_PID=""
SERVER_OWNER_TOKEN=""
CURRENT_SERVER_LOG=""

MAIN_CONDITIONS=(clean benign_image benign_text benign_joint direct_image direct_text direct_joint misleading_image misleading_text misleading_joint)
STYLE_CONDITIONS=(clean benign_simple benign_news benign_camouflage direct_simple direct_news direct_camouflage misleading_simple misleading_news misleading_camouflage)
SIZE_CONDITIONS=(clean benign_small benign_medium benign_large direct_small direct_medium direct_large misleading_small misleading_medium misleading_large)

usage() {
  cat <<'EOF'
Usage:
  scripts/run_v3_final_experiments.sh [options]

Options:
  --model NAME          Select a model; repeat to create a queue.
  --stage STAGE         all, clean, attack, or analysis (default: all).
  --include-secondary   After main, run style, size, and P7 pilot sensitivity.
  --dry-run             Print the resolved plan without loading a model.
  --list                List configured models and local cache status.
  --stop-on-error       Stop the queue after the first model failure.
  --continue-on-error   Continue to the next model (default).
  --port PORT           Managed MLX server port (default: 8091).
  -h, --help            Show this help.

Aliases:
  qwen27       qwen35_27b_bf16 (default, canonical BF16)
  mistral      mistral31_24b_8bit (default, cross-family)
  mistral_bf16 mistral31_24b_bf16
  qwen32       qwen3vl_32b_bf16
  qwen32_8bit  qwen3vl_32b_8bit
  qwen36       qwen36_27b_bf16
  qwen235      qwen3vl_235b_a22b_4bit
  qwen397      qwen35_397b_a17b_4bit

With no --model option, Qwen3.5-27B BF16 and Mistral 24B 8-bit are run.
Qwen 9B is historical only and is never selected by this script.
No model is downloaded. Missing or partial checkpoints are skipped.
EOF
}

normalize_model() {
  case "$1" in
    qwen27) echo "qwen35_27b_bf16" ;;
    mistral) echo "mistral31_24b_8bit" ;;
    mistral_bf16) echo "mistral31_24b_bf16" ;;
    mistralbf16) echo "mistral31_24b_bf16" ;;
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
    --stage)
      [[ $# -ge 2 ]] || { echo "--stage requires a value" >&2; exit 2; }
      STAGE="$2"
      shift 2
      ;;
    --include-secondary) INCLUDE_SECONDARY=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --list) LIST_ONLY=1; shift ;;
    --stop-on-error) CONTINUE_ON_ERROR=0; shift ;;
    --continue-on-error) CONTINUE_ON_ERROR=1; shift ;;
    --port)
      [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }
      PORT="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$STAGE" in all|clean|attack|analysis) ;; *) echo "Invalid stage: $STAGE" >&2; exit 2 ;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT > 0 && PORT < 65536 )) || { echo "Invalid port: $PORT" >&2; exit 2; }
[[ "$CONCURRENCY" =~ ^[0-9]+$ ]] && (( CONCURRENCY > 0 )) || { echo "V3_CONCURRENCY must be positive" >&2; exit 2; }

cd "$PROJECT_ROOT"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found: $PYTHON_BIN" >&2
  exit 1
fi

model_cli=("$PYTHON_BIN" -m src.v3_final_analysis list-models --protocol "$PROTOCOL" --format tsv)
if (( ${#REQUESTED_MODELS[@]} == 0 )); then
  model_cli+=(--defaults)
else
  for slug in "${REQUESTED_MODELS[@]}"; do model_cli+=(--model "$slug"); done
fi

if (( LIST_ONLY )); then
  printf "%-30s %-10s %-18s %s\n" "SLUG" "PRECISION" "CACHE" "MODEL_ID"
  while IFS=$'\t' read -r slug model_id local_path precision canonical default_run result_dir role cache_complete cache_status; do
    [[ -n "$slug" ]] || continue
    printf "%-30s %-10s %-18s %s\n" "$slug" "$precision" "$cache_status" "$model_id"
  done < <("$PYTHON_BIN" -m src.v3_final_analysis list-models --protocol "$PROTOCOL" --format tsv)
  exit 0
fi

if ! model_output="$("${model_cli[@]}" 2>&1)"; then
  echo "$model_output" >&2
  exit 2
fi
MODEL_RECORDS=()
while IFS= read -r record; do [[ -n "$record" ]] && MODEL_RECORDS+=("$record"); done <<< "$model_output"
(( ${#MODEL_RECORDS[@]} > 0 )) || { echo "No models selected" >&2; exit 3; }

if (( DRY_RUN )); then
  echo "V3 final experiment dry-run"
  echo "Protocol: $PROTOCOL"
  echo "Stage: $STAGE"
  echo "Prompt: $PROMPT"
  echo "Port: $PORT"
  echo "Concurrency: $CONCURRENCY"
  echo "Offline mode: enabled; downloads disabled"
  echo "Secondary sensitivity: $INCLUDE_SECONDARY"
  echo
  while IFS=$'\t' read -r slug model_id local_path precision canonical default_run result_dir role cache_complete cache_status; do
    echo "[$slug]"
    echo "  model_id: $model_id"
    echo "  precision: $precision"
    echo "  local_snapshot: $local_path"
    echo "  cache: $cache_status"
    echo "  result_dir: $result_dir"
    if [[ "$cache_complete" != "true" ]]; then
      echo "  action: SKIP (no download)"
    elif [[ "$STAGE" == "analysis" ]]; then
      echo "  action: analyze existing $result_dir/predictions.jsonl"
    else
      echo "  server: $PYTHON_BIN -m mlx_vlm.server --model $model_id --host 127.0.0.1 --port $PORT ..."
      echo "  main: clean 720 -> all 10 conditions x 720 -> per-model analysis"
      if (( INCLUDE_SECONDARY )) && [[ "$slug" == "qwen35_27b_bf16" || "$slug" == "qwen3vl_32b_bf16" ]]; then
        echo "  secondary: style 1200 rows; size 600 rows; paired P5/P7 pilot 900+900 rows"
      fi
    fi
    echo
  done <<< "$model_output"
  echo "No files, servers, downloads, inference, or analysis were created by this dry-run."
  exit 0
fi

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This runner requires native Apple Silicon macOS." >&2
  exit 1
fi

if ! "$PYTHON_BIN" scripts/freeze_v3_artifacts.py check --prompt-config "$PROMPT"; then
  echo "Canonical V3 artifacts do not match the frozen lock; aborting before inference." >&2
  exit 1
fi

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_ROOT="$PROJECT_ROOT/logs/v3/final_runs/$RUN_ID"
RUN_MANIFEST="$LOG_ROOT/run_manifest.json"
SUMMARY="$LOG_ROOT/summary.tsv"
mkdir -p "$LOG_ROOT"
printf "slug\tmodel_id\tprecision\tstatus\texit_code\tresult_dir\tlog_dir\n" > "$SUMMARY"

selected_csv="$(printf '%s\n' "${MODEL_RECORDS[@]}" | cut -f1 | paste -sd, -)"
"$PYTHON_BIN" - "$RUN_MANIFEST" "$RUN_ID" "$PROTOCOL" "$PROMPT" "$STAGE" "$selected_csv" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path, run_id, protocol, prompt, stage, selected = sys.argv[1:]
payload = {
    "schema_version": 1,
    "run_id": run_id,
    "started_at": datetime.now(timezone.utc).isoformat(),
    "ended_at": None,
    "status": "running",
    "protocol": protocol,
    "prompt": prompt,
    "stage": stage,
    "selected_models": selected.split(",") if selected else [],
    "offline_only": True,
    "models": {},
}
Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY

capture_environment() {
  local output="$LOG_ROOT/environment.txt"
  {
    echo "run_id=$RUN_ID"
    date -u '+utc=%Y-%m-%dT%H:%M:%SZ'
    uname -a
    sw_vers 2>/dev/null || true
    sysctl -n hw.memsize 2>/dev/null | awk '{printf "unified_memory_bytes=%s\n",$1}'
    df -h "$PROJECT_ROOT"
    "$PYTHON_BIN" --version
    "$PYTHON_BIN" -m pip show mlx-vlm mlx pandas Pillow PyYAML 2>/dev/null || true
    git rev-parse HEAD 2>/dev/null || true
    git status --short 2>/dev/null || true
    vm_stat 2>/dev/null || true
  } > "$output"
}
capture_environment

manifest_model_update() {
  local slug="$1" status="$2" stage_name="$3" pid_value="$4" exit_code="$5" result_dir="$6" model_id="$7" precision="$8" local_path="$9"
  "$PYTHON_BIN" - "$RUN_MANIFEST" "$slug" "$status" "$stage_name" "$pid_value" "$exit_code" "$result_dir" "$model_id" "$precision" "$local_path" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
slug, status, stage, pid, exit_code, result_dir, model_id, precision, local_path = sys.argv[2:]
payload = json.loads(path.read_text(encoding="utf-8"))
record = payload["models"].setdefault(slug, {
    "model_id": model_id, "precision": precision, "local_model_path": local_path,
    "result_dir": result_dir, "started_at": datetime.now(timezone.utc).isoformat(),
})
record.update({"status": status, "stage": stage, "updated_at": datetime.now(timezone.utc).isoformat()})
if pid: record["server_pid"] = int(pid)
if exit_code: record["exit_code"] = int(exit_code)
path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY
}

finalize_manifest() {
  local status="$1"
  "$PYTHON_BIN" - "$RUN_MANIFEST" "$status" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
path = Path(sys.argv[1]); payload = json.loads(path.read_text(encoding="utf-8"))
payload["status"] = sys.argv[2]; payload["ended_at"] = datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
PY
}

if ! "$PYTHON_BIN" scripts/patch_mlx_vlm_mac_thread_stream.py 2>&1 | tee "$LOG_ROOT/mlx_compatibility.log"; then
  echo "Required MLX-VLM macOS compatibility check failed." >&2
  finalize_manifest failed_preflight
  exit 1
fi

port_is_free() {
  ! lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1
}

stop_server() {
  local pid="$SERVER_PID"
  [[ -n "$pid" ]] || return 0
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping managed MLX server PID $pid..."
    local children=()
    while IFS= read -r child; do [[ -n "$child" ]] && children+=("$child"); done < <(pgrep -P "$pid" 2>/dev/null || true)
    (( ${#children[@]} )) && kill -TERM "${children[@]}" 2>/dev/null || true
    kill -TERM "$pid" 2>/dev/null || true
    local deadline=$((SECONDS + STOP_TIMEOUT))
    while kill -0 "$pid" 2>/dev/null && (( SECONDS < deadline )); do sleep 1; done
    if kill -0 "$pid" 2>/dev/null; then
      echo "Managed PID $pid did not stop in ${STOP_TIMEOUT}s; sending SIGKILL to that PID only." >&2
      kill -KILL "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
    echo "Model offloaded; checkpoint remains on disk."
  fi
  SERVER_PID=""
  SERVER_OWNER_TOKEN=""
  sleep 2
}
trap 'stop_server' EXIT
trap 'stop_server; finalize_manifest interrupted; exit 130' INT TERM

wait_for_server() {
  local expected="$1" health_path="$2"
  local deadline=$((SECONDS + START_TIMEOUT))
  while (( SECONDS < deadline )); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "Server PID $SERVER_PID exited during model load." >&2
      tail -n 100 "$CURRENT_SERVER_LOG" >&2 || true
      return 1
    fi
    if "$PYTHON_BIN" - "$expected" "$PORT" "$health_path" >/dev/null 2>&1 <<'PY'
import json, sys, urllib.request
from pathlib import Path
expected, port, output = sys.argv[1:]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5) as response:
    health = json.load(response)
if health.get("status") != "healthy" or health.get("loaded_model") != expected:
    raise SystemExit(1)
Path(output).write_text(json.dumps(health, indent=2), encoding="utf-8")
PY
    then
      return 0
    fi
    sleep 5
  done
  echo "Timed out after ${START_TIMEOUT}s loading $expected." >&2
  tail -n 100 "$CURRENT_SERVER_LOG" >&2 || true
  return 1
}

start_server() {
  local model_id="$1" model_log_dir="$2"
  if ! port_is_free; then
    echo "Port $PORT is already in use. It will not be killed automatically." >&2
    return 1
  fi
  CURRENT_SERVER_LOG="$model_log_dir/server.log"
  SERVER_OWNER_TOKEN="$RUN_ID:$model_id"
  echo "Loading $model_id (server log: $CURRENT_SERVER_LOG)"
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 \
    "$PYTHON_BIN" -m mlx_vlm.server \
      --model "$model_id" --host 127.0.0.1 --port "$PORT" \
      --max-kv-size "$MAX_KV_SIZE" --vision-cache-size 1 --trust-remote-code \
      > "$CURRENT_SERVER_LOG" 2>&1 &
  SERVER_PID=$!
  echo "$SERVER_PID" > "$model_log_dir/server.pid"
  wait_for_server "$model_id" "$model_log_dir/health.json"
}

output_complete() {
  local predictions="$1" n="$2"; shift 2
  "$PYTHON_BIN" -m src.v3_final_analysis check-output \
    --predictions "$predictions" --n-per-condition "$n" --conditions "$@" >/dev/null 2>&1
}

run_inference() {
  local run_id="$1" split="$2" prompt="$3" manifest="$4" result_dir="$5" log_path="$6"; shift 6
  VLM_BASE_URL="http://127.0.0.1:$PORT/v1" V3_EXPECTED_MODEL_ID="$CURRENT_MODEL_ID" \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
    "$PYTHON_BIN" -m src.v3_inference run \
      --run-id "$run_id" --split "$split" --conditions "$@" \
      --concurrency "$CONCURRENCY" --prompt-config "$prompt" --manifest "$manifest" \
      --output-dir "$result_dir" --smoke-report-path "$result_dir/smoke_test.json" \
      2>&1 | tee "$log_path"
  return "${PIPESTATUS[0]}"
}

write_deployment_gate() {
  local result_dir="$1"
  "$PYTHON_BIN" -m src.v3_final_analysis deployment-gate \
    --predictions "$result_dir/predictions.jsonl" \
    --manifest "$MANIFEST" --protocol "$PROTOCOL" \
    --output "$result_dir/deployment_readiness_gate.json"
}

run_secondary() {
  local slug="$1" model_log_dir="$2" base_result="$3" rc=0
  local secondary_root="$(dirname "$base_result")/secondary"
  local style_dir="$secondary_root/style" size_dir="$secondary_root/size"
  local p5_dir="$secondary_root/p5_pilot" p7_dir="$secondary_root/p7_pilot"
  local analysis_root="$PROJECT_ROOT/$REPORT_ROOT/models/$slug/secondary"

  if ! output_complete "$style_dir/predictions.jsonl" 120 "${STYLE_CONDITIONS[@]}"; then
    run_inference "${RUN_ID}__${slug}__style" style_ablation "$PROMPT" "$MANIFEST" "$style_dir" "$model_log_dir/style.log" "${STYLE_CONDITIONS[@]}" || rc=$?
  else echo "Resume: style output already complete for $slug"; fi
  (( rc == 0 )) || return "$rc"

  if ! output_complete "$size_dir/predictions.jsonl" 60 "${SIZE_CONDITIONS[@]}"; then
    run_inference "${RUN_ID}__${slug}__size" size_ablation "$PROMPT" "$MANIFEST" "$size_dir" "$model_log_dir/size.log" "${SIZE_CONDITIONS[@]}" || rc=$?
  else echo "Resume: size output already complete for $slug"; fi
  (( rc == 0 )) || return "$rc"

  if ! output_complete "$p5_dir/predictions.jsonl" 90 "${MAIN_CONDITIONS[@]}"; then
    run_inference "${RUN_ID}__${slug}__p5_pilot" pilot "$PROMPT" "$MANIFEST" "$p5_dir" "$model_log_dir/p5_pilot.log" "${MAIN_CONDITIONS[@]}" || rc=$?
  else echo "Resume: P5 pilot output already complete for $slug"; fi
  (( rc == 0 )) || return "$rc"

  if ! output_complete "$p7_dir/predictions.jsonl" 90 "${MAIN_CONDITIONS[@]}"; then
    run_inference "${RUN_ID}__${slug}__p7_pilot" pilot "$P7_PROMPT" "$MANIFEST" "$p7_dir" "$model_log_dir/p7_pilot.log" "${MAIN_CONDITIONS[@]}" || rc=$?
  else echo "Resume: P7 pilot output already complete for $slug"; fi
  (( rc == 0 )) || return "$rc"

  "$PYTHON_BIN" -m src.v3_final_analysis analyze-ablation \
    --protocol "$PROTOCOL" --predictions "$style_dir/predictions.jsonl" --manifest "$MANIFEST" \
    --output-dir "$analysis_root/style" --model-slug "$slug" --kind style \
    2>&1 | tee "$model_log_dir/style_analysis.log"
  rc="${PIPESTATUS[0]}"; (( rc == 0 )) || return "$rc"

  "$PYTHON_BIN" -m src.v3_final_analysis analyze-ablation \
    --protocol "$PROTOCOL" --predictions "$size_dir/predictions.jsonl" --manifest "$MANIFEST" \
    --output-dir "$analysis_root/size" --model-slug "$slug" --kind size \
    2>&1 | tee "$model_log_dir/size_analysis.log"
  rc="${PIPESTATUS[0]}"; (( rc == 0 )) || return "$rc"

  "$PYTHON_BIN" -m src.v3_final_analysis analyze \
    --protocol "$PROTOCOL" --predictions "$p5_dir/predictions.jsonl" --manifest "$MANIFEST" \
    --output-dir "$analysis_root/p5_pilot" --model-slug "$slug" \
    2>&1 | tee "$model_log_dir/p5_analysis.log"
  rc="${PIPESTATUS[0]}"; (( rc == 0 )) || return "$rc"

  "$PYTHON_BIN" -m src.v3_final_analysis analyze \
    --protocol "$PROTOCOL" --predictions "$p7_dir/predictions.jsonl" --manifest "$MANIFEST" \
    --output-dir "$analysis_root/p7_pilot" --model-slug "$slug" \
    2>&1 | tee "$model_log_dir/p7_analysis.log"
  rc="${PIPESTATUS[0]}"; (( rc == 0 )) || return "$rc"

  "$PYTHON_BIN" -m src.v3_final_analysis compare-prompts \
    --protocol "$PROTOCOL" --p5-predictions "$p5_dir/predictions.jsonl" \
    --p7-predictions "$p7_dir/predictions.jsonl" --manifest "$MANIFEST" \
    --output "$analysis_root/prompt_sensitivity.csv" --model-slug "$slug" \
    2>&1 | tee "$model_log_dir/prompt_comparison.log"
  rc="${PIPESTATUS[0]}"
  return "$rc"
}

completed=0
failed=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug CURRENT_MODEL_ID local_path precision canonical default_run result_dir role cache_complete cache_status <<< "$record"
  model_log_dir="$LOG_ROOT/$slug"
  mkdir -p "$model_log_dir"
  result_abs="$PROJECT_ROOT/$result_dir"
  predictions="$result_abs/predictions.jsonl"
  analysis_dir="$PROJECT_ROOT/$REPORT_ROOT/models/$slug"
  rc=0

  echo
  echo "================================================================"
  echo "Model: $slug"
  echo "ID: $CURRENT_MODEL_ID"
  echo "Precision: $precision"
  echo "Role: $role"
  echo "Local snapshot: $local_path"
  echo "Cache: $cache_status"
  echo "================================================================"

  if [[ "$cache_complete" != "true" ]]; then
    echo "Skipping $slug: checkpoint is not complete locally; no download attempted."
    manifest_model_update "$slug" skipped_cache preflight "" 3 "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$slug" "$CURRENT_MODEL_ID" "$precision" skipped_cache 3 "$result_dir" "$model_log_dir" >> "$SUMMARY"
    failed=$((failed + 1))
    (( CONTINUE_ON_ERROR )) && continue || break
  fi

  need_clean=0; need_attack=0
  if [[ "$STAGE" == "all" || "$STAGE" == "clean" ]]; then
    output_complete "$predictions" 720 clean || need_clean=1
  fi
  if [[ "$STAGE" == "all" || "$STAGE" == "attack" ]]; then
    output_complete "$predictions" 720 "${MAIN_CONDITIONS[@]}" || need_attack=1
  fi

  run_model_secondary=0
  if (( INCLUDE_SECONDARY )) && [[ "$STAGE" == "all" ]] && [[ "$slug" == "qwen35_27b_bf16" || "$slug" == "qwen3vl_32b_bf16" ]]; then
    run_model_secondary=1
  elif (( INCLUDE_SECONDARY )) && [[ "$STAGE" != "analysis" ]]; then
    echo "Secondary style/size/P7 suite is reserved for canonical BF16 Qwen models; skipping it for $slug."
  fi

  if (( need_clean || need_attack || run_model_secondary )); then
    manifest_model_update "$slug" loading server "" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
    if ! start_server "$CURRENT_MODEL_ID" "$model_log_dir"; then
      rc=10
    else
      manifest_model_update "$slug" running server "$SERVER_PID" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
      echo "Health check passed for exact loaded model $CURRENT_MODEL_ID (PID $SERVER_PID)."
      vm_stat > "$model_log_dir/memory_after_load.txt" 2>/dev/null || true
    fi
  fi

  if (( rc == 0 && need_clean )); then
    manifest_model_update "$slug" running clean "$SERVER_PID" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
    run_inference "${RUN_ID}__${slug}__main_clean" main "$PROMPT" "$MANIFEST" "$result_abs" "$model_log_dir/clean.log" clean || rc=$?
  elif [[ "$STAGE" == "all" || "$STAGE" == "clean" ]]; then
    echo "Resume: clean output already complete for $slug"
  fi

  if (( rc == 0 && need_attack )); then
    manifest_model_update "$slug" running attack "$SERVER_PID" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
    run_inference "${RUN_ID}__${slug}__main_attack" main "$PROMPT" "$MANIFEST" "$result_abs" "$model_log_dir/attack.log" "${MAIN_CONDITIONS[@]}" || rc=$?
  elif [[ "$STAGE" == "all" || "$STAGE" == "attack" ]]; then
    echo "Resume: full main output already complete for $slug"
  fi

  if (( rc == 0 )) && output_complete "$predictions" 720 clean; then
    write_deployment_gate "$result_abs" 2>&1 | tee "$model_log_dir/deployment_gate.log" || rc=$?
  fi

  if (( rc == 0 && run_model_secondary )); then
    manifest_model_update "$slug" running secondary "$SERVER_PID" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
    run_secondary "$slug" "$model_log_dir" "$result_abs" || rc=$?
  fi

  if [[ -n "$SERVER_PID" ]]; then
    stop_server
    vm_stat > "$model_log_dir/memory_after_offload.txt" 2>/dev/null || true
    if ! port_is_free; then
      echo "Port $PORT remains occupied after stopping managed PID; refusing to continue." >&2
      (( rc == 0 )) && rc=11
    fi
  fi

  if (( rc == 0 )) && [[ "$STAGE" == "all" || "$STAGE" == "analysis" ]]; then
    if [[ -f "$predictions" ]]; then
      manifest_model_update "$slug" running analysis "" "" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
      "$PYTHON_BIN" -m src.v3_final_analysis analyze \
        --protocol "$PROTOCOL" --predictions "$predictions" --manifest "$MANIFEST" \
        --output-dir "$analysis_dir" --model-slug "$slug" \
        2>&1 | tee "$model_log_dir/analysis.log"
      rc="${PIPESTATUS[0]}"
    else
      echo "Cannot analyze $slug: $predictions does not exist." >&2
      rc=12
    fi
  fi

  if (( rc == 0 )); then
    status=completed
    completed=$((completed + 1))
  else
    status=failed
    failed=$((failed + 1))
  fi
  manifest_model_update "$slug" "$status" done "" "$rc" "$result_dir" "$CURRENT_MODEL_ID" "$precision" "$local_path"
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$slug" "$CURRENT_MODEL_ID" "$precision" "$status" "$rc" "$result_dir" "$model_log_dir" >> "$SUMMARY"
  if (( rc != 0 && ! CONTINUE_ON_ERROR )); then break; fi
done

if [[ "$STAGE" == "all" || "$STAGE" == "analysis" ]]; then
  "$PYTHON_BIN" -m src.v3_final_analysis aggregate --protocol "$PROTOCOL" --output-dir "$REPORT_ROOT" \
    2>&1 | tee "$LOG_ROOT/aggregate.log" || failed=$((failed + 1))
fi

final_status=completed
(( failed == 0 )) || final_status=completed_with_failures
finalize_manifest "$final_status"
trap - EXIT INT TERM

echo
echo "V3 final queue finished: completed=$completed failed_or_skipped=$failed"
echo "Run manifest: $RUN_MANIFEST"
echo "Summary: $SUMMARY"
echo "Paper-facing analysis: $PROJECT_ROOT/$REPORT_ROOT"
(( failed == 0 ))
