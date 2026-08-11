#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_ID="${V3_MODEL_ID:-mlx-community/Qwen3.5-27B-8bit}"
SERVER_PORT="${V3_MLX_PORT:-8080}"
MAX_KV_SIZE="${V3_MAX_KV_SIZE:-4096}"

cd "$PROJECT_ROOT"
if [[ ! -x .venv-mac/bin/python ]]; then
  echo "Run scripts/setup_macos.sh first." >&2
  exit 1
fi

exec .venv-mac/bin/python -m mlx_vlm.server \
  --model "$MODEL_ID" \
  --host 127.0.0.1 \
  --port "$SERVER_PORT" \
  --max-kv-size "$MAX_KV_SIZE" \
  --vision-cache-size 1 \
  --trust-remote-code
