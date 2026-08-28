# V3 full-study TODO

This is the execution checklist for the paper dataset and multi-model study. Do not change the frozen prompt, V3 splits, payloads, renderer, or metric definitions after production inference starts.

## P0 — freeze before transfer

- [x] Build leakage-resistant V3 splits and generated attacks.
- [x] Validate 9,900 condition rows and 6,480 visual-condition rows with zero failures.
- [x] Create tweet-redacted public split index and human-review templates.
- [ ] Commit the current V3 code/config/report state and tag it `v3-data-freeze`.
- [x] Add `scripts/freeze_v3_artifacts.py` to record and verify SHA-256 hashes for the prompt, configs, splits, and full condition manifest.
- [ ] Re-run `python scripts/freeze_v3_artifacts.py freeze` immediately before the first qualified full-set run, commit the resulting lock, and then use `check` before every model.
- [ ] Copy the ignored `data/v3/`, `data/raw/`, and processed source files to the Mac through encrypted/local storage; do not push tweet text or images to public GitHub.
- [ ] Verify the copied files against the recorded SHA-256 manifest.

## P1 — Mac Studio environment

- [ ] Confirm native `arm64` Python 3.12 and current macOS.
- [ ] Run `scripts/setup_macos.sh` and save package versions.
- [ ] Build the pipeline image with `docker compose -f docker/compose.mac.yml build`.
- [ ] Start native MLX-VLM with `scripts/start_v3_mlx.sh`; ordinary Linux containers are not the Metal runtime.
- [ ] Confirm `/v1/models`, one-image smoke test, JSON parsing, and deterministic repeat test (same request five times).
- [ ] Reserve at least 180 GB model-cache space and keep at least 15% free disk.

## P2 — lock and clean-screen models

For every clean-screen candidate in `configs/v3/models.yaml`:

- [ ] Accept any gated model license explicitly (Gemma entries).
- [ ] Run `python -m src.model_registry lock --slug SLUG --platform mac` before downloading/running.
- [ ] Save model ID, immutable Hub SHA, MLX-VLM version, precision, prompt hash, macOS version, chip, RAM, and server arguments.
- [ ] Run a one-image vision smoke test.
- [ ] Run five identical deterministic requests; investigate any label disagreement.
- [ ] Run the frozen V4 prompt on the 180-sample balanced prompt-validation screen; stop below 60% accuracy, 55% macro-F1, 40% minimum class recall, or 99.5% parse rate.
- [ ] For screen passers, run only the 720-sample main clean condition; stop below 70% accuracy, 65% macro-F1, 50% minimum class recall, or 99.5% parse rate.
- [ ] Publish every clean-screen result, including rejected models; do not select on attack metrics.
- [ ] Set `V3_RUN_ATTACKS=1` only for models passing both gates.

## P3 — production inference

Run models sequentially; never keep multiple large checkpoints resident merely because 512 GB unified memory is available.

- [ ] Gemma 4 12B 8-bit — full V3 matrix only if qualified.
- [ ] Mistral Small 3.1 24B 8-bit — full V3 matrix only if qualified.
- [ ] Gemma 4 26B-A4B 8-bit — full V3 matrix only if qualified.
- [ ] Qwen3.5 27B 8-bit — full V3 matrix only if qualified.
- [ ] Gemma 4 31B 8-bit — full V3 matrix only if qualified.
- [ ] Qwen3-VL 32B 8-bit — full V3 matrix only if qualified.
- [ ] Qwen3-VL 235B-A22B 4-bit — ultra-large full V3 matrix only if qualified.
- [ ] Qwen3.5 397B-A17B 4-bit — ultra-large full V3 matrix only if qualified.
- [ ] Resume with the same run ID after interruptions; never delete an inference cache during production.
- [ ] Verify 9,180 parsed predictions per qualified model (or explicitly record every failure/retry).
- [ ] Back up completed run folders after each model.

Example per model:

```bash
V3_MODEL_ID=mlx-community/Qwen3.5-27B-8bit scripts/start_v3_mlx.sh

VLM_BASE_URL=http://127.0.0.1:8080/v1 \
V3_CONCURRENCY=1 \
scripts/run_v3_model.sh qwen35_27b_8bit
```

Raise concurrency only after a 100-request stability test. Record the final value; do not change it within a model run.

## P4 — sensitivity studies

- [ ] Qwen3.5 27B BF16 vs 8-bit vs 4-bit on prompt-validation + main, only if its 8-bit candidate qualifies.
- [ ] Report the 235B/397B 4-bit ultra tier separately; do not interpret its contrast with 8-bit standard models as a pure size effect.
- [ ] Near-duplicate threshold sensitivity at dHash Hamming 2/4/6 without reusing those alternative splits for the primary result.
- [ ] Minimum-image-side sensitivity at 96/128/224 px.
- [ ] Natural-prevalence reweighting in addition to balanced macro metrics.
- [ ] Exclude any human-rejected overlays and report both intent-to-treat and review-passed estimates.

## P5 — human review

- **Status:** OPEN submission-quality task. The numerical main, style, and size
  results remain valid without this review; however, it is required before
  claiming human readability, plausibility, camouflage/stealth, or absence of
  critical-damage occlusion.
- **Materials:** use the blinded gallery
  [`reports/v3/manual_review/final_visual_review.html`](../reports/v3/manual_review/final_visual_review.html),
  the blank 303-row instrument
  [`final_visual_review.csv`](../reports/v3/manual_review/final_visual_review.csv),
  and the protocol
  [`PROTOCOL.md`](../reports/v3/manual_review/PROTOCOL.md). The gallery omits
  model outputs and tweet text.
- [ ] Freeze the exact reviewer scope before ratings begin; do not add/remove
  rows after seeing ratings.
- [ ] Collect two independent, pseudonymous reviewer passes, blinded to model
  predictions, covering readability, attack-semantic visibility, presentation
  plausibility, critical-damage obscuration, image usability, and whether the
  original damage remains judgeable.
- [ ] Use `yes`, `no`, or `uncertain`; never auto-fill human labels.
- [ ] Calculate raw agreement and Cohen's kappa for two reviewers (or
  Krippendorff's alpha for more), then adjudicate disagreements only after the
  independent passes.
- [ ] Report the adjudicated acceptance rate by review group/style/size. If
  this work is not completed, retain the digital style/size results but remove
  perceptual-realism and non-occlusion claims from the manuscript.

## P6 — final analysis

- [ ] Compute clean accuracy, macro-F1, per-class metrics, confusion matrices, ASR, targeted ASR, severity drop, induced under-triage, and Wilson/bootstrap intervals.
- [ ] Compare each attack with its modality-matched benign control using paired tests.
- [ ] Estimate model-family and model-size effects; size claims must use within-family Qwen and Gemma contrasts.
- [ ] Fit sample/event/model-aware mixed or hierarchical models; do not treat the qualified models' condition rows as independent.
- [ ] Correct multiple comparisons and retain exact denominators.
- [ ] Produce event, damage-class, style, size, payload, model-family, and precision subgroup tables.
- [ ] Build model-by-condition robustness heatmaps and confidence-interval plots.

## P7 — paper and release

- [ ] Separate confirmatory claims from pilot/exploratory findings.
- [ ] Document the weak Qwen 9B clean baseline as a secondary result.
- [ ] Include threat model, ethical use, dataset terms, limitations, and human-review protocol.
- [ ] Add `CITATION.cff`, dataset/model citations, environment locks, and model-card SHAs.
- [ ] Run privacy scan; public artifacts must contain no tweet text.
- [ ] Commit aggregate reports only; keep raw data, generated images, model weights, predictions, and caches out of public Git.
- [ ] Tag the final reproducible release.
