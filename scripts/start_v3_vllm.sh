#!/usr/bin/env bash
set -euo pipefail

VLLM_BIN="${V3_VLLM_BIN:-$(command -v vllm || true)}"
MODEL_PATH="${V3_MODEL_PATH:-Qwen/Qwen3.5-27B}"
SERVED_NAME="${V3_SERVED_NAME:-qwen3.5-27b}"
PORT="${V3_VLLM_PORT:-8000}"

if [[ -z "$VLLM_BIN" ]]; then
  echo "vLLM was not found. Activate its environment or set V3_VLLM_BIN." >&2
  exit 1
fi

exec "$VLLM_BIN" serve "$MODEL_PATH" \
  --host 0.0.0.0 \
  --port "$PORT" \
  --served-model-name "$SERVED_NAME" \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.88 \
  --max-num-seqs 5 \
  --limit-mm-per-prompt '{"image": 1}' \
  --generation-config vllm \
  --dtype half \
  --enforce-eager \
  --trust-remote-code
