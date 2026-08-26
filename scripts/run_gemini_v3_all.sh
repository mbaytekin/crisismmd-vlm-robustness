#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
RUN_TAG="${GEMINI_RUN_TAG:-thinking0-json-v2}"
ACTION="${1:-all}"
SPLITS=(pilot main style_ablation size_ablation natural_clean_all official_test)

case "$ACTION" in
  prepare|submit|all|status|download) ;;
  *)
    echo "Usage: scripts/run_gemini_v3_all.sh [prepare|submit|all|status|download]" >&2
    exit 2
    ;;
esac

for split in "${SPLITS[@]}"; do
  echo
  echo "[$split] action=$ACTION model=$MODEL run_tag=$RUN_TAG"
  scripts/run_gemini_v3_batch.sh \
    --split "$split" \
    --model "$MODEL" \
    --run-tag "$RUN_TAG" \
    --action "$ACTION"
done
