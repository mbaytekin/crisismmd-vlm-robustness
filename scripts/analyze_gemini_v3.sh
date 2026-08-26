#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${V3_PYTHON:-$PROJECT_ROOT/.venv-mac/bin/python}"
MODEL_SLUG="${GEMINI_MODEL_SLUG:-gemini_2_5_flash}"
RUN_TAG="${GEMINI_RUN_TAG:-thinking0-json-v2}"
RESULT_ROOT="${GEMINI_RESULT_ROOT:-results/v3/gemini_batch/gemini-2.5-flash/$RUN_TAG}"
REPORT_ROOT="${GEMINI_REPORT_ROOT:-reports/v3/final_analysis/models/$MODEL_SLUG}"

[[ -x "$PYTHON_BIN" ]] || { echo "Python environment not found: $PYTHON_BIN" >&2; exit 1; }

run_analysis() {
  local label="$1"
  shift
  echo
  echo "================================================================"
  echo "Gemini analysis: $label"
  echo "================================================================"
  "$PYTHON_BIN" -m src.v3_final_analysis "$@"
}

run_analysis main analyze \
  --predictions "$RESULT_ROOT/main/predictions.jsonl" \
  --manifest data/v3/manifests/all_conditions.csv \
  --output-dir "$REPORT_ROOT" \
  --model-slug "$MODEL_SLUG"

run_analysis style analyze-ablation \
  --predictions "$RESULT_ROOT/style_ablation/predictions.jsonl" \
  --manifest data/v3/manifests/style_ablation_conditions.csv \
  --output-dir "$REPORT_ROOT/secondary/style" \
  --model-slug "$MODEL_SLUG" \
  --kind style

run_analysis size analyze-ablation \
  --predictions "$RESULT_ROOT/size_ablation/predictions.jsonl" \
  --manifest data/v3/manifests/size_ablation_conditions.csv \
  --output-dir "$REPORT_ROOT/secondary/size" \
  --model-slug "$MODEL_SLUG" \
  --kind size

run_analysis natural-clean analyze-clean \
  --predictions "$RESULT_ROOT/natural_clean_all/predictions.jsonl" \
  --manifest data/v3/manifests/natural_clean_all.csv \
  --output-dir "reports/v3/clean_benchmarks/$MODEL_SLUG/natural_clean_all" \
  --model-slug "$MODEL_SLUG" \
  --cohort natural_clean_all

run_analysis official-test analyze-clean \
  --predictions "$RESULT_ROOT/official_test/predictions.jsonl" \
  --manifest data/v3/manifests/official_test_clean.csv \
  --output-dir "reports/v3/clean_benchmarks/$MODEL_SLUG/official_test" \
  --model-slug "$MODEL_SLUG" \
  --cohort official_test

# The V3 pilot is historical/exploratory and is intentionally kept outside the
# canonical model report directory.
run_analysis exploratory-pilot analyze \
  --predictions "$RESULT_ROOT/pilot/predictions.jsonl" \
  --manifest data/v3/manifests/all_conditions.csv \
  --output-dir "reports/v3/exploratory/gemini/$MODEL_SLUG/pilot" \
  --model-slug "$MODEL_SLUG"

echo
echo "Gemini V3 analysis complete."
echo "  Main and ablations: $REPORT_ROOT"
echo "  Clean benchmarks:   reports/v3/clean_benchmarks/$MODEL_SLUG"
echo "  Exploratory pilot:  reports/v3/exploratory/gemini/$MODEL_SLUG/pilot"
