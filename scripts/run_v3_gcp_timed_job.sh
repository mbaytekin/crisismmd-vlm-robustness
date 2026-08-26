#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL=""
STAGE=""
KIND="both"
COHORT="both"
PORT="${V3_GCP_PORT:-8000}"
SHUTDOWN_ON_EXIT="${V3_SHUTDOWN_ON_EXIT:-0}"

usage() {
  cat <<'EOF'
Usage: scripts/run_v3_gcp_timed_job.sh --model NAME --stage STAGE [options]

Options:
  --model NAME     Model alias accepted by run_v3_gcp_a100.sh.
  --stage STAGE    main, ablation, clean, or all.
  --kind KIND      style, size, or both (default: both).
  --cohort NAME    natural, official, or both (default: both).
  --port PORT      Managed vLLM port (default: 8000).
  -h, --help       Show this help.

Set V3_SHUTDOWN_ON_EXIT=1 to stop the VM after the job finishes or fails.
EOF
}

while (( $# )); do
  case "$1" in
    --model) [[ $# -ge 2 ]] || { echo "--model requires a value" >&2; exit 2; }; MODEL="$2"; shift 2 ;;
    --stage) [[ $# -ge 2 ]] || { echo "--stage requires a value" >&2; exit 2; }; STAGE="$2"; shift 2 ;;
    --kind) [[ $# -ge 2 ]] || { echo "--kind requires a value" >&2; exit 2; }; KIND="$2"; shift 2 ;;
    --cohort) [[ $# -ge 2 ]] || { echo "--cohort requires a value" >&2; exit 2; }; COHORT="$2"; shift 2 ;;
    --port) [[ $# -ge 2 ]] || { echo "--port requires a value" >&2; exit 2; }; PORT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$MODEL" ]] || { echo "--model is required" >&2; exit 2; }
case "$STAGE" in main|ablation|clean|all) ;; *) echo "Invalid --stage: $STAGE" >&2; exit 2 ;; esac
case "$KIND" in style|size|both) ;; *) echo "Invalid --kind: $KIND" >&2; exit 2 ;; esac
case "$COHORT" in natural|official|both) ;; *) echo "Invalid --cohort: $COHORT" >&2; exit 2 ;; esac
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT > 0 && PORT < 65536 )) || { echo "Invalid port: $PORT" >&2; exit 2; }

JOB_STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
JOB_DIR="logs/v3/gcp_a100/timed_jobs/${JOB_STAMP}__${MODEL}__${STAGE}"
TIMING_PATH="$JOB_DIR/timing.json"
mkdir -p "$JOB_DIR"

START_EPOCH="$(date -u +%s)"
START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
FINALIZED=0

write_timing() {
  local rc="$1"
  (( FINALIZED == 0 )) || return 0
  FINALIZED=1
  local end_epoch end_utc duration
  end_epoch="$(date -u +%s)"
  end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  duration=$((end_epoch - START_EPOCH))
  "$HOME/venvs/crisismmd-py312/bin/python" - \
    "$TIMING_PATH" "$MODEL" "$STAGE" "$KIND" "$COHORT" "$PORT" \
    "$START_UTC" "$end_utc" "$START_EPOCH" "$end_epoch" "$duration" "$rc" <<'PY'
import json
import platform
import sys

(
    output, model, stage, kind, cohort, port, start_utc, end_utc,
    start_epoch, end_epoch, duration, return_code,
) = sys.argv[1:]
payload = {
    "schema_version": 1,
    "model": model,
    "stage": stage,
    "kind": kind,
    "cohort": cohort,
    "port": int(port),
    "hostname": platform.node(),
    "start_utc": start_utc,
    "end_utc": end_utc,
    "start_epoch": int(start_epoch),
    "end_epoch": int(end_epoch),
    "duration_seconds": int(duration),
    "return_code": int(return_code),
}
with open(output, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2)
    handle.write("\n")
PY
  echo "Timing record: $TIMING_PATH"
  echo "End-to-end duration: ${duration}s; return_code=$rc"
}

finish() {
  local rc="$1"
  write_timing "$rc"
  if [[ "$SHUTDOWN_ON_EXIT" == "1" ]]; then
    echo "Stopping VM after timed job completion."
    sudo shutdown -h now || true
  fi
}
trap 'rc=$?; finish "$rc"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "Timed GCP job"
echo "  model: $MODEL"
echo "  stage: $STAGE"
echo "  kind: $KIND"
echo "  cohort: $COHORT"
echo "  start: $START_UTC"
echo "  timing: $TIMING_PATH"

scripts/run_v3_gcp_a100.sh \
  --model "$MODEL" \
  --stage "$STAGE" \
  --kind "$KIND" \
  --cohort "$COHORT" \
  --port "$PORT"
