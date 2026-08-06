#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
python -m src.attack_generation.generator --split test --output-root data/attacks_fixed/test --manifest data/attacks_fixed/test_attack_manifest.csv
python -m src.attack_generation.validation --split test --manifest data/attacks_fixed/test_attack_manifest.csv
