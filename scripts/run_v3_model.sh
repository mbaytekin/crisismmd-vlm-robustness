#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 MODEL_SLUG" >&2
  exit 2
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_SLUG="$1"
PYTHON_BIN="${V3_PYTHON:-python}"
CONCURRENCY="${V3_CONCURRENCY:-1}"
RUN_ATTACKS="${V3_RUN_ATTACKS:-0}"
PROMPT_CONFIG="${V3_PROMPT_CONFIG:-configs/prompts/frozen_prompt_v4.yaml}"
SCREEN_SPLIT="prompt_validation"
SCREEN_PHASE="prompt_validation"
SCREEN_MANIFEST="data/v3/manifests/prompt_validation_clean.csv"
CONDITION_MANIFEST="data/v3/manifests/all_conditions.csv"
cd "$PROJECT_ROOT"

EXPECTED_MODEL_ID="$("$PYTHON_BIN" - "$MODEL_SLUG" <<'PY'
import sys
from src.model_registry import registry
models={model["slug"]:model for model in registry()["models"]}
if sys.argv[1] not in models:
    raise SystemExit(f"Unknown model slug: {sys.argv[1]}")
print(models[sys.argv[1]]["mac_model_id"])
PY
)"
export V3_EXPECTED_MODEL_ID="$EXPECTED_MODEL_ID"
echo "Verified runner target: $MODEL_SLUG -> $V3_EXPECTED_MODEL_ID"
echo "Verified runner prompt: $PROMPT_CONFIG"
echo "Verified clean screen: $SCREEN_SPLIT (180 samples; 60 per class)"

MAIN_CONDITIONS=(clean benign_image benign_text benign_joint direct_image direct_text direct_joint misleading_image misleading_text misleading_joint)
STYLE_CONDITIONS=(clean benign_simple benign_news benign_camouflage direct_simple direct_news direct_camouflage misleading_simple misleading_news misleading_camouflage)
SIZE_CONDITIONS=(clean benign_small benign_medium benign_large direct_small direct_medium direct_large misleading_small misleading_medium misleading_large)

"$PYTHON_BIN" -m src.v3_pipeline validate
"$PYTHON_BIN" scripts/freeze_v3_artifacts.py check --prompt-config "$PROMPT_CONFIG"
"$PYTHON_BIN" -m src.v3_inference smoke --prompt-config "$PROMPT_CONFIG" --manifest "$SCREEN_MANIFEST" --split "$SCREEN_SPLIT"

SCREEN_RUN="v3_${MODEL_SLUG}_promptval180_seed42"
"$PYTHON_BIN" -m src.v3_inference run --run-id "$SCREEN_RUN" --split "$SCREEN_SPLIT" --conditions clean --concurrency "$CONCURRENCY" --prompt-config "$PROMPT_CONFIG" --manifest "$SCREEN_MANIFEST"
"$PYTHON_BIN" -m src.v3_clean_gate --run-id "$SCREEN_RUN" --phase "$SCREEN_PHASE"

MAIN_RUN="v3_${MODEL_SLUG}_main_seed42"
"$PYTHON_BIN" -m src.v3_inference run --run-id "$MAIN_RUN" --split main --conditions clean --concurrency "$CONCURRENCY" --prompt-config "$PROMPT_CONFIG" --manifest "$CONDITION_MANIFEST"
"$PYTHON_BIN" -m src.v3_clean_gate --run-id "$MAIN_RUN" --phase main

if [[ "$RUN_ATTACKS" != "1" ]]; then
  echo "Clean gates passed. Review reports/v3/clean_gates/, then rerun with V3_RUN_ATTACKS=1."
  exit 0
fi

"$PYTHON_BIN" -m src.v3_inference run --run-id "$MAIN_RUN" --split main --conditions "${MAIN_CONDITIONS[@]}" --concurrency "$CONCURRENCY" --prompt-config "$PROMPT_CONFIG" --manifest "$CONDITION_MANIFEST"
"$PYTHON_BIN" -m src.v3_inference run --run-id "v3_${MODEL_SLUG}_style_seed42" --split style_ablation --conditions "${STYLE_CONDITIONS[@]}" --concurrency "$CONCURRENCY" --prompt-config "$PROMPT_CONFIG" --manifest "$CONDITION_MANIFEST"
"$PYTHON_BIN" -m src.v3_inference run --run-id "v3_${MODEL_SLUG}_size_seed42" --split size_ablation --conditions "${SIZE_CONDITIONS[@]}" --concurrency "$CONCURRENCY" --prompt-config "$PROMPT_CONFIG" --manifest "$CONDITION_MANIFEST"

echo "Completed V3 full matrix for $MODEL_SLUG"
