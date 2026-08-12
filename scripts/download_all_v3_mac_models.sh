#!/usr/bin/env bash
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${V3_PYTHON:-.venv-mac/bin/python}"
DOWNLOAD_ONE="scripts/download_v3_mac_model_if_missing.sh"
INCLUDE_GATED="${INCLUDE_GATED:-0}"

if [[ "$INCLUDE_GATED" != "0" && "$INCLUDE_GATED" != "1" ]]; then
  echo "INCLUDE_GATED must be 0 or 1." >&2
  exit 2
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN." >&2
  echo "Run scripts/setup_docker_mac.sh first, or set V3_PYTHON." >&2
  exit 1
fi

mapfile_compat() {
  while IFS= read -r line; do
    MODEL_RECORDS+=("$line")
  done
}

MODEL_RECORDS=()
mapfile_compat < <("$PYTHON_BIN" - <<'PY'
from src.model_registry import registry

for model in registry()["models"]:
    print(f"{model['slug']}|{int(bool(model.get('gated', False)))}")
PY
)

failed=()
skipped=()
for index in "${!MODEL_RECORDS[@]}"; do
  record="${MODEL_RECORDS[$index]}"
  slug="${record%%|*}"
  gated="${record##*|}"
  echo
  echo "[$((index + 1))/${#MODEL_RECORDS[@]}] Checking $slug"
  if [[ "$gated" == "1" && "$INCLUDE_GATED" != "1" ]]; then
    skipped+=("$slug")
    echo "Skipping gated model (set INCLUDE_GATED=1 after Hugging Face login)."
    continue
  fi
  if ! "$DOWNLOAD_ONE" "$slug" mac; then
    failed+=("$slug")
    echo "Download failed for $slug; continuing with the next model." >&2
  fi
done

echo
scripts/check_v3_mac_model_cache.sh mac

if (( ${#failed[@]} > 0 )); then
  echo "Failed models: ${failed[*]}" >&2
  echo "Rerun the script to resume incomplete downloads." >&2
  exit 1
fi

if (( ${#skipped[@]} > 0 )); then
  echo "Skipped gated models: ${skipped[*]}"
fi
echo "All selected V3 Mac models are present in the Hugging Face cache."
