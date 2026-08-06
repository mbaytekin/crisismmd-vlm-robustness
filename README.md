# CrisisMMD VLM Robustness

Reproducible research codebase for evaluating whether typographic visual and multimodal interventions can alter a vision-language model’s disaster-damage severity assessment on CrisisMMD.

The primary V2 experiment uses a frozen prompt and a locally served `qwen3.5-9b-awq` model through vLLM. The study compares clean inputs with benign controls, direct instruction attacks, and misleading-claim attacks.

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
configs/       prompts, model settings, attack payloads, V2 pipeline config
src/           data preparation, attack generation, inference, evaluation, reporting
tests/         reproducibility, parser, cache, split, and metric tests
scripts/       legacy V1 shell entry points retained for reference
reports/v2/    publication-facing reports, tables, audit gallery, and review templates
data/v2/       local generated manifests, split metadata, and attack-image documentation
```

Raw CrisisMMD files, generated attack images, processed dataset derivatives, inference caches, and local logs are excluded by `.gitignore`. The repository is intended to contain code, configuration, tests, documentation, and aggregate research artifacts—not the dataset itself.

## Audit and manual review

The independent audit is available at [`reports/v2/audit/audit_gallery.html`](reports/v2/audit/audit_gallery.html). It compares clean and modified images, model outputs, payload metadata, confidence, label changes, and severity drop for representative examples.

Automatic validation checks image decodability, source identity, bounding boxes, text preservation, modality consistency, contrast, occupied area, and manifest completeness. An automatic `PASS` does not replace human review of readability, plausibility, critical-region visibility, or ethical validity.

## Dataset and responsible use

CrisisMMD is an external dataset. Follow its official terms of use and citation requirements. Do not commit raw images, tweet text, or generated dataset derivatives to a public repository unless the applicable terms explicitly permit it. Dataset acquisition and local preparation are intentionally separate from the tracked research code.

## Citation

Please cite the original CrisisMMD publications and the dataset source listed by the CrisisNLP project. This repository’s technical reports record the exact prompt lock, model identity, seeds, run IDs, and evaluation definitions used for the reported results.
