#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
[[ -f results/pilot_predictions.jsonl ]] && python -m src.evaluation.evaluate --split pilot
[[ -f results/test_predictions.jsonl ]] && python -m src.evaluation.evaluate --split test
[[ -f results/test_predictions.jsonl ]] && python -m src.evaluation.error_analysis --split test

