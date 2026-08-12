#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This setup is for native arm64 macOS only." >&2
  exit 1
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "Install uv first: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

uv venv --python 3.12 .venv-mac
uv pip install --python .venv-mac/bin/python -r requirements-docker.txt
uv pip install --python .venv-mac/bin/python "mlx-vlm==0.6.3"
uv pip install --python .venv-mac/bin/python "torch==2.13.0" "torchvision==0.28.0"
.venv-mac/bin/python scripts/patch_mlx_vlm_mac_thread_stream.py

.venv-mac/bin/python - <<'PY'
import platform
import mlx.core as mx
import mlx_vlm
print({"machine": platform.machine(), "mlx_device": str(mx.default_device()), "mlx_vlm": getattr(mlx_vlm, "__version__", "unknown")})
PY
