#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${V3_PYTHON:-.venv-mac/bin/python}"
PROMPT_CONFIG="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
RUN_ATTACKS="${V3_RUN_ATTACKS:-0}"
SERVER_PORT_EXPLICIT="${V3_MLX_PORT+x}"
SERVER_PORT="${V3_MLX_PORT:-8090}"
START_TIMEOUT="${V3_SERVER_START_TIMEOUT:-3600}"
STOP_EXISTING_MLX="${V3_STOP_EXISTING_MLX:-1}"
RUN_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG_DIR="$PROJECT_ROOT/logs/v3/mac_model_runs/$RUN_STAMP"
SUMMARY_PATH="$LOG_DIR/summary.tsv"

cd "$PROJECT_ROOT"

usage() {
  cat <<'EOF'
Usage:
  scripts/run_all_v3_mac_models.sh [MODEL_SLUG ...]
  scripts/run_all_v3_mac_models.sh --list

With no model slugs, every complete V3 Mac checkpoint in the local Hugging
Face cache is screened on the 180-sample prompt-validation set with the frozen
V4 prompt. Missing or partial checkpoints are never downloaded.

Environment variables:
  V3_PROMPT_CONFIG         Prompt file (default: frozen_prompt_v4.yaml)
  V3_CONCURRENCY           Inference concurrency (default: 1)
  V3_RUN_ATTACKS           Run attacks after both clean gates pass (default: 0)
  V3_MLX_PORT              Managed server port (default: first free port >= 8090)
  V3_SERVER_START_TIMEOUT  Model load timeout in seconds (default: 3600)
  V3_STOP_EXISTING_MLX     Stop stale user-owned MLX servers at startup (default: 1)
EOF
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN." >&2
  echo "Run scripts/setup_macos.sh first, or set V3_PYTHON." >&2
  exit 1
fi

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This runner requires native Apple Silicon macOS." >&2
  exit 1
fi

if [[ ! "$SERVER_PORT" =~ ^[0-9]+$ ]] || (( SERVER_PORT < 1 || SERVER_PORT > 65535 )); then
  echo "V3_MLX_PORT must be a valid TCP port." >&2
  exit 2
fi

if [[ ! "$START_TIMEOUT" =~ ^[0-9]+$ ]] || (( START_TIMEOUT < 1 )); then
  echo "V3_SERVER_START_TIMEOUT must be a positive integer." >&2
  exit 2
fi

if [[ "$STOP_EXISTING_MLX" != "0" && "$STOP_EXISTING_MLX" != "1" ]]; then
  echo "V3_STOP_EXISTING_MLX must be 0 or 1." >&2
  exit 2
fi

cache_inventory() {
  "$PYTHON_BIN" - "$@" <<'PY'
import sys
from pathlib import Path

from src.model_registry import registry

requested = sys.argv[1:]
models = registry()["models"]
by_slug = {model["slug"]: model for model in models}
unknown = sorted(set(requested) - set(by_slug))
if unknown:
    raise SystemExit(f"Unknown model slug(s): {', '.join(unknown)}")

cache_root = Path.home() / ".cache" / "huggingface" / "hub"
selected = [by_slug[slug] for slug in requested] if requested else models
for model in selected:
    model_id = model["mac_model_id"]
    cache_dir = cache_root / ("models--" + model_id.replace("/", "--"))
    snapshots_dir = cache_dir / "snapshots"
    snapshots = [path for path in snapshots_dir.iterdir() if path.is_dir()] if snapshots_dir.is_dir() else []
    incomplete = list(cache_dir.rglob("*.incomplete")) if cache_dir.exists() else []
    complete = bool(snapshots) and not incomplete
    size_bytes = 0
    blobs_dir = cache_dir / "blobs"
    if blobs_dir.is_dir():
        try:
            size_bytes = sum(path.stat().st_size for path in blobs_dir.rglob("*") if path.is_file())
        except OSError:
            pass
    fields = (
        model["slug"],
        model_id,
        "1" if model.get("gated", False) else "0",
        "complete" if complete else "missing_or_partial",
        f"{size_bytes / 1024**3:.1f}",
    )
    print("\t".join(fields))
PY
}

if [[ "${1:-}" == "--list" ]]; then
  printf "%-29s %-9s %-19s %9s  %s\n" "SLUG" "GATED" "CACHE" "SIZE_GIB" "MODEL_ID"
  while IFS=$'\t' read -r slug model_id gated cache_status size_gib; do
    [[ -n "$slug" ]] || continue
    gated_text="no"
    [[ "$gated" == "1" ]] && gated_text="yes"
    printf "%-29s %-9s %-19s %9s  %s\n" "$slug" "$gated_text" "$cache_status" "$size_gib" "$model_id"
  done < <(cache_inventory)
  exit 0
fi

if ! "$PYTHON_BIN" scripts/freeze_v3_artifacts.py check --prompt-config "$PROMPT_CONFIG"; then
  echo "The selected prompt or dataset inputs do not match reports/v3/artifact_lock.json." >&2
  echo "Review the changes before creating a new research run." >&2
  exit 1
fi

if command -v lsof >/dev/null 2>&1; then
  if [[ -n "$SERVER_PORT_EXPLICIT" ]] && lsof -nP -iTCP:"$SERVER_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Requested port $SERVER_PORT is already in use. Set V3_MLX_PORT to a free port." >&2
    exit 1
  fi
  if [[ -z "$SERVER_PORT_EXPLICIT" ]]; then
    while lsof -nP -iTCP:"$SERVER_PORT" -sTCP:LISTEN >/dev/null 2>&1; do
      SERVER_PORT=$((SERVER_PORT + 1))
      if (( SERVER_PORT > 8190 )); then
        echo "Could not find a free MLX server port between 8090 and 8190." >&2
        exit 1
      fi
    done
  fi
fi

stop_process_list() {
  local label="$1"
  shift
  local pids=("$@")
  (( ${#pids[@]} > 0 )) || return 0

  echo "Stopping $label process(es): ${pids[*]}"
  kill -TERM "${pids[@]}" 2>/dev/null || true
  local alive=()
  local pid
  local process_state
  for _ in {1..60}; do
    alive=()
    for pid in "${pids[@]}"; do
      if kill -0 "$pid" 2>/dev/null; then
        process_state="$(ps -o stat= -p "$pid" 2>/dev/null || true)"
        [[ "$process_state" == Z* ]] || alive+=("$pid")
      fi
    done
    (( ${#alive[@]} == 0 )) && return 0
    sleep 1
  done

  echo "$label did not stop within 60 seconds; sending SIGKILL." >&2
  kill -KILL "${alive[@]}" 2>/dev/null || true
}

existing_mlx=()
while IFS= read -r pid; do
  [[ -n "$pid" ]] && existing_mlx+=("$pid")
done < <(pgrep -u "$(id -u)" -f 'python.*-m mlx_vlm\.server' 2>/dev/null || true)
if (( ${#existing_mlx[@]} > 0 )); then
  if [[ "$STOP_EXISTING_MLX" == "1" ]]; then
    stop_process_list "stale MLX server" "${existing_mlx[@]}"
    echo "Previous MLX models were offloaded from unified memory."
  else
    echo "Existing mlx_vlm server process(es) detected: ${existing_mlx[*]}" >&2
    echo "Stop them first or set V3_STOP_EXISTING_MLX=1." >&2
    exit 1
  fi
fi

mkdir -p "$LOG_DIR"
printf "slug\tmodel_id\tgated\tcache_gib\tstatus\texit_code\tserver_log\trun_log\n" > "$SUMMARY_PATH"
echo "Managed MLX server port: $SERVER_PORT"

MODEL_RECORDS=()
while IFS= read -r record; do
  [[ -n "$record" ]] && MODEL_RECORDS+=("$record")
done < <(cache_inventory "$@")

selected_count=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug model_id gated cache_status size_gib <<< "$record"
  if [[ "$cache_status" == "complete" ]]; then
    selected_count=$((selected_count + 1))
  else
    echo "Skipping $slug: local checkpoint is missing or partial ($model_id)."
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$slug" "$model_id" "$gated" "$size_gib" "skipped_cache" "-" "-" "-" >> "$SUMMARY_PATH"
  fi
done

if (( selected_count == 0 )); then
  echo "No complete local checkpoints were selected." >&2
  echo "Inspect the registry and cache with: scripts/run_all_v3_mac_models.sh --list" >&2
  exit 3
fi

SERVER_PID=""
stop_server() {
  if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Stopping managed MLX server (PID $SERVER_PID)..."
    stop_process_list "managed MLX server" "$SERVER_PID"
    wait "$SERVER_PID" 2>/dev/null || true
    echo "Model offloaded from unified memory; its checkpoint remains in the disk cache."
  fi
  SERVER_PID=""
}
trap stop_server EXIT
trap 'stop_server; exit 130' INT TERM

wait_for_server() {
  local model_id="$1"
  local log_path="$2"
  local deadline=$((SECONDS + START_TIMEOUT))
  while (( SECONDS < deadline )); do
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
      echo "MLX server exited while loading $model_id." >&2
      tail -n 80 "$log_path" >&2 || true
      return 1
    fi
    if "$PYTHON_BIN" - "$model_id" "$SERVER_PORT" >/dev/null 2>&1 <<'PY'
import json
import sys
import urllib.request

expected, port = sys.argv[1], sys.argv[2]
with urllib.request.urlopen(f"http://127.0.0.1:{port}/v1/models", timeout=3) as response:
    payload = json.load(response)
served = [item.get("id") for item in payload.get("data", [])]
if expected not in served:
    raise SystemExit(f"Expected {expected!r}, served {served!r}")
PY
    then
      return 0
    fi
    sleep 5
  done
  echo "Timed out after ${START_TIMEOUT}s while loading $model_id." >&2
  tail -n 80 "$log_path" >&2 || true
  return 1
}

completed=0
failed=0
current=0
for record in "${MODEL_RECORDS[@]}"; do
  IFS=$'\t' read -r slug model_id gated cache_status size_gib <<< "$record"
  [[ "$cache_status" == "complete" ]] || continue
  current=$((current + 1))
  server_log="$LOG_DIR/${slug}_server.log"
  run_log="$LOG_DIR/${slug}_run.log"

  echo
  echo "[$current/$selected_count] $slug"
  echo "Model: $model_id"
  echo "Cache: ${size_gib} GiB"
  echo "Prompt: $PROMPT_CONFIG"

  if ! "$PYTHON_BIN" -m src.model_registry lock --slug "$slug" --platform mac > "$LOG_DIR/${slug}_lock.json"; then
    echo "Could not create the immutable model lock for $slug; continuing." >&2
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$slug" "$model_id" "$gated" "$size_gib" "lock_failed" "1" "$server_log" "$run_log" >> "$SUMMARY_PATH"
    failed=$((failed + 1))
    continue
  fi

  echo "Loading the model. Server output: $server_log"
  V3_MODEL_ID="$model_id" V3_MLX_PORT="$SERVER_PORT" scripts/start_v3_mlx.sh > "$server_log" 2>&1 &
  SERVER_PID=$!

  if ! wait_for_server "$model_id" "$server_log"; then
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
      "$slug" "$model_id" "$gated" "$size_gib" "server_failed" "1" "$server_log" "$run_log" >> "$SUMMARY_PATH"
    failed=$((failed + 1))
    stop_server
    continue
  fi

  echo "Server is ready on http://127.0.0.1:$SERVER_PORT/v1"
  VLM_BASE_URL="http://127.0.0.1:$SERVER_PORT/v1" \
  V3_PYTHON="$PYTHON_BIN" \
  V3_CONCURRENCY="$CONCURRENCY" \
  V3_PROMPT_CONFIG="$PROMPT_CONFIG" \
  V3_RUN_ATTACKS="$RUN_ATTACKS" \
    scripts/run_v3_model.sh "$slug" 2>&1 | tee "$run_log"
  run_status=${PIPESTATUS[0]}

  status="completed"
  if (( run_status != 0 )); then
    status="failed_or_gate_rejected"
    failed=$((failed + 1))
    echo "$slug stopped with exit code $run_status. The next model will still run." >&2
  else
    completed=$((completed + 1))
  fi
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$slug" "$model_id" "$gated" "$size_gib" "$status" "$run_status" "$server_log" "$run_log" >> "$SUMMARY_PATH"
  stop_server
  sleep 5
done

echo
echo "Mac model queue finished: completed=$completed failed_or_rejected=$failed"
echo "Summary: $SUMMARY_PATH"
echo "Clean-gate reports: $PROJECT_ROOT/reports/v3/clean_gates"

(( failed == 0 ))
