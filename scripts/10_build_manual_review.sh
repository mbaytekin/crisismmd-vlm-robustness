#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
[[ -f data/attacks/pilot_attack_manifest.csv ]] && python -m src.manual_review.build_gallery --split pilot
[[ -f data/attacks/test_attack_manifest.csv ]] && python -m src.manual_review.build_gallery --split test

