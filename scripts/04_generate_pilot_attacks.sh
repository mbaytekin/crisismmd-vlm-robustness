#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
python -m src.attack_generation.generator --split pilot
python -m src.attack_generation.validation --split pilot
python -m src.manual_review.build_gallery --split pilot

