# CrisisMMD VLM Robustness

Reproducible research codebase for evaluating whether typographic visual and multimodal interventions can alter a vision-language model’s disaster-damage severity assessment on CrisisMMD.

The single paper-writing reference is
[`reports/v3/ALL_RESULTS.md`](reports/v3/ALL_RESULTS.md). It combines active
decisions, dataset construction, completed BF16 + Gemini results, claim bounds,
remaining work, and bibliography. The full decision history remains in
[`docs/PAPER_DECISIONS.md`](docs/PAPER_DECISIONS.md).

## Paper and GPT workflow

Use the following order for manuscript work or a new GPT conversation:

1. Read [`reports/v3/ALL_RESULTS.md`](reports/v3/ALL_RESULTS.md) as the canonical
   manuscript reference.
2. Use [`docs/PAPER_DECISIONS.md`](docs/PAPER_DECISIONS.md) only when the dated
   history or a superseded protocol choice must be audited.
3. Edit [`paper.md`](paper.md) from the canonical reference and preserve every
   stated caveat.
4. Verify empirical claims using the evidence paths linked from the reference;
   conversation summaries alone are not evidence.
5. Record a new dated decision in the log before changing a prompt, cohort,
   threshold, metric, model panel, exclusion, or manuscript claim. Preserve old
   decisions by marking them `SUPERSEDED` rather than deleting them.

Give GPT `reports/v3/ALL_RESULTS.md` and the current `paper.md`, then use:

```text
ALL_RESULTS.md dosyasını paper kararları, dataset yöntemi ve sonuçlar için
kanonik referans kabul et. paper.md ile çelişkileri bul, caveat'leri koru,
sonuç tablolarındaki paydaları değiştirme ve kanıtsız iddia ekleme.
```

V2 is the completed historical experiment. V3 is the corrected primary pipeline: it removes tweet/near-image split leakage, excludes unusable text/images, matches visual dose across payload families, freezes size-ablation placement, and validates camouflage contrast after rendering. The final paper panel contains four BF16 open VLMs and Gemini 2.5 Flash under one frozen prompt; exact runtime provenance is recorded per run and is not treated as an experimental factor.

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

The paper-facing V3 matrix is complete for Qwen3.5 27B BF16, Qwen3.6 27B BF16,
Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, and Gemini 2.5 Flash. Read the
single consolidated interpretation and tables in
[`reports/v3/ALL_RESULTS.md`](reports/v3/ALL_RESULTS.md). The V2 and 9B summaries
below are retained only as historical context.

The main run is complete with 9,000/9,000 parsed predictions. The strongest main condition is `direct_image` (ASR 32.5%, severity drop 0.576), followed by `direct_joint` (30.5%, 0.422). Misleading image and joint conditions reach 23.5% and 26.1% ASR, respectively. Benign controls produce much smaller effects and are used to separate ordinary content sensitivity from adversarial behavior.

The full tables, ablations, confidence intervals, error analysis, and audit materials are in [`reports/v2/`](reports/v2/), with the entry point at [`reports/v2/final_summary.md`](reports/v2/final_summary.md).

The corrected V3 Qwen 9B pilot contains 90 independent samples × 10 conditions (900/900 parsed). Clean accuracy is 53.3%, so V3 attack estimates are exploratory and use 48 clean-correct samples. Direct-image and direct-joint ASR are both 39.6% (95% Wilson CI 27.0%–53.7%); benign-image/joint instability is 12.2%. See [`reports/v3/pilot_results.md`](reports/v3/pilot_results.md).

## Corrected V3 workflow

The full V3 study is designed for a 512 GB M3 Ultra Mac Studio. The paper-facing protocol is [`configs/v3/final_analysis_protocol.yaml`](configs/v3/final_analysis_protocol.yaml), and the exact manual commands and log locations are documented in [`scripts/RUN_V3_FINAL_EXPERIMENTS.md`](scripts/RUN_V3_FINAL_EXPERIMENTS.md). External-disk export and Ubuntu restore instructions remain in [`docs/UBUNTU_DATA_TRANSFER.md`](docs/UBUNTU_DATA_TRANSFER.md).

On the Mac, MLX-VLM runs natively so it can use Metal. The version-pinned Docker container runs the research pipeline and calls that native OpenAI-compatible endpoint. An NVIDIA/vLLM Compose profile is retained as a portability path, but results from different backends must not be pooled in the primary comparison.

```bash
scripts/setup_macos.sh
bash scripts/run_v3_final_experiments.sh --list
bash scripts/run_v3_final_experiments.sh --dry-run
bash scripts/run_v3_final_experiments.sh
```

The final runner uses only complete checkpoints already present in the local cache, loads one model at a time, records the exact model ID and precision, resumes completed work, and never downloads a missing model. Qwen 9B and quantized runs remain historical. The untouched 720-image clean result is reported first without a pass/fail threshold; the fixed conditional robustness matrix uses each model's explicitly counted clean-correct mild/severe decisions.

The 720-image main set is a custom class-balanced paired robustness cohort, not CrisisMMD's published 529-image test split. Dataset counts, duplicate checks, selection behavior, and the paper-facing interpretation are audited in [`reports/v3/dataset_protocol_audit.md`](reports/v3/dataset_protocol_audit.md). Build the ignored local clean manifests, inspect the queue, and then launch it manually:

```bash
.venv-mac/bin/python -m src.v3_dataset_protocol build
scripts/run_v3_clean_benchmarks.sh --dry-run \
  --model qwen27 --model mistral --model qwen32_8bit
scripts/run_v3_clean_benchmarks.sh --cohort both \
  --model qwen27 --model mistral --model qwen32_8bit
```

This secondary queue evaluates all 3,474 locally valid severity records under their natural distribution and the exact published 529-row test split, clean-only. It reports duplicate-cluster bootstrap intervals, event/event-by-class metrics, leave-one-event-out sensitivity, and exact-SHA label-conflict sensitivity. It uses port 8094 by default, supports the larger Qwen aliases listed by `--help`, resumes completed predictions, never downloads checkpoints, and stops only the server PID it starts.

V3 splits, payloads, frozen V4/P5 prompt, and attack images are immutable for the final run. The commands below are retained only for pipeline reproduction and validation; do not regenerate artifacts during paper-facing inference.

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

After pilot artifact validation succeeds, generate and validate the remaining splits:

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
