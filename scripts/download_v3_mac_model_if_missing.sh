#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SLUG="${1:-qwen35_27b_8bit}"
PLATFORM="${2:-mac}"
CHECK_ONLY="${CHECK_ONLY:-0}"

if [[ "$PLATFORM" != "mac" && "$PLATFORM" != "nvidia" ]]; then
  echo "Usage: $0 [MODEL_SLUG] [mac|nvidia]" >&2
  exit 2
fi

PYTHON_BIN="${V3_PYTHON:-.venv-mac/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Python environment not found at $PYTHON_BIN." >&2
  echo "Run scripts/setup_docker_mac.sh first, or set V3_PYTHON." >&2
  exit 1
fi

"$PYTHON_BIN" - "$SLUG" "$PLATFORM" "$CHECK_ONLY" <<'PY'
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

from src.model_registry import registry

slug, platform, check_only = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
models = {model["slug"]: model for model in registry()["models"]}
if slug not in models:
    known = ", ".join(sorted(models))
    raise SystemExit(f"Unknown model slug: {slug}\nKnown slugs: {known}")

model = models[slug]
field = "mac_model_id" if platform == "mac" else "nvidia_model_id"
model_id = model[field]
cache_name = "models--" + model_id.replace("/", "--")
cache_dir = Path.home() / ".cache" / "huggingface" / "hub" / cache_name

if cache_dir.exists() and any(cache_dir.iterdir()):
    print(f"Model already exists in Hugging Face cache: {model_id}")
    print(f"Cache path: {cache_dir}")
    raise SystemExit(0)

print(f"Model is missing locally, downloading: {model_id}")
if check_only:
    print("CHECK_ONLY=1, so no download was started.")
    raise SystemExit(3)
print("This can take a long time for large VLM checkpoints.")
snapshot_download(repo_id=model_id, resume_download=True)
print(f"Downloaded: {model_id}")
PY
