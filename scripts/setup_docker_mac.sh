#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" || "$(uname -m)" != "arm64" ]]; then
  echo "This setup is intended for Apple Silicon macOS." >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not on PATH." >&2
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed, but the Docker daemon is not reachable. Start Docker Desktop and rerun this script." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it with: brew install uv" >&2
  exit 1
fi

echo "Setting up native macOS MLX environment..."
scripts/setup_macos.sh

echo "Building Docker research pipeline image..."
docker compose -f docker/compose.mac.yml build

echo
echo "Done. Start a model server in one terminal, for example:"
echo "  scripts/start_v3_mlx.sh mlx-community/Qwen3.5-27B-8bit"
echo
echo "Then smoke-test from Docker in another terminal:"
echo "  docker compose -f docker/compose.mac.yml run --rm research python -m src.v3_inference smoke"
