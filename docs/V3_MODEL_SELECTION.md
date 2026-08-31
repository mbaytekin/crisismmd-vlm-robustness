# Historical model-screening rationale — eliminated from paper-facing use

**Status:** The candidate/gate policy below is superseded by the completed
six-model panel in D018--D037. It must not be supplied to a manuscript-writing
model or used to qualify the reported results. It remains only as execution
history.

Selection date: 2026-08-11. Revised after the Qwen3.5 9B pilot produced only 53.3% clean accuracy. The goal is to measure attack robustness only on models that first demonstrate adequate CrisisMMD task competence.

## Clean-screen candidate panel

| Model | Nominal size | Why it is included |
|---|---:|---|
| Gemma 4 Unified | 12B | Lowest retained large-model candidate and recent unified multimodal architecture. |
| Mistral Small 3.1 | 24B | Independent Pixtral-style vision architecture and family diversity. |
| Gemma 4 MoE | 26B A4B | Mixture-of-experts contrast; 26B total but only about 4B active parameters. |
| Qwen3.5 | 27B | Current dense Qwen candidate and successor to the weak 9B baseline. |
| Gemma 4 Dense | 31B | Large dense Gemma candidate. |
| Qwen3-VL Instruct | 32B | Vision-specialized large Qwen comparator. |
| Qwen3-VL MoE Instruct | 235B-A22B | Ultra-large vision-specialized MoE; 4-bit Mac checkpoint is about 133 GB. |
| Qwen3.5 MoE | 397B-A17B | Ultra-large current unified multimodal MoE; 4-bit Mac checkpoint is about 224 GB. |

The standard 12B–32B tier uses MLX 8-bit checkpoints. The 235B and 397B ultra-large tier uses MLX 4-bit checkpoints so both fit safely beside macOS, Metal, vision state, and KV cache on the 512 GB machine. Compare size only within a precision tier; treat standard-versus-ultra differences as capability evidence with a quantization caveat, not a pure parameter-scaling effect. “Model size” is the original total parameter count, while `A22B`/`A17B` records active MoE parameters.

## Clean-first qualification

1. Run the selected zero-shot prompt on the 180-example prompt-validation split (60 per class). Stop below 60% accuracy, 55% macro-F1, 40% minimum class recall, or 99.5% parse rate.
2. For screen passers, run only the 720 clean main examples. Stop below 70% accuracy, 65% macro-F1, 50% minimum class recall, or 99.5% parse rate.
3. Run attack, benign, style, and size conditions only after both gates pass. Publish the clean screen for every rejected candidate to avoid selective reporting.

The main gate is intentionally stricter and class-aware: high aggregate accuracy cannot hide collapse on `mild_damage` or another class. Clean qualification uses no attacked images and therefore cannot select models based on favorable attack outcomes.

## Why this backend policy

- MLX is designed for Apple Silicon and unified CPU/GPU memory.
- MLX-VLM exposes an OpenAI-compatible server and currently supports Qwen3/3.5 VL, Gemma 4, Mistral3, MiniCPM-V and other VLM families.
- The pipeline remains in Docker for dependency reproducibility, but the Metal model server runs natively and is reached through `host.docker.internal`.
- NVIDIA replication uses the official version-pinned vLLM OpenAI image.
- vLLM-Metal is promising but currently lists native multimodal support only for a small experimental set (not the whole candidate panel), so it is not the common primary backend.
- Docker Model Runner can use Metal on Apple Silicon and supports vision through llama.cpp-compatible models, but it would introduce a second model-format/runtime axis. Keep it as an operational fallback, not the primary paper backend.

## Precision policy

Use 8-bit MLX weights for screening and primary full runs. If Qwen3.5 27B qualifies, run its BF16/8-bit/4-bit sensitivity on prompt-validation + main. This prevents quantization from being silently mixed with model-family/size effects.

## Sources

- Qwen3.5 implementation and multimodal configuration: https://huggingface.co/docs/transformers/model_doc/qwen3_5
- Qwen3.5 27B model card: https://huggingface.co/Qwen/Qwen3.5-27B
- Qwen3-VL 32B model card: https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct
- Qwen3-VL 235B-A22B model card: https://huggingface.co/Qwen/Qwen3-VL-235B-A22B-Instruct
- Qwen3.5 397B-A17B model card: https://huggingface.co/Qwen/Qwen3.5-397B-A17B
- Gemma 4 overview: https://ai.google.dev/gemma/docs/core
- Gemma 4 technical report: https://arxiv.org/abs/2607.02770
- Mistral Small 3.1 model card: https://docs.mistral.ai/models/model-cards/mistral-small-3-1-25-03
- MiniCPM-V official repository/model documentation: https://github.com/OpenBMB/MiniCPM-V
- MLX-VLM server and model support: https://github.com/Blaizzy/mlx-vlm
- vLLM-Metal support matrix: https://docs.vllm.ai/projects/vllm-metal/en/latest/supported_models/
- Docker Model Runner engines: https://docs.docker.com/ai/model-runner/inference-engines/
- Official vLLM Docker deployment: https://docs.vllm.ai/en/latest/deployment/docker/

All model repository revisions must be resolved to immutable Hub SHAs immediately before production and stored under `reports/v3/model_locks/`.
