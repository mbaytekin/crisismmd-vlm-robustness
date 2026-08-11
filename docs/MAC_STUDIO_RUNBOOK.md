# Mac Studio M3 Ultra runbook

Target: Apple Silicon M3 Ultra with 512 GB unified memory. Run one model at a time. Large memory capacity does not remove the need to control model revision, precision, backend version, concurrency, thermal state, and cache behavior.

## 1. Transfer and verify data

Clone the public repository. The recommended portable transfer uses a mounted
external disk, preserves repository-relative paths, and verifies every copied
file with SHA-256. The Ubuntu export/restore procedure is documented separately
in [`UBUNTU_DATA_TRANSFER.md`](UBUNTU_DATA_TRANSFER.md).

On the source Linux machine, find the mount point and export:

```bash
findmnt -nr -S /dev/sda1 -o TARGET
mkdir -p /media/db21052/YZTB_Vision/can.baytekin
scripts/transfer_research_data.py export \
  /media/db21052/YZTB_Vision/can.baytekin
scripts/transfer_research_data.py verify-disk \
  /media/db21052/YZTB_Vision/can.baytekin
```

On the Mac, clone the repository and import from the mounted volume:

```bash
git clone git@github.com:mbaytekin/crisismmd-vlm-robustness.git
cd crisismmd-vlm-robustness
scripts/transfer_research_data.py import \
  /Volumes/YZTB_Vision/can.baytekin
scripts/transfer_research_data.py verify-repo \
  /Volumes/YZTB_Vision/can.baytekin
python scripts/freeze_v3_artifacts.py check
```

The transfer bundle includes these ignored/private locations when present:

```text
data/
results/
logs/
reports/private/
reports/manual_review/assets/
.model-lock/
```

Import overwrites only manifest-listed files whose content differs and never
deletes extra local files. Model caches and virtual environments are not
included. Do not move private tweet text through public Git. Verify the freeze
hash manifest before inference.

The current external disk is NTFS. Native macOS access is normally read-only,
which is sufficient for importing the bundle. Writing a refreshed bundle from
the Mac requires a compatible NTFS write driver; do not reformat the disk
without a separate backup.

## 2. Install native Metal runtime

```bash
scripts/setup_macos.sh
```

The script requires native `arm64` macOS, Python 3.12 through `uv`, and installs pinned `mlx-vlm==0.6.4` in `.venv-mac`.

## 3. Build the pipeline container

```bash
docker compose -f docker/compose.mac.yml build
```

Docker holds Python data/evaluation dependencies. MLX-VLM runs on macOS because an ordinary Docker Desktop Linux container is not the common Metal runtime used by this study.

## 4. Lock and start one model

```bash
.venv-mac/bin/python -m src.model_registry lock \
  --slug qwen35_27b_8bit --platform mac

V3_MODEL_ID=mlx-community/Qwen3.5-27B-8bit \
scripts/start_v3_mlx.sh
```

In a second terminal:

```bash
VLM_BASE_URL=http://127.0.0.1:8080/v1 \
.venv-mac/bin/python -m src.v3_inference smoke
```

Alternatively run the client in Docker:

```bash
docker compose -f docker/compose.mac.yml run --rm research \
  python -m src.v3_inference smoke
```

## 5. Pilot gate, then full matrix

Clean-only screening (default):

```bash
VLM_BASE_URL=http://127.0.0.1:8080/v1 \
V3_PYTHON=.venv-mac/bin/python \
V3_CONCURRENCY=1 \
scripts/run_v3_model.sh qwen35_27b_8bit
```

The runner stops immediately if the 90-image pilot gate fails. A pilot passer continues with 720 main clean images and stops if the stricter main gate fails. After reviewing `reports/v3/clean_gates/`, explicitly unlock attacks for a qualified model:

```bash
VLM_BASE_URL=http://127.0.0.1:8080/v1 \
V3_PYTHON=.venv-mac/bin/python \
V3_RUN_ATTACKS=1 \
V3_CONCURRENCY=1 \
scripts/run_v3_model.sh qwen35_27b_8bit
```

Run IDs and SQLite caches are deterministic, so completed clean requests are reused.

## 6. Operational checks

- Keep the frozen prompt and condition manifests unchanged.
- Disable thinking for every model; if a backend cannot disable it, record that incompatibility and do not silently compare it with non-thinking runs.
- Begin at concurrency 1. Raise it only after deterministic and stability checks.
- Record wall time, per-request latency, parse failures, retries, memory pressure, swap use, model SHA, backend version, and server command.
- Avoid active memory pressure/swap during production. Restart the server between models.
- Back up `results/v3/` after every model.
- Never mix BF16, 8-bit, and 4-bit in the primary panel without labeling precision explicitly.

## 7. Expected workload

Each complete model has 9,900 condition predictions:

| Split | Source samples | Conditions | Predictions |
|---|---:|---:|---:|
| Pilot | 90 | 10 | 900 |
| Main | 720 | 10 | 7,200 |
| Style | 120 | 10 | 1,200 |
| Size | 60 | 10 | 600 |
| Total | 990 | — | 9,900 |

Each rejected candidate costs at most 90 or 810 clean predictions. Every model that passes both gates produces 9,900 full-matrix predictions. With eight candidates, the maximum is 79,200 full-matrix predictions, but the actual total depends on qualification. Estimate runtime from a 100-request benchmark rather than parameter count alone.

The 235B-A22B and 397B-A17B ultra tier uses 4-bit checkpoints (about 133 GB and 224 GB respectively); the standard tier remains 8-bit. Fully stop the previous server and confirm low memory pressure before loading either ultra model. Never pool the two precision tiers in an unqualified size regression.
