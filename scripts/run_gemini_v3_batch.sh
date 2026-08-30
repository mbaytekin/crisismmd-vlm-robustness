#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${V3_PYTHON:-$PROJECT_ROOT/.venv-mac/bin/python}"
ENV_FILE="${GEMINI_ENV_FILE:-$PROJECT_ROOT/.env}"
MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
SPLIT="pilot"
SHARD_SIZE="${GEMINI_BATCH_SHARD_SIZE:-500}"
MAX_OUTPUT_TOKENS="${GEMINI_MAX_OUTPUT_TOKENS:-512}"
THINKING_BUDGET="${GEMINI_THINKING_BUDGET:-0}"
RUN_TAG="${GEMINI_RUN_TAG:-}"
ACTION="submit"
FORCE=0
LIMIT=""

export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

usage() {
  cat <<'EOF'
Usage: scripts/run_gemini_v3_batch.sh [options]

Default action is prepare + submit for the 90-sample V3 pilot (900 requests).
Batch jobs are asynchronous; use --action status and --action download later.

Options:
  --split NAME       pilot, main, style_ablation, size_ablation,
                     natural_clean_all, official_test,
                     text_rhetoric_ablation, or size_response_pt
                     (default: pilot)
  --model NAME       Gemini model (default: gemini-2.5-flash)
  --shard-size N     Requests per input JSONL shard (default: 500)
  --max-output-tokens N
                     Output ceiling (default: 512; minimum: 256).
  --thinking-budget N
                     Gemini 2.5 thinking budget (default: 0/off).
  --run-tag NAME     Isolate this attempt under a new result directory.
  --limit N          Prepare only N records (smoke testing only).
  --action ACTION    prepare, submit, status, download, or all (default: submit)
  --env-file PATH    Secret env file (default: .env)
  --force            Re-submit already recorded shards (use only deliberately)
  -h, --help         Show this help.

The API key is read locally from GEMINI_API_KEY. Never put it in git or chat.
EOF
}

while (( $# )); do
  case "$1" in
    --split) SPLIT="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --shard-size) SHARD_SIZE="$2"; shift 2 ;;
    --max-output-tokens) MAX_OUTPUT_TOKENS="$2"; shift 2 ;;
    --thinking-budget) THINKING_BUDGET="$2"; shift 2 ;;
    --run-tag) RUN_TAG="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --action) ACTION="$2"; shift 2 ;;
    --env-file) ENV_FILE="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -x "$PYTHON_BIN" ]] || { echo "Python environment not found: $PYTHON_BIN" >&2; exit 1; }
if [[ "$ACTION" != "prepare" ]]; then
  [[ -f "$ENV_FILE" ]] || {
    echo "Missing env file: $ENV_FILE" >&2
    echo "Create it with: cp .env.example .env" >&2
    exit 2
  }

  if ! grep -Eq '^GEMINI_API_KEY=[^[:space:]]' "$ENV_FILE"; then
    echo "GEMINI_API_KEY is empty in $ENV_FILE" >&2
    echo "Add it locally, then rerun this command. The key is never printed." >&2
    exit 2
  fi
fi

RESULT_ROOT="$PROJECT_ROOT/results/v3/gemini_batch/$MODEL"
[[ -n "$RUN_TAG" ]] && RESULT_ROOT="$RESULT_ROOT/$RUN_TAG"
INPUT_DIR="$RESULT_ROOT/$SPLIT/input"

prepare_args=(
  prepare --split "$SPLIT" --model "$MODEL" --shard-size "$SHARD_SIZE"
  --max-output-tokens "$MAX_OUTPUT_TOKENS" --thinking-budget "$THINKING_BUDGET"
  --output-dir "${INPUT_DIR%/input}"
)
[[ -n "$LIMIT" ]] && prepare_args+=(--limit "$LIMIT")

run_batch() {
  "$PYTHON_BIN" scripts/gemini_v3_batch.py "$@" \
    --input-dir "$INPUT_DIR" --env-file "$ENV_FILE"
}

case "$ACTION" in
  prepare)
    "$PYTHON_BIN" scripts/gemini_v3_batch.py "${prepare_args[@]}"
    ;;
  submit)
    if [[ ! -f "$INPUT_DIR/../batch_spec.json" ]]; then
      "$PYTHON_BIN" scripts/gemini_v3_batch.py "${prepare_args[@]}"
    fi
    submit_args=(submit)
    (( FORCE )) && submit_args+=(--force)
    run_batch "${submit_args[@]}"
    ;;
  status)
    run_batch status
    ;;
  download)
    run_batch download
    ;;
  all)
    "$PYTHON_BIN" scripts/gemini_v3_batch.py "${prepare_args[@]}"
    submit_args=(submit)
    (( FORCE )) && submit_args+=(--force)
    run_batch "${submit_args[@]}"
    echo
    echo "Batch submitted. Check later with:"
    follow_up=("$0" --split "$SPLIT" --model "$MODEL")
    [[ -n "$RUN_TAG" ]] && follow_up+=(--run-tag "$RUN_TAG")
    printf "  %q" "${follow_up[@]}" --action status
    printf "\n"
    printf "  %q" "${follow_up[@]}" --action download
    printf "\n"
    ;;
  *)
    echo "Invalid --action: $ACTION" >&2
    usage >&2
    exit 2
    ;;
esac
