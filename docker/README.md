# Container profiles

The pipeline container is hardware-neutral. It reads local images from the mounted repository and sends base64 image requests to an OpenAI-compatible model server.

## Apple Silicon

Metal inference runs natively on macOS; the Linux VM used by an ordinary Compose service must not be treated as the model runtime. Start `mlx_vlm.server` with `scripts/start_v3_mlx.sh`, then run:

```bash
docker compose -f docker/compose.mac.yml build
docker compose -f docker/compose.mac.yml run --rm research \
  python -m src.v3_inference smoke
```

The container reaches the native server through `host.docker.internal:8080/v1`.

## NVIDIA

```bash
V3_MODEL_ID=Qwen/Qwen3.5-9B V3_SERVED_NAME=qwen35-9b \
docker compose -f docker/compose.nvidia.yml up -d vllm

docker compose -f docker/compose.nvidia.yml run --rm research \
  python -m src.v3_inference smoke
```

The official vLLM image is version-pinned. Resolve and record the model commit before a production run.
