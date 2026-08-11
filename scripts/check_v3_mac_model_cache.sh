#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${V3_PYTHON:-.venv-mac/bin/python}"
PLATFORM="${1:-mac}"

if [[ "$PLATFORM" != "mac" && "$PLATFORM" != "nvidia" ]]; then
  echo "Usage: $0 [mac|nvidia]" >&2
  exit 2
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN." >&2
  echo "Run scripts/setup_docker_mac.sh first, or set V3_PYTHON." >&2
  exit 1
fi

"$PYTHON_BIN" - "$PLATFORM" <<'PY'
import sys
from pathlib import Path

from src.model_registry import registry

platform = sys.argv[1]
field = "mac_model_id" if platform == "mac" else "nvidia_model_id"
cache_root = Path.home() / ".cache" / "huggingface" / "hub"

for model in registry()["models"]:
    model_id = model[field]
    cache_name = "models--" + model_id.replace("/", "--")
    cache_dir = cache_root / cache_name
    present = cache_dir.exists() and any(cache_dir.iterdir())
    status = "present" if present else "missing"
    size = ""
    if present:
        try:
            bytes_total = sum(p.stat().st_size for p in cache_dir.rglob("*") if p.is_file())
            size = f" ({bytes_total / 1024**3:.1f} GiB)"
        except OSError:
            size = ""
    print(f"{status:7} {model['slug']:26} {model_id}{size}")
PY
