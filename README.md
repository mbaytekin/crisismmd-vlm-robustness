# CrisisMMD VLM Robustness

Reproducible research codebase for evaluating whether typographic visual and multimodal interventions can alter a vision-language model’s disaster-damage severity assessment on CrisisMMD.

V2 is the completed historical experiment. V3 is the corrected primary pipeline: it removes tweet/near-image split leakage, excludes unusable text/images, matches visual dose across payload families, freezes size-ablation placement, and validates camouflage contrast after rendering. V3 uses one frozen prompt and clean-screens eight 12B–397B candidate models through one MLX-VLM backend on Apple Silicon before any attack inference.

## Research question

Can an attacker change a disaster image, its accompanying text, or both so that a vision-language model underestimates the visible physical damage while the CrisisMMD ground-truth label remains unchanged?

The threat model is black-box, training-free, and model-independent. It does not use gradients, model weights, fine-tuning, optimized pixel noise, or attack-specific prompt changes.

## Experiment design

The V2 main experiment contains 900 unique samples evaluated under 10 paired conditions:

- `clean`
- `benign_image`, `benign_text`, `benign_joint`
- `direct_image`, `direct_text`, `direct_joint`
- `misleading_image`, `misleading_text`, `misleading_joint`

This produces 9,000 model evaluations. Additional image-only ablations evaluate three visual styles (`simple`, `news`, `camouflage`) and three text sizes (`small`, `medium`, `large`). All conditions use the same frozen prompt, temperature 0, top-p 1, seed 42, and a locked local model identity.

## Metrics

- **ASR:** fraction of clean-correct samples whose attacked prediction becomes incorrect.
- **Severity drop:** ordinal clean prediction minus attacked prediction, using `little_or_no_damage=0`, `mild_damage=1`, and `severe_damage=2`.
- **Under-triage:** severe ground-truth samples predicted as mild or little/no damage.
- **Benign control effect:** label changes caused by neutral controls; these are not counted as adversarial attack success.
- **Paired uncertainty:** deterministic paired bootstrap intervals and Holm-adjusted exact McNemar tests.

## Current results

The main run is complete with 9,000/9,000 parsed predictions. The strongest main condition is `direct_image` (ASR 32.5%, severity drop 0.576), followed by `direct_joint` (30.5%, 0.422). Misleading image and joint conditions reach 23.5% and 26.1% ASR, respectively. Benign controls produce much smaller effects and are used to separate ordinary content sensitivity from adversarial behavior.

The full tables, ablations, confidence intervals, error analysis, and audit materials are in [`reports/v2/`](reports/v2/), with the entry point at [`reports/v2/final_summary.md`](reports/v2/final_summary.md).

The corrected V3 Qwen 9B pilot contains 90 independent samples × 10 conditions (900/900 parsed). Clean accuracy is 53.3%, so V3 attack estimates are exploratory and use 48 clean-correct samples. Direct-image and direct-joint ASR are both 39.6% (95% Wilson CI 27.0%–53.7%); benign-image/joint instability is 12.2%. See [`reports/v3/pilot_results.md`](reports/v3/pilot_results.md).

## Corrected V3 workflow

The full V3 study is designed for a 512 GB M3 Ultra Mac Studio. Start with [`docs/V3_TODO.md`](docs/V3_TODO.md), then use the [`Mac Studio runbook`](docs/MAC_STUDIO_RUNBOOK.md). External-disk export and Ubuntu restore instructions are in [`docs/UBUNTU_DATA_TRANSFER.md`](docs/UBUNTU_DATA_TRANSFER.md). Model choices and size-tier rationale are documented in [`docs/V3_MODEL_SELECTION.md`](docs/V3_MODEL_SELECTION.md); the executable registry is [`configs/v3/models.yaml`](configs/v3/models.yaml).

On the Mac, MLX-VLM runs natively so it can use Metal. The version-pinned Docker container runs the research pipeline and calls that native OpenAI-compatible endpoint. An NVIDIA/vLLM Compose profile is retained as a portability path, but results from different backends must not be pooled in the primary comparison.

```bash
scripts/setup_macos.sh
scripts/start_v3_mlx.sh mlx-community/Qwen3.5-27B-8bit
python -m src.model_registry validate
python scripts/freeze_v3_artifacts.py check
scripts/run_v3_model.sh qwen35_27b_8bit
```

The runner defaults to clean-only screening: 90 pilot images followed by 720 main images if the pilot passes. Review the gate reports, then rerun a qualified model with `V3_RUN_ATTACKS=1` to unlock adversarial, benign, style, and size conditions.

```bash
python -m src.v3_pipeline prepare
python -m src.v3_pipeline generate --split pilot
python -m src.v3_pipeline generate --split main
python -m src.v3_pipeline generate --split style_ablation
python -m src.v3_pipeline generate --split size_ablation
python -m src.v3_pipeline validate

scripts/start_v3_vllm.sh
python -m src.v3_inference smoke
python -m src.v3_inference run --run-id RUN_ID --split pilot \
  --conditions clean benign_image benign_text benign_joint direct_image direct_text direct_joint misleading_image misleading_text misleading_joint \
  --concurrency 5
python -m src.v3_reporting --run-id RUN_ID
```

V3 selects one representative per globally constructed duplicate cluster. Clusters union exact tweet IDs/text, exact image SHA/pHash, and dHash neighbours within Hamming distance 4. The old prompt-selection pilot, suspected mojibake, and images with a short side below 128 px are excluded before selection.

## Reproducible V2 workflow

Use the project’s existing Conda environment:

```bash
conda activate vlm_app
pytest -q
```

Prepare splits and manifests:

```bash
python -m src.v2_pipeline prepare
python -m src.v2_pipeline generate --split pilot
python -m src.v2_pipeline validate --split pilot
```

After the pilot gate passes, generate and validate the remaining splits:

```bash
python -m src.v2_pipeline generate --split main
python -m src.v2_pipeline generate --split style_ablation
python -m src.v2_pipeline generate --split size_ablation

python -m src.v2_pipeline validate --split main
python -m src.v2_pipeline validate --split style_ablation
python -m src.v2_pipeline validate --split size_ablation
```

Run inference against a local OpenAI-compatible vLLM server and evaluate each run:

```bash
python -m src.v2_pipeline inference --run-id v2_main_YYYYMMDD_HHMMSS --split main --concurrency 5
python -m src.v2_pipeline evaluate --run-id v2_main_YYYYMMDD_HHMMSS --split main
```

The same `inference` and `evaluate` commands apply to `pilot`, `style_ablation`, and `size_ablation`. Inference uses a per-run SQLite cache and can be resumed with the same run ID.

## Repository structure

```text
configs/       prompts, model settings, and versioned attack/pipeline configs
src/           data preparation, attack generation, inference, evaluation, reporting
tests/         reproducibility, parser, cache, split, and metric tests
scripts/       legacy V1 shell entry points retained for reference
reports/v2/    historical experiment reports and corrected retrospective analysis
reports/v3/    corrected split/attack validation, pilot metrics, and review package
data/v2/       historical generated-data documentation
data/v3/       corrected generated-data documentation (large outputs ignored)
```

Raw CrisisMMD files, generated attack images, processed dataset derivatives, inference caches, and local logs are excluded by `.gitignore`. The repository is intended to contain code, configuration, tests, documentation, and aggregate research artifacts—not the dataset itself.

## Audit and manual review

The independent audit is available at [`reports/v2/audit/audit_gallery.html`](reports/v2/audit/audit_gallery.html). It compares clean and modified images, model outputs, payload metadata, confidence, label changes, and severity drop for representative examples.

Automatic validation checks image decodability, source identity, bounding boxes, text preservation, modality consistency, contrast, occupied area, and manifest completeness. An automatic `PASS` does not replace human review of readability, plausibility, critical-region visibility, or ethical validity.

## Dataset and responsible use

CrisisMMD is an external dataset. Follow its official terms of use and citation requirements. Do not commit raw images, tweet text, or generated dataset derivatives to a public repository unless the applicable terms explicitly permit it. Dataset acquisition and local preparation are intentionally separate from the tracked research code.

## Citation

Please cite the original CrisisMMD publications and the dataset source listed by the CrisisNLP project. This repository’s technical reports record the exact prompt lock, model identity, seeds, run IDs, and evaluation definitions used for the reported results.
