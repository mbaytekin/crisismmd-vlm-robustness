# BF16 Experiment Runtime Durations

**Updated:** 2026-08-27

**Scope:** GCP A100/vLLM BF16 runs for the paper-facing V3 experiments.

## Runtime table

The durations below are reconstructed from the first and last `request_timestamp`
in each completed `predictions.jsonl`. They measure the inference request span;
model download, model loading, and post-inference analysis are not included.

| Model | Main | Style ablation | Size ablation | Natural clean | Official test |
|---|---:|---:|---:|---:|---:|
| Mistral 24B BF16 | 4h 22m | 47m | 23m | 2h 13m | 20m |
| Qwen3.5 27B BF16 | 5h 58m | 1h | 30m | 2h 53m | 26m |
| Qwen3.6 27B BF16 | 5h 53m | 59m | 29m | 2h 51m | 26m |
| Qwen3-VL 32B BF16 | 6h 58m | 1h 10m | 34m | 3h 28m | 32m |

## Completed timed main runs

| Model | Workload | Inference request span | End-to-end | Status | Timing record |
|---|---:|---:|---:|---|---|
| Qwen3.5 27B BF16 | 7,200 predictions | 5h 57m 43s | 6h 03m 27s | Complete; 7,200 parsed | `logs/v3/gcp_a100/timed_jobs/20260826T145403Z__qwen35__main/timing.json` |
| Qwen3.6 27B BF16 | 7,200 predictions | 5h 52m 56s | 5h 58m 47s | Complete; 7,200 parsed | `logs/v3/gcp_a100/timed_jobs/20260826T145418Z__qwen36__main/timing.json` |

Both jobs used the upstream CUDA checkpoints, BF16, one A100 80 GB GPU, vLLM,
the frozen V4 prompt, concurrency 1, and the same V3 manifests and decoding
settings. End-to-end time includes server startup and post-inference analysis;
the horizontal runtime table reports only the inference request span for
consistency with the other completed experiments.

## Provenance note

The earlier inventory described some Qwen3.5 secondary runs as local MLX runs.
The retained GCP artifacts show that Qwen3.5 style and size were already
completed on GCP A100/vLLM on 2026-08-24, so they were not duplicated. The two
formerly missing Qwen3.5 and Qwen3.6 main tracks are now complete.

The underlying completed artifacts remain separate by model and runtime under
`results/v3/gcp_a100/<model>/`. The paper-facing open-model table now uses the
completed A100/vLLM runs. MLX repeats remain separate, noncanonical audit
artifacts and are not pooled with the A100 predictions.
