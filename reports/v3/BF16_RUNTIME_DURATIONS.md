# BF16 Experiment Runtime Durations

**Updated:** 2026-08-29

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
| Qwen3.8 27B BF16 | 6h 52m | 1h 08m | 34m | 3h 17m | 30m |
| Qwen3-VL 32B BF16 | 6h 58m | 1h 10m | 34m | 3h 28m | 32m |

## Completed timed main runs

| Model | Workload | Inference request span | End-to-end | Status | Timing record |
|---|---:|---:|---:|---|---|
| Qwen3.5 27B BF16 | 7,200 predictions | 5h 57m 43s | 6h 03m 27s | Complete; 7,200 parsed | `logs/v3/gcp_a100/timed_jobs/20260826T145403Z__qwen35__main/timing.json` |
| Qwen3.6 27B BF16 | 7,200 predictions | 5h 52m 56s | 5h 58m 47s | Complete; 7,200 parsed | `logs/v3/gcp_a100/timed_jobs/20260826T145418Z__qwen36__main/timing.json` |

## Completed extension and follow-up request spans

These spans are reconstructed from the first and last `request_timestamp` in
each pulled prediction file. They are inference spans only; no end-to-end
timing record was pulled for the extension jobs.

| Model/workload | Predictions | Request span | Status |
|---|---:|---:|---|
| Qwen3.8 main | 7,200 | 6h 52m 15s | Complete; 7,200 parsed |
| Qwen3.8 style | 1,200 | 1h 07m 56s | Complete; 1,200 parsed |
| Qwen3.8 relative size | 600 | 33m 55s | Complete; 600 parsed |
| Qwen3.8 natural clean | 3,474 | 3h 16m 56s | Complete; 3,474 parsed |
| Qwen3.8 official clean | 529 | 29m 46s | Complete; 529 parsed |
| Qwen3.8 text rhetoric | 1,080 | 59m 33s | Complete; 1,080 parsed |
| Qwen3.8 point size | 960 | 54m 48s | Complete; 960 parsed |

### Follow-up spans for all open BF16 models

| Model | Text rhetoric (1,080) | Point size (960) |
|---|---:|---:|
| Qwen3.5 27B BF16 | 53m 32s | 47m 58s |
| Qwen3.6 27B BF16 | 52m 43s | 47m 14s |
| Qwen3.8 27B BF16 | 59m 33s | 54m 48s |
| Qwen3-VL 32B BF16 | 1h 04m 45s | 56m 21s |
| Mistral 24B BF16 | 36m 31s | 37m 16s |

The five-open-model follow-up spans are retained in the prediction artifacts;
all ten text/point-size files contain the expected parsed rows. The GCP VMs
remain running during the active work session and are stopped only on the
user's final instruction.

Both jobs used the upstream CUDA checkpoints, BF16, one A100 80 GB GPU, vLLM,
the fixed zero-shot prompt, concurrency 1, and the same V3 manifests and decoding
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
