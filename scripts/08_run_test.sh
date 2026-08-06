#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
PROMPT_CONFIG="configs/prompts/frozen_prompt.yaml"
if [[ "${1:-}" == "--prompt-config" ]]; then PROMPT_CONFIG="$2"; shift 2; fi
if [[ ! -f data/attacks_fixed/test_attack_manifest.csv ]]; then
  echo "Missing corrected test manifest. Run scripts/07_generate_test_attacks.sh first." >&2
  exit 2
fi
python -m src.inference.runner --split test --prompt-config "$PROMPT_CONFIG" --output results/baseline_revision/test_predictions.jsonl --cache results/baseline_revision/test_inference_cache.sqlite --attack-manifest data/attacks_fixed/test_attack_manifest.csv
