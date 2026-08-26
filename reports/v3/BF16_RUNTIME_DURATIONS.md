# BF16 Experiment Runtime Durations

**Snapshot:** 2026-08-26 15:00 UTC

**Scope:** GCP A100/vLLM BF16 runs for the paper-facing V3 experiments.

## Runtime table

The durations below are reconstructed from the first and last `request_timestamp`
in each completed `predictions.jsonl`. They measure the inference request span;
model download, model loading, and post-inference analysis are not included.

| Model | Main | Style ablation | Size ablation | Natural clean | Official test |
|---|---:|---:|---:|---:|---:|
| Mistral 24B BF16 | 4h 22m | 47m | 23m | 2h 13m | 20m |
| Qwen3.5 27B BF16 | running | 1h | 30m | 2h 53m | 26m |
| Qwen3.6 27B BF16 | running | 59m | 29m | 2h 51m | 26m |
| Qwen3-VL 32B BF16 | 6h 58m | 1h 10m | 34m | 3h 28m | 32m |

`running` means the experiment was still in progress at the snapshot time.

## Current missing runs

Two missing A100 comparisons were started in parallel on 2026-08-26:

| Model | Track | Workload | VM | Timing record |
|---|---|---:|---|---|
| Qwen3.5 27B BF16 | Main | 7200 predictions | `can-crisismmd-qwen35-ablation` | `logs/v3/gcp_a100/timed_jobs/20260826T145403Z__qwen35__main/timing.json` |
| Qwen3.6 27B BF16 | Main | 7200 predictions | `can-crisismmd-a100-80gb-20260824` | `logs/v3/gcp_a100/timed_jobs/20260826T145418Z__qwen36__main/timing.json` |

These jobs use the upstream CUDA checkpoints, BF16, one A100 80 GB GPU, vLLM,
the frozen V4 prompt, concurrency 1, and the same V3 manifests and decoding
settings. The timing wrapper records the end-to-end duration, including model
startup and analysis, and shuts down the VM after completion when launched with
`V3_SHUTDOWN_ON_EXIT=1`.

## Provenance note

The earlier inventory described some Qwen3.5 secondary runs as local MLX runs.
The retained GCP artifacts show that Qwen3.5 style and size were already
completed on GCP A100/vLLM on 2026-08-24, so they were not duplicated. The only
missing BF16 A100 comparisons at the time of this snapshot were the two main
tracks listed above.

The underlying completed artifacts remain separate by model and runtime under
`results/v3/gcp_a100/<model>/`. Results from MLX and CUDA/vLLM are not pooled as
if they were the same runtime; runtime provenance is retained for reproducibility.
