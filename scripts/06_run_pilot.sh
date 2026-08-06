#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
python -m src.inference.runner --split pilot
python -m src.evaluation.evaluate --split pilot
python -m src.evaluation.error_analysis --split pilot

