#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
RUN_TAG="${GEMINI_RUN_TAG:-thinking0-json-v2}"
INTERVAL_SECONDS="${GEMINI_WATCH_INTERVAL_SECONDS:-1800}"
ONCE=0

SPLITS=(pilot main style_ablation size_ablation natural_clean_all official_test)
DOWNLOADED_SPLITS=""

expected_records() {
  case "$1" in
    pilot) echo 900 ;;
    main) echo 7200 ;;
    style_ablation) echo 1200 ;;
    size_ablation) echo 600 ;;
    natural_clean_all) echo 3474 ;;
    official_test) echo 529 ;;
    *) return 1 ;;
  esac
}

usage() {
  cat <<'EOF'
Usage: scripts/watch_gemini_v3_batch.sh [options]

Checks the corrected Gemini Batch queue immediately and every 30 minutes by default.
Completed splits are downloaded and verified. The script exits 0 only after all
six splits are downloaded with every record parsed successfully.

Options:
  --model NAME          Gemini model (default: gemini-2.5-flash)
  --run-tag NAME        Batch run tag (default: thinking0-json-v2)
  --interval-seconds N  Poll interval (default: 1800)
  --once                Check/download once and exit (useful for testing)
  -h, --help            Show this help.
EOF
}

while (( $# )); do
  case "$1" in
    --model) MODEL="$2"; shift 2 ;;
    --run-tag) RUN_TAG="$2"; shift 2 ;;
    --interval-seconds) INTERVAL_SECONDS="$2"; shift 2 ;;
    --once) ONCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$INTERVAL_SECONDS" =~ ^[0-9]+$ ]] && (( INTERVAL_SECONDS > 0 )) || {
  echo "--interval-seconds must be a positive integer" >&2
  exit 2
}

timestamp() {
  date -u '+%Y-%m-%dT%H:%M:%SZ'
}

verify_output() {
  local split="$1"
  local predictions="$PROJECT_ROOT/results/v3/gemini_batch/$MODEL/$RUN_TAG/$split/predictions.jsonl"
  local expected
  expected="$(expected_records "$split")" || return 1
  [[ -f "$predictions" ]] || {
    echo "[$split] missing predictions file after download: $predictions" >&2
    return 1
  }
  "$PROJECT_ROOT/.venv-mac/bin/python" - "$predictions" "$expected" <<'PY'
import json
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1])
expected = int(sys.argv[2])
rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
counts = Counter(row.get("parse_status") for row in rows)
if len(rows) != expected or counts.get("parsed", 0) != expected:
    print({"records": len(rows), "expected": expected, "parse_status": dict(counts)}, file=sys.stderr)
    raise SystemExit(1)
print({"records": len(rows), "parsed": counts["parsed"]})
PY
}

status_split() {
  local split="$1"
  local output rc
  output="$(scripts/run_gemini_v3_batch.sh \
    --split "$split" --model "$MODEL" --run-tag "$RUN_TAG" --action status 2>&1)"
  rc=$?
  printf '%s\n' "$output"

  if (( rc != 0 )); then
    if [[ "$output" == *"Missing jobs manifest"* ]]; then
      echo "[$split] not submitted yet"
      return 1
    fi
    echo "[$split] status check failed" >&2
    return 2
  fi
  if [[ "$output" == *'"JOB_STATE_FAILED"'* ||
        "$output" == *'"JOB_STATE_CANCELLED"'* ||
        "$output" == *'"JOB_STATE_EXPIRED"'* ]]; then
    echo "[$split] terminal Batch failure detected; no automatic resubmission" >&2
    return 2
  fi
  if [[ "$output" == *'"JOB_STATE_RUNNING"'* ||
        "$output" == *'"JOB_STATE_PENDING"'* ]]; then
    return 1
  fi
  if [[ "$output" == *'"JOB_STATE_SUCCEEDED"'* ]]; then
    return 0
  fi
  echo "[$split] no completed/running state found" >&2
  return 1
}

check_and_download() {
  local completed=0
  local split rc
  for split in "${SPLITS[@]}"; do
    echo
    echo "[$(timestamp)] Checking $split"
    if status_split "$split"; then
      if [[ " $DOWNLOADED_SPLITS " == *" $split "* ]]; then
        echo "[$split] already downloaded in this watcher session"
      elif verify_output "$split" >/dev/null 2>&1; then
        DOWNLOADED_SPLITS="$DOWNLOADED_SPLITS $split"
        echo "[$split] existing output verified; no re-download needed"
      else
        echo "[$split] all shards succeeded; downloading"
        if scripts/run_gemini_v3_batch.sh \
          --split "$split" --model "$MODEL" --run-tag "$RUN_TAG" --action download; then
          if verify_output "$split"; then
            DOWNLOADED_SPLITS="$DOWNLOADED_SPLITS $split"
            echo "[$split] download and parse verification passed"
          else
            echo "[$split] verification failed" >&2
            return 2
          fi
        else
          echo "[$split] download failed" >&2
          return 2
        fi
      fi
      completed=$((completed + 1))
    else
      rc=$?
      (( rc == 2 )) && return 2
    fi
  done

  if (( completed == ${#SPLITS[@]} )); then
    echo
    echo "[$(timestamp)] All Gemini V3 splits downloaded and verified. Watcher finished."
    return 0
  fi
  return 1
}

echo "Gemini V3 Batch watcher"
echo "  model: $MODEL"
echo "  run tag: $RUN_TAG"
echo "  interval: ${INTERVAL_SECONDS}s"

while true; do
  check_and_download
  rc=$?
  (( rc == 0 )) && exit 0
  (( rc == 2 )) && exit 1
  if (( ONCE )); then
    echo "Watcher one-shot check finished; incomplete splits remain."
    exit 3
  fi
  echo
  echo "[$(timestamp)] Results are not all ready; next check in ${INTERVAL_SECONDS}s."
  sleep "$INTERVAL_SECONDS"
done
