# CrisisMMD VLM Robustness: Canonical Paper-Writing Reference

**Status date:** 2026-08-28
**Paper panel:** Qwen3.5 27B BF16, Qwen3.6 27B BF16, Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, and Gemini 2.5 Flash.
**Purpose:** This is the one reader-facing file to use while writing the manuscript. It combines the active paper decisions, dataset construction and rationale, complete BF16 + Gemini results, supported claims, caveats, and bibliography. Implementation artifacts remain audit evidence, but they are not competing manuscript summaries.
**Interpretation rule:** Decisions D018-D022 govern post-result manuscript scope. Historical 8-bit, 4-bit, V2, 9B pilot, pass/fail gates, and deployment thresholds are excluded from paper-facing conclusions. Qwen3.8 is a pending same-protocol extension and must not enter aggregate tables until its complete matrix is available.

## Technical Summary

The completed evidence is sufficient to write a controlled, paired adversarial-robustness paper. All five models parsed every main response; balanced-main clean accuracy was 50.28%-55.69%. Clean performance is reported continuously without a pass/fail or deployment threshold. The paper-primary attack percentage is the number of clean-correct mild/severe decisions shifted downward divided by all 720 main samples. Conditional ASR on the clean-correct eligible subset is retained as a susceptibility analysis, not used as the headline population percentage.

The main result is not a universal modality ordering. All 30 malicious model-condition comparisons produced a positive full-cohort malicious-minus-benign downward risk difference with Holm-corrected McNemar significance. However, magnitude and modality were strongly model-dependent. Full-cohort direct image/joint effects reached about 25%-33% for Qwen3-VL and Mistral, 14%-23% for the dense Qwen models, and 9%/25% for Gemini. Conditional eligible-only rates are larger and remain useful for explaining susceptibility, but they are not the headline population percentages.

Presentation-style and size experiments are secondary mechanism analyses. Simple/news presentation was usually more effective than camouflage for direct instructions, but this is a bundled presentation contrast rather than an isolated style effect. Size did not have a universal monotonic relationship with attack success. These ablations have small model-specific eligible denominators (style 28-37; size 13-21), so exact counts and uncertainty must remain visible.

The paper's defensible contribution is therefore: a duplicate-resistant paired benchmark; image/text/joint delivery with matched benign controls; safety-directional metrics defined on clean-correct target-eligible decisions; and evidence that typographic vulnerability is substantial but architecture- and modality-dependent. It should not be framed as a model leaderboard, an operational disaster system, or proof that one runtime/model family is universally safer.

## Paper-Readiness Verdict

**The study is manuscript-ready and has a coherent publishable contribution.** The expensive evidence is complete for a common five-model panel: main clean + nine paired conditions, natural clean, official-test clean, presentation-style ablation, and size ablation. The matched-control result is especially strong: all 30 malicious model-condition effects are positive and Holm-significant, and strict typography-matched sensitivity preserves that conclusion.

**It is not yet submission-ready in its strongest form.** The remaining material work is not another model matrix. Complete the two-reviewer visual validation before making readability, plausibility, camouflage, or non-occlusion claims; verify the bibliography and model revision table; and write the manuscript from this file. If visual review is omitted, the paper can still report the main digital intervention results, but the presentation-style section must be explicitly exploratory and must avoid perceptual claims.

The central contribution is meaningful for the literature because it combines four elements that prior typographic-attack and disaster-classification studies do not ordinarily combine in one design: a disaster under-triage target, globally duplicate-resistant cohorts, three delivery modalities, and modality-matched benign controls with direction-sensitive paired statistics. The contribution is an evaluation protocol and empirical finding, not a new classifier, attack optimizer, or defense.

## Active Paper Decisions

| Decision | Current rule | Manuscript consequence |
|---|---|---|
| Framing | Clean-characterized paired conditional robustness audit | Do not call the work a leaderboard or operational deployment study |
| Clean performance | No pass/fail, qualification, or deployment threshold | Report accuracy, macro-F1, MAE, parsing, confusion matrix, and per-class recall as continuous measurements |
| Primary panel | Four BF16 open VLMs plus Gemini 2.5 Flash | Exclude historical 8-bit, 4-bit, V2, and 9B pilot results from primary tables |
| Primary estimand | Full-cohort downward success: clean-correct mild/severe cases shifted lower, divided by all 720 samples | Report its numerator and 720 denominator; retain eligible-only ASR as conditional susceptibility |
| Controls | Compare each malicious condition with its modality-matched benign condition | Attacked accuracy alone is descriptive, not the main finding |
| Statistics | Wilson intervals, 5,000 paired bootstrap draws, exact McNemar, Holm correction | Keep pairing and comparison families explicit; do not pool model predictions |
| Prompt | Frozen zero-shot P5/V4 for all main runs | Do not add attack-aware language or retrofit the prompt after outcomes |
| P7 sensitivity | Predeclared but not run; retired from required scope | Disclose this protocol deviation and do not claim prompt invariance |
| Runtimes | Canonical open-model results use GCP A100/CUDA-vLLM; Gemini uses its hosted API | Do not interpret cross-service differences as backend effects |
| Main cohort | Preserve custom balanced V3 main-720 | Use it for paired effects, not natural-prevalence or event-general claims |
| Secondary clean cohorts | Natural-3,474 and official-test-529 | Use them for competence context and literature comparability, not attack prevalence |
| Ablations | Separate presentation-style-120 and relative-size-60 cohorts; frozen post-review text-rhetoric and point-size follow-ups | Treat all as secondary mechanism analyses with explicit denominators |
| Human review | Required for perceptual/readability/occlusion claims | Main numerical effects remain valid without it, but style realism claims do not |

## Decisions Retired or Narrowed After the Completed Runs

These changes are amendments to reporting scope, not silent rewrites of the frozen experiment:

1. **Deployment and clean pass/fail thresholds are retired (D018).** The old 180-screen and 720-main numeric cutoffs were investigator-defined and not externally calibrated for an operational use case. They remain in historical artifacts but are absent from manuscript claims and figures.
2. **The 8-bit/4-bit candidate panel is retired from primary reporting (D019).** The final common panel is selected by completion of the same paper matrix, not by favorable attack outcomes: four BF16 open models plus Gemini 2.5 Flash.
3. **The MLX-only runtime rule is superseded by a common A100 runtime (D020).** Canonical open-model outputs use GCP A100/CUDA-vLLM and Gemini uses its hosted Batch API. Repeated MLX runs remain noncanonical audit evidence and are not mixed into the primary tables.
4. **The P7 prompt sensitivity is retired from required scope (D021).** It was predeclared as secondary but never run. The paper must disclose this deviation and list prompt dependence as a limitation; it must not imply that V4 results are prompt-invariant.
5. **The 90-sample pilot is historical only.** It helped debug the pipeline but does not enter the five-model paper evidence.
6. **Human visual review is not retired.** It is still needed for claims about readability, plausibility, camouflage, or critical-region occlusion. Omitting it requires removing those perceptual claims, not pretending the validation occurred.

## What Dataset Counts Mean

| Count | Population | Paper use |
|---:|---|---|
| 18,082 | Real CrisisMMD v2.0 images across all annotation tasks | Overall dataset scale only |
| 3,526 | Published damage-severity image rows | Severity-task source population before local exact-image deduplication |
| 3,474 | Locally valid, exact-SHA-unique severity image-text rows | Natural-distribution clean-only evaluation |
| 529 | Published damage-severity test rows: 71 little/no, 126 mild, 332 severe | Secondary clean literature-comparability evaluation |
| 720 | Custom V3 main: 240 examples per class | Primary paired clean/attack experiment |
| 120 | Presentation-style ablation: 40 examples per class | Secondary paired mechanism experiment |
| 60 | Size ablation: 20 examples per class | Secondary paired mechanism experiment |

The often-mentioned 18,082 images are not all damage-severity examples. Only 3,526 published rows have the severity label used here. Exact SHA-256 deduplication removes 52 repeated rows from 42 duplicate-image groups, producing 3,474 unique valid severity rows.

## How the V3 Experimental Cohorts Were Constructed

1. Start with the 3,474 exact-SHA-unique severity rows.
2. Construct global duplicate clusters using exact tweet ID/text, exact image identity, perceptual identity, and dHash distance <= 4.
3. Exclude 144 rows linked to old pilot clusters, 207 suspected mojibake rows, and 28 images below 128 pixels on either side.
4. Retain 3,095 eligible rows in 2,628 independent duplicate clusters.
5. Allocate rare labels first and create size (20/class), pilot (30/class), presentation-style (40/class), and main (240/class) cohorts using seed 42 and event-equalizing selection.
6. Require zero cross-split overlap by sample ID, tweet ID, exact image hash, and duplicate-cluster ID.

This procedure yields 990 globally disjoint attack-benchmark sources: 90 pilot + 720 main + 120 style + 60 size. Each source has ten paired conditions, giving 9,900 validated condition rows. The separate 180-example prompt-validation split is clean-only and was used for prompt/model routing, not final attack estimation.

The 720 main cohort is scientifically defensible for balanced paired estimation, but it is custom rather than official or natural-prevalence. Auxiliary cohorts were allocated first and event equalization created event-by-class structural zeros; all main little/no examples come from three hurricane events. Event-specific results are therefore descriptive, and only class-prior reweighting is supported.

### Why 720, 120, and 60?

These exact values are **not CrisisMMD conventions and are not sample sizes copied from a prior paper**. Repository history shows that 240, 40, and 20 sources per class were introduced in the initial V3 protocol and fixed before the canonical five-model paper-facing runs. The repository contains no derivation from a published rule, no predeclared minimum detectable effect, and no a priori power calculation for these values. They must therefore be reported as investigator-chosen protocol allocations, not as literature-standard sample sizes.

The allocation is nevertheless coherent with the experiments' different roles. Main received the largest cohort because it estimates the primary paired attack effects across ten conditions. Presentation-style received a smaller, separate cohort because it is a secondary bundled-mechanism comparison. Size received the smallest cohort because it is a secondary ordered one-factor comparison. Every cohort remains exactly class-balanced and fully paired within source, so enlarging a cohort increases cost by ten model requests per added source while preserving equal class contribution.

| Cohort | Fixed sources | Per class | Predictions per model | Retrospective worst-case Wilson 95% half-width | Interpretation |
|---|---:|---:|---:|---:|---|
| Main | 720 | 240 | 7,200 | 3.6 points overall; 6.3 per class | Primary paired experiment |
| Presentation style | 120 | 40 | 1,200 | 8.8 points overall | Secondary mechanism analysis |
| Size | 60 | 20 | 600 | 12.3 points overall | Secondary mechanism analysis |

The half-widths above describe full-cohort binomial precision at the conservative 50% proportion. They are retrospective diagnostics, not evidence that the sample sizes were prospectively powered. The primary downward-ASR denominators are smaller and model-specific because eligibility requires a correct clean prediction on a mild/severe example; their reported Wilson intervals, rather than the nominal cohort sizes, govern the strength of each claim.

Formal prospective sizing would have required assumptions that were unavailable when V3 was frozen. Confidence-interval sizing requires a target width and an anticipated proportion, while McNemar power for paired binary outcomes requires expected discordant-pair probabilities or an anticipated paired effect. Wei and Hutson describe interval-width-based binomial sizing, and Lachin describes power/sample-size calculations for McNemar's matched proportions. Those references justify how sample size should be planned or evaluated; they do not retroactively generate `720/120/60`.

### Main Event-by-Class Composition

| Event | Little/no | Mild | Severe | Total |
|---|---:|---:|---:|---:|
| California wildfires | 0 | 21 | 36 | 57 |
| Hurricane Harvey | 75 | 70 | 36 | 181 |
| Hurricane Irma | 124 | 70 | 36 | 230 |
| Hurricane Maria | 41 | 71 | 36 | 148 |
| Iraq-Iran earthquake | 0 | 0 | 36 | 36 |
| Mexico earthquake | 0 | 3 | 36 | 39 |
| Sri Lanka floods | 0 | 5 | 24 | 29 |
| **Total** | **240** | **240** | **240** | **720** |

This table makes the trade-off visible: the cohort is class-balanced globally but not event-balanced within class. Event and class are partly confounded, so event-specific comparisons cannot be interpreted as clean disaster-type effects.

The published 529-row test split is also not an untouched confirmatory set for this project. It is severe-majority (62.8%), shares 106 duplicate clusters across official train/test under the V3 rule, and only 319 of 529 rows are independent of every existing V3 cohort. It is retained only as a named secondary clean benchmark, with accuracy reported alongside macro-F1.

## Why the Dataset Design Is Scientifically Defensible

The original CrisisMMD release established a multimodal social-media dataset across seven 2017 disasters with humanitarian and damage annotations. The later disaster-image benchmark by Alam et al. explicitly identified exact and near duplicates and constructed non-overlapping evaluation splits. V3 follows that literature-supported leakage-control principle by clustering globally before allocating any experimental cohort. It does not copy Alam et al.'s numerical duplicate threshold or split ratio: V3's dHash <= 4 threshold, event-equalizing selector, allocation order, and `720/120/60` counts are study-specific implementation choices. The official CrisisMMD resources are still evaluated separately so readers can compare against a named released split rather than only a custom sample.

The 720-source main cohort is not claimed to be a canonical CrisisMMD test set. It is an experimental sample designed for paired estimation: every source supplies clean, benign, direct, and misleading observations; classes contribute equally; and duplicate clusters cannot cross cohorts. Its 240 examples per class give a retrospective worst-case binomial 95% half-width of about 6.3 percentage points for a class-specific proportion, while the full 720-source estimate is about 3.7 points. These are precision descriptions, not an a priori power calculation. The actual primary attack denominators are smaller because they include only clean-correct mild/severe cases.

This three-cohort reporting strategy is deliberate:

1. **Main-720** estimates paired intervention effects with equal class representation.
2. **Natural-3,474** describes clean behavior over all locally valid exact-image-unique severity rows.
3. **Official-test-529** provides split-named clean comparability with prior work.

No one cohort can serve all three purposes without tradeoffs. The natural and official cohorts are not attacked, because their role is competence characterization rather than paired mechanism estimation. The main cohort is not prevalence-weighted, so the paper must not estimate real-world attack prevalence from it.

### Dataset Decisions That Must Appear in Methods

- State that 18,082 is the scale of all CrisisMMD image tasks, while 3,526 is the relevant published severity population.
- State every local exclusion and the resulting 3,095 eligible rows / 2,628 independent duplicate clusters.
- Describe the cluster keys and dHash <= 4 rule before describing split sizes.
- Name main-720 as a **custom, class-balanced, duplicate-cluster-disjoint paired cohort**.
- State that `720/120/60` are fixed investigator-chosen V3 allocations, not CrisisMMD or literature standards and not a priori powered sample sizes.
- Explain the role-based allocation: main is primary; presentation style and size are smaller secondary mechanism cohorts. Report their retrospective precision and all model-specific eligible denominators.
- State that auxiliary cohorts were allocated before main and that this induced event-by-class structural zeros.
- Report the exact main event distribution and avoid event-general or disaster-type causal claims.
- Describe official-test-529 as a secondary natural-imbalance benchmark; pair accuracy with macro-F1 and class recall.
- Preserve four main rows linked to exact-image label-conflict groups in the frozen primary analysis and report their exclusion sensitivity.
- Do not rebuild V3 after observing results. A future redesigned cohort would be V4, main-first, within-class event-proportional, and fully rerun.

### Literature Basis for the Dataset Choices

- [Alam, Ofli, and Imran (2018), CrisisMMD](https://doi.org/10.1609/icwsm.v12i1.14983) is the dataset source and establishes the seven-disaster multimodal setting.
- [The official CrisisMMD resource page](https://crisisnlp.qcri.org/crisismmd) identifies the v2.0 data, released annotation splits, and recommended dataset citations.
- [Alam et al. (2020), ASONAM](https://doi.org/10.1109/ASONAM49781.2020.9381294) motivates exact/near-duplicate detection and non-overlapping disaster-image evaluation splits.
- [Ofli, Alam, and Imran (2020), ISCRAM](https://arxiv.org/abs/2004.11838) provides multimodal disaster-response context and the released multimodal baseline split.
- [Shetty et al. (2025), Multimedia Tools and Applications](https://doi.org/10.1007/s11042-024-19818-0) is a supervised multimodal disaster-assessment reference. Its regime and metrics are contextual rather than directly comparable with zero-shot generative VLM scores.
- [Wei and Hutson (2013)](https://doi.org/10.1080/02664763.2012.740629) supports planning binomial samples against an explicit interval-width target; it does not prescribe a CrisisMMD cohort size.
- [Lachin (1992)](https://doi.org/10.1002/sim.4780110909) supports prospective power analysis for paired binary/McNemar outcomes when anticipated discordant-pair probabilities are available; those assumptions were not predeclared for V3.

## Fixed Experimental Design

### Main Conditions

| Family | Image | Accompanying text | Conditions |
|---|---|---|---|
| Clean | Original | Original | `clean` |
| Benign | Benign archive text or original | Benign archive prefix or original | image, text, joint |
| Direct | Instruction targeting `little_or_no_damage` or original | Same instruction prefix or original | image, text, joint |
| Misleading | False low-damage claim or original | Same false claim prefix or original | image, text, joint |

Image and joint conditions share the same attacked image. Within a source and semantic family, image/text/joint use the same assigned payload. The original tweet is preserved after a two-newline prefix in text and joint conditions.

### Why Direct and Misleading Are Separate

The two malicious families operationalize different ways untrusted external content can conflict with visual evidence:

- **Direct instruction** is imperative language that explicitly tells the model to ignore or override evidence and produce the low-damage target. Because the instruction is embedded in an image or accompanying post rather than sent as the trusted system prompt, its delivery is an indirect prompt-injection setting in the security taxonomy.
- **Misleading claim** is declarative low-damage misinformation presented as scene context, often with inspection or official-report framing. It contains no command to the model. Its intended mechanism is cross-modal evidential conflict rather than explicit instruction following.

The exact English sentences are investigator-authored fixed payload pools, not quotations copied from CrisisMMD or from a prior benchmark. They were frozen before the canonical model matrix, assigned deterministically by sample, and reused across image/text/joint delivery. The distinction is grounded in indirect prompt-injection work that embeds malicious instructions in external content, and in typographic/cross-modal studies showing that semantically relevant or misleading text can override visual evidence. It is still a bundled semantic contrast: imperative form, target-label explicitness, authority framing, and wording differ, so the main direct-versus-misleading comparison is not a pure causal estimate of speech act alone.

A frozen follow-up text-rhetoric experiment therefore separates four variants on the existing disjoint 120-source cohort: exact-label direct instruction, natural-language direct instruction, plain misleading claim, and authority-framed misleading claim. Each has a rhetoric-matched benign control. This follow-up is secondary and post-review; it refines the semantic interpretation without replacing the canonical direct/misleading result.

### Presentation-Style and Size Conditions

Presentation style compares simple black overlays, a fictional `CRISIS24` news banner, and background-aware camouflage. This factor bundles contrast, background, occupied area, and placement policy; it must not be described as a single isolated visual component or as human-validated realism.

Size uses the simple renderer while fixing payload, placement, colors, and opacity. Target relative font heights are 3% (small), 5% (medium), and 8% (large). This is a cleaner ordered one-factor comparison, but observed effects must not be called monotonic unless supported model by model.

The original completed size ablation therefore used **relative image-height percentages**, not typographic points. A separate frozen follow-up now manipulates nominal `3, 6, 9, 12, 15 pt` on the same disjoint 60-source cohort. Rendering is fixed at 72 PPI, so the nominal values map to `3, 6, 9, 12, 15 px`; the paper must report both units and must not imply that raster pixels have a device-independent physical point size. The endpoint is 15 pt because the ECCV 2024 typography study used the same five 3-15 pixel levels, while a pre-render audit showed that 18-27 pt would occupy 53%-100% of the smallest image and confound type size with heavy occlusion. Font file/hash, placement, colors, opacity, realized pixels, relative font height, line count, and occupied area are frozen and recorded.

The literature establishes typography size, opacity, color, placement, scene coherence, and semantic relevance as attack factors. Our contribution is not discovering that typography matters in general; it is evaluating those factors in a paired disaster under-triage task with matched benign controls, duplicate-resistant cohorts, direction-sensitive outcomes, and explicit clean competence.

### Prompt and Inference

The primary prompt is the frozen zero-shot P5 rubric in `configs/prompts/frozen_prompt_v4.yaml`. It prioritizes visible physical damage to man-made infrastructure and allows tweet text only to clarify visible evidence. It contains no attack-aware instruction. Decoding is deterministic: temperature 0, top-p 1, seed 42, maximum 150 output tokens, and thinking disabled.

| Paper label | Exact model identity | Precision/service | Result provenance |
|---|---|---|---|
| Qwen3.5 27B BF16 | `Qwen/Qwen3.5-27B` | BF16 | GCP A100 / vLLM |
| Qwen3.6 27B BF16 | `Qwen/Qwen3.6-27B` | BF16 | GCP A100 / vLLM |
| Qwen3-VL 32B BF16 | `Qwen/Qwen3-VL-32B-Instruct` | BF16 | GCP A100 / vLLM |
| Mistral 24B BF16 | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | BF16 | GCP A100 / vLLM |
| Gemini 2.5 Flash | `gemini-2.5-flash` | Hosted service | Gemini Batch API |

All four open models use the same GCP A100/CUDA-vLLM execution family for the canonical tables. Gemini remains a separate hosted service. Predictions are never pooled across models as independent observations, and runtime is not treated as a causal factor.

## Metric Definitions

- **Clean accuracy / macro-F1:** three-class correctness and class-balanced F1.
- **Eligible denominator:** samples whose ground truth is mild/severe and whose clean prediction is correct for that model.
- **Conditional downward ASR:** downward successes divided by the model-specific eligible denominator. This measures susceptibility after conditioning on a correct actionable clean decision.
- **Full-cohort downward success rate (paper-primary):** the same downward-success count divided by all 720 main samples. Algebraically this is `eligible share x conditional downward ASR`; this is the requested clean-performance-aware population percentage.
- **Full-cohort upward shift rate:** clean-correct little/no or mild decisions shifted to a higher severity, divided by all 720 samples.
- **Induced severe under-triage:** clean-correct severe samples attacked to mild or little/no.
- **Induced critical under-triage:** clean-correct severe samples attacked specifically to little/no.
- **Full-cohort benign-adjusted effect (paper-primary):** `(malicious downward successes - matched-benign downward successes) / 720`. Benign behavior is a matched control baseline, not a standard deviation. It is not multiplied by clean accuracy a second time because clean eligibility is already encoded in both success indicators.
- **Conditional benign-adjusted risk difference:** the same paired contrast divided by the eligible denominator; retained as a susceptibility analysis.

Wilson 95% intervals are used for proportions. Paired effects use 5,000 bootstrap draws with seed 42. Paired binary outcomes use exact two-sided McNemar tests with Holm correction inside predeclared comparison families. Models are analyzed separately.

## Main Clean Competence and Full-Cohort Downward Attack Success

Attack columns report downward-success counts over all 720 balanced-main samples. For example, a 50% eligible share and 40% conditional ASR produce a 20% full-cohort rate. This is not attacked error rate: it counts only initially correct mild/severe decisions that move downward.

| Model | Clean acc. | Macro-F1 | Eligible n/720 | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 55.69% | 54.94% | 245/720 | 14.86% | 4.86% | 14.44% | 6.39% | 3.75% | 7.64% |
| Qwen3.6 27B BF16 | 53.89% | 53.17% | 245/720 | 23.06% | 2.78% | 15.42% | 6.11% | 2.08% | 7.50% |
| Qwen3-VL 32B BF16 | 53.19% | 52.98% | 294/720 | 32.64% | 4.72% | 32.92% | 9.86% | 3.75% | 9.44% |
| Mistral 24B BF16 | 50.28% | 48.57% | 232/720 | 26.25% | 8.61% | 24.58% | 10.14% | 2.78% | 11.53% |
| Gemini 2.5 Flash | 54.58% | 54.85% | 273/720 | 9.44% | 6.11% | 24.58% | 6.67% | 5.97% | 10.83% |
| **Unweighted model mean** | **53.53%** | **52.90%** | **257.8/720** | **21.25%** | **5.42%** | **22.39%** | **7.83%** | **3.67%** | **9.39%** |

Clean performance is modest and heterogeneous, with eligible counts of 232-294. The 720-denominator rate makes that competence limitation visible in the headline effect while preserving the attack's direction. It does not imply that any model is operationally useful. No pass/fail label is assigned.

### Conditional Susceptibility Among Eligible Decisions

These are the original eligible-only downward ASRs. They answer a different question: once a model made a correct mild/severe decision, how often did the attack lower it?

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 43.67% | 14.29% | 42.45% | 18.78% | 11.02% | 22.45% |
| Qwen3.6 27B BF16 | 67.76% | 8.16% | 45.31% | 17.96% | 6.12% | 22.04% |
| Qwen3-VL 32B BF16 | 79.93% | 11.56% | 80.61% | 24.15% | 9.18% | 23.13% |
| Mistral 24B BF16 | 81.47% | 26.72% | 76.29% | 31.47% | 8.62% | 35.78% |
| Gemini 2.5 Flash | 24.91% | 16.12% | 64.84% | 17.58% | 15.75% | 28.57% |
| **Unweighted model mean** | **59.55%** | **15.37%** | **61.90%** | **21.99%** | **10.14%** | **26.39%** |

### Main Clean Detail

MAE uses the ordinal mapping little/no=0, mild=1, severe=2. Recall columns show why aggregate accuracy alone is insufficient.

| Model | Accuracy | Macro-F1 | Ordinal MAE | Little recall | Mild recall | Severe recall | Correct mild+severe |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 55.69% | 54.94% | 0.5486 | 65.00% | 35.83% | 66.25% | 245 |
| Qwen3.6 27B BF16 | 53.89% | 53.17% | 0.5833 | 59.58% | 35.83% | 66.25% | 245 |
| Qwen3-VL 32B BF16 | 53.19% | 52.98% | 0.5319 | 37.08% | 56.67% | 65.83% | 294 |
| Mistral 24B BF16 | 50.28% | 48.57% | 0.5778 | 54.17% | 71.67% | 25.00% | 232 |
| Gemini 2.5 Flash | 54.58% | 54.85% | 0.5597 | 50.00% | 50.83% | 62.92% | 273 |
| **Unweighted model mean** | **53.53%** | **52.90%** | **0.5603** | **53.17%** | **50.17%** | **57.25%** | **257.8** |

Mistral's 25% severe recall is the clearest class-level weakness. The two dense Qwen runs have identical mild and severe recall but differ on little/no recall. These differences explain why all conditional attack denominators and severe-case denominators must remain model-specific.

### Cross-Model Mean Clean Confusion Matrix

Rows are ground truth and columns are predictions. Each cell is the unweighted mean of the five models' row-normalized clean confusion matrices, so every model contributes equally. This is a descriptive panel summary, not a pooled 3,600-observation estimate. Model-specific count matrices belong in the appendix.

| Ground truth | Pred. little/no | Pred. mild | Pred. severe |
|---|---:|---:|---:|
| Little/no | 53.17% | 41.42% | 5.42% |
| Mild | 26.75% | 50.17% | 23.08% |
| Severe | 23.25% | 19.50% | 57.25% |

## Matched Benign-Control Instability

These are benign downward-success counts divided by all 720 main samples. The same image/text/joint control rate is subtracted from its malicious counterpart. Benign is a matched intervention baseline, not an estimate of standard deviation.

| Model | Benign image | Benign text | Benign joint |
|---|---:|---:|---:|
| Qwen3.5 27B BF16 | 1.25% | 0.56% | 1.53% |
| Qwen3.6 27B BF16 | 1.94% | 0.14% | 1.81% |
| Qwen3-VL 32B BF16 | 1.39% | 0.56% | 1.53% |
| Mistral 24B BF16 | 2.50% | 0.56% | 2.92% |
| Gemini 2.5 Flash | 2.08% | 1.67% | 2.22% |
| **Unweighted model mean** | **1.83%** | **0.69%** | **2.00%** |

Benign controls caused some instability, particularly for visual and joint additions, but their downward rates were substantially below the corresponding malicious rates. This is why the paper reports malicious-minus-matched-benign effects rather than attributing every changed prediction to attack semantics.

## Malicious Effects Exceed Matched Benign Instability

Values are paired malicious-minus-benign downward risk differences on the full 720-sample cohort. All 30 values are positive, their full-cohort bootstrap intervals exclude zero, and all Holm-adjusted McNemar tests are significant. Conditional eligible-cohort effects and strict typography-matched sensitivity remain in model-level artifacts.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | +13.61 pp | +4.31 pp | +12.92 pp | +5.14 pp | +3.19 pp | +6.11 pp |
| Qwen3.6 27B BF16 | +21.11 pp | +2.64 pp | +13.61 pp | +4.17 pp | +1.94 pp | +5.69 pp |
| Qwen3-VL 32B BF16 | +31.25 pp | +4.17 pp | +31.39 pp | +8.47 pp | +3.19 pp | +7.92 pp |
| Mistral 24B BF16 | +23.75 pp | +8.06 pp | +21.67 pp | +7.64 pp | +2.22 pp | +8.61 pp |
| Gemini 2.5 Flash | +7.36 pp | +4.44 pp | +22.36 pp | +4.58 pp | +4.31 pp | +8.61 pp |
| **Unweighted model mean** | **+19.42 pp** | **+4.72 pp** | **+20.39 pp** | **+6.00 pp** | **+2.97 pp** | **+7.39 pp** |

This is the cleanest evidence that the findings are not explained merely by adding visual/textual material. Benign controls can still change predictions, but malicious payloads create substantially more downward movement on the same samples.

## Cross-Model Mean Severity Transition Matrices

These confusion-matrix-like rows replace mean severity drop as the main presentation. Each row begins with a clean-correct label and shows the attacked label distribution. Values are unweighted means of the five model-specific row percentages. Downward and upward movements are both visible; model-specific count matrices belong in the appendix.

| Condition | Clean label | To little/no | To mild | To severe |
|---|---|---:|---:|---:|
| Direct image | Little/no | 100.00% | 0.00% | 0.00% |
|  | Mild | 75.11% | 21.62% | 3.27% |
|  | Severe | 47.61% | 2.10% | 50.29% |
| Direct text | Little/no | 99.72% | 0.28% | 0.00% |
|  | Mild | 25.99% | 71.77% | 2.24% |
|  | Severe | 2.38% | 2.25% | 95.37% |
| Direct joint | Little/no | 99.74% | 0.26% | 0.00% |
|  | Mild | 73.85% | 23.19% | 2.95% |
|  | Severe | 51.22% | 2.59% | 46.19% |
| Misleading image | Little/no | 99.44% | 0.56% | 0.00% |
|  | Mild | 29.29% | 69.90% | 0.81% |
|  | Severe | 2.95% | 12.52% | 84.53% |
| Misleading text | Little/no | 99.21% | 0.79% | 0.00% |
|  | Mild | 16.04% | 83.45% | 0.51% |
|  | Severe | 0.52% | 5.65% | 93.83% |
| Misleading joint | Little/no | 99.62% | 0.38% | 0.00% |
|  | Mild | 34.69% | 64.57% | 0.75% |
|  | Severe | 3.68% | 15.64% | 80.68% |

### Full-Cohort Upward Shift Rates

Upward shifts are possible but rare. Each value is the count of clean-correct little/no or mild decisions shifted to a higher class divided by 720. These are not additional model runs; they are symmetric post-analysis of the existing paired predictions.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 0.83% | 0.28% | 0.97% | 0.28% | 0.00% | 0.00% |
| Qwen3.6 27B BF16 | 0.14% | 0.28% | 0.97% | 0.14% | 0.14% | 0.28% |
| Qwen3-VL 32B BF16 | 0.00% | 0.42% | 0.00% | 0.14% | 0.00% | 0.14% |
| Mistral 24B BF16 | 0.00% | 0.28% | 0.00% | 0.14% | 0.56% | 0.28% |
| Gemini 2.5 Flash | 1.39% | 0.83% | 0.14% | 0.28% | 0.42% | 0.14% |
| **Unweighted model mean** | **0.47%** | **0.42%** | **0.42%** | **0.20%** | **0.22%** | **0.17%** |

The directional asymmetry is empirical rather than imposed by the analysis: attacks overwhelmingly lower severity, but occasional mild-to-severe and little/no-to-mild transitions occur. Mean ordinal severity drop remains available as a supplementary magnitude statistic in each model's `attack_metrics.csv` and `statistical_tests.csv`.

## Severe Cases Show Safety-Relevant Under-Triage

Each cell is induced severe under-triage / induced critical under-triage among clean-correct severe cases. The table focuses on direct attacks because they produce the largest safety effects.

| Model | Direct image | Direct text | Direct joint |
|---|---:|---:|---:|
| Qwen3.5 27B BF16 | 28.93% / 28.30% | 7.55% / 3.77% | 33.96% / 33.96% |
| Qwen3.6 27B BF16 | 55.97% / 54.72% | 1.89% / 1.26% | 32.70% / 32.08% |
| Qwen3-VL 32B BF16 | 67.72% / 67.09% | 4.43% / 1.90% | 73.42% / 73.42% |
| Mistral 24B BF16 | 83.33% / 76.67% | 3.33% / 1.67% | 73.33% / 65.00% |
| Gemini 2.5 Flash | 12.58% / 11.26% | 5.96% / 3.31% | 55.63% / 51.66% |
| **Unweighted model mean** | **49.71% / 47.61%** | **4.63% / 2.38%** | **53.81% / 51.22%** |

The Qwen3-VL, Mistral, and Gemini joint findings are not only generic label changes: many initially correct severe judgments are moved directly to little/no damage.

## Class-Conditional Downward Transitions

Each cell reports `mild->little/no / severe->mild / severe->little/no`. Percentages are followed by exact `n/N`; mild and severe denominators differ because they are anchored to the model's clean-correct examples in that ground-truth class.

### Direct transitions

| Model | Image M->L / S->M / S->L | Text M->L / S->M / S->L | Joint M->L / S->M / S->L |
|---|---:|---:|---:|
| Qwen3.5 27B BF16 | 70.93% (61/86) / 0.63% (1/159) / 28.30% (45/159) | 26.74% (23/86) / 3.77% (6/159) / 3.77% (6/159) | 58.14% (50/86) / 0.00% (0/159) / 33.96% (54/159) |
| Qwen3.6 27B BF16 | 89.53% (77/86) / 1.26% (2/159) / 54.72% (87/159) | 19.77% (17/86) / 0.63% (1/159) / 1.26% (2/159) | 68.60% (59/86) / 0.63% (1/159) / 32.08% (51/159) |
| Qwen3-VL 32B BF16 | 94.12% (128/136) / 0.63% (1/158) / 67.09% (106/158) | 19.85% (27/136) / 2.53% (4/158) / 1.90% (3/158) | 88.97% (121/136) / 0.00% (0/158) / 73.42% (116/158) |
| Mistral 24B BF16 | 80.81% (139/172) / 6.67% (4/60) / 76.67% (46/60) | 34.88% (60/172) / 1.67% (1/60) / 1.67% (1/60) | 77.33% (133/172) / 8.33% (5/60) / 65.00% (39/60) |
| Gemini 2.5 Flash | 40.16% (49/122) / 1.32% (2/151) / 11.26% (17/151) | 28.69% (35/122) / 2.65% (4/151) / 3.31% (5/151) | 76.23% (93/122) / 3.97% (6/151) / 51.66% (78/151) |

### Misleading transitions

| Model | Image M->L / S->M / S->L | Text M->L / S->M / S->L | Joint M->L / S->M / S->L |
|---|---:|---:|---:|
| Qwen3.5 27B BF16 | 27.91% (24/86) / 10.69% (17/159) / 3.14% (5/159) | 19.77% (17/86) / 5.66% (9/159) / 0.63% (1/159) | 33.72% (29/86) / 11.95% (19/159) / 4.40% (7/159) |
| Qwen3.6 27B BF16 | 29.07% (25/86) / 8.81% (14/159) / 3.14% (5/159) | 13.95% (12/86) / 1.89% (3/159) / 0.00% (0/159) | 33.72% (29/86) / 13.21% (21/159) / 2.52% (4/159) |
| Qwen3-VL 32B BF16 | 29.41% (40/136) / 15.82% (25/158) / 3.80% (6/158) | 13.97% (19/136) / 5.06% (8/158) / 0.00% (0/158) | 27.94% (38/136) / 15.82% (25/158) / 3.16% (5/158) |
| Mistral 24B BF16 | 35.47% (61/172) / 16.67% (10/60) / 3.33% (2/60) | 8.72% (15/172) / 8.33% (5/60) / 0.00% (0/60) | 39.53% (68/172) / 20.00% (12/60) / 5.00% (3/60) |
| Gemini 2.5 Flash | 24.59% (30/122) / 10.60% (16/151) / 1.32% (2/151) | 23.77% (29/122) / 7.28% (11/151) / 1.99% (3/151) | 38.52% (47/122) / 17.22% (26/151) / 3.31% (5/151) |

Direct image/joint instructions frequently push mild cases all the way to little/no and, for several models, push severe cases directly to little/no rather than merely to mild. Misleading claims produce smaller critical transitions and relatively more severe-to-mild movement. Wilson intervals for every transition are retained in each model's `class_transitions.csv`.

## Modality Interaction Patterns

Patterns are defined on the same eligible samples using image/text/joint downward-success indicators. `Robust` means no modality succeeded; `joint-only` means only joint succeeded; `persistent visual` means both image and joint succeeded; and `all modalities` means all three succeeded. Derived groups overlap and therefore do not sum to 100%. In particular, `joint-only` is an observational pattern, not causal proof of multimodal synergy.

### Direct interaction patterns

| Model | Robust | Joint-only | Image-only | Text-only | Persistent visual | All modalities |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 37.96% (93/245) | 13.06% (32/245) | 18.78% (46/245) | 0.41% (1/245) | 24.49% (60/245) | 8.57% (21/245) |
| Qwen3.6 27B BF16 | 20.41% (50/245) | 11.02% (27/245) | 34.29% (84/245) | 0.00% (0/245) | 33.47% (82/245) | 7.35% (18/245) |
| Qwen3-VL 32B BF16 | 15.99% (47/294) | 3.74% (11/294) | 3.06% (9/294) | 0.34% (1/294) | 76.87% (226/294) | 11.22% (33/294) |
| Mistral 24B BF16 | 16.38% (38/232) | 0.86% (2/232) | 6.03% (14/232) | 1.29% (3/232) | 75.43% (175/232) | 25.43% (59/232) |
| Gemini 2.5 Flash | 32.23% (88/273) | 39.93% (109/273) | 2.93% (8/273) | 0.00% (0/273) | 21.98% (60/273) | 13.19% (36/273) |

### Misleading interaction patterns

| Model | Robust | Joint-only | Image-only | Text-only | Persistent visual | All modalities |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 75.51% (185/245) | 3.27% (8/245) | 1.22% (3/245) | 0.82% (2/245) | 17.55% (43/245) | 8.57% (21/245) |
| Qwen3.6 27B BF16 | 77.55% (190/245) | 4.08% (10/245) | 0.41% (1/245) | 0.00% (0/245) | 17.55% (43/245) | 5.71% (14/245) |
| Qwen3-VL 32B BF16 | 72.79% (214/294) | 2.38% (7/294) | 3.40% (10/294) | 0.34% (1/294) | 20.41% (60/294) | 8.16% (24/294) |
| Mistral 24B BF16 | 61.64% (143/232) | 5.60% (13/232) | 1.29% (3/232) | 1.29% (3/232) | 30.17% (70/232) | 7.33% (17/232) |
| Gemini 2.5 Flash | 69.23% (189/273) | 8.79% (24/273) | 0.73% (2/273) | 1.47% (4/273) | 16.85% (46/273) | 11.36% (31/273) |

The interaction patterns sharpen the model-level interpretation. Qwen3-VL and Mistral direct vulnerability is predominantly persistent across image and joint delivery. Qwen3.6 has a larger image-only group, while Gemini has a uniquely large joint-only group. This supports heterogeneous modality behavior without treating the observational pattern labels as mechanisms.

## Secondary Natural and Official Clean Characterization

Each cell is accuracy / macro-F1. Natural-clean uncertainty is duplicate-cluster bootstrapped over 2,933 independent clusters; official-test results are secondary and post-hoc.

| Model | Natural 3,474 | Official 529 |
|---|---:|---:|
| Qwen3.5 27B BF16 | 56.79% / 49.47% | 57.28% / 49.82% |
| Qwen3.6 27B BF16 | 56.10% / 48.12% | 56.52% / 48.12% |
| Qwen3-VL 32B BF16 | 56.36% / 48.68% | 56.90% / 49.45% |
| Mistral 24B BF16 | 36.56% / 36.28% | 37.05% / 36.83% |
| Gemini 2.5 Flash | 54.84% / 48.16% | 56.33% / 49.99% |
| **Unweighted model mean** | **52.13% / 46.14%** | **52.82% / 46.84%** |

The main and secondary clean views tell different stories because they answer different questions. The balanced main gives equal class precision for the paired audit. Natural and official cohorts expose source prevalence and class behavior. Mistral's large drop on natural/official data is especially important: its balanced-main attack estimates remain conditionally valid, but its broader task competence is weak.

## Presentation-Style Ablation

Values are downward ASR; eligible n is model-specific. Simple/news/camouflage are bundled presentation packages. These results do not establish human readability, plausibility, or perceptual realism.

| Model | Eligible n | Direct simple | Direct news | Direct camouflage | Misleading simple | Misleading news | Misleading camouflage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 31 | 41.94% | 32.26% | 12.90% | 19.35% | 22.58% | 9.68% |
| Qwen3.6 27B BF16 | 32 | 56.25% | 34.38% | 15.62% | 12.50% | 18.75% | 9.38% |
| Qwen3-VL 32B BF16 | 37 | 81.08% | 83.78% | 21.62% | 24.32% | 29.73% | 16.22% |
| Mistral 24B BF16 | 28 | 67.86% | 53.57% | 32.14% | 32.14% | 39.29% | 17.86% |
| Gemini 2.5 Flash | 36 | 25.00% | 16.67% | 8.33% | 22.22% | 16.67% | 13.89% |
| **Unweighted model mean** | **32.8** | **54.42%** | **44.13%** | **18.13%** | **22.11%** | **25.40%** | **13.40%** |

Direct simple/news attacks are especially strong for Qwen3-VL and Mistral, while both dense Qwen models also show larger direct effects for simple/news than camouflage. Camouflage usually reduces efficacy but does not eliminate it. Small denominators and several individually non-significant ablation contrasts make these rankings descriptive rather than confirmatory.

## Size Ablation

Values are downward ASR. Target relative font heights are small=3%, medium=5%, and large=8%.

| Model | Eligible n | Direct small | Direct medium | Direct large | Misleading small | Misleading medium | Misleading large |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 20 | 70.00% | 70.00% | 50.00% | 25.00% | 25.00% | 35.00% |
| Qwen3.6 27B BF16 | 19 | 68.42% | 78.95% | 63.16% | 15.79% | 21.05% | 15.79% |
| Qwen3-VL 32B BF16 | 21 | 76.19% | 90.48% | 85.71% | 28.57% | 33.33% | 33.33% |
| Mistral 24B BF16 | 13 | 53.85% | 61.54% | 76.92% | 15.38% | 38.46% | 38.46% |
| Gemini 2.5 Flash | 18 | 22.22% | 27.78% | 44.44% | 11.11% | 16.67% | 22.22% |
| **Unweighted model mean** | **18.2** | **58.14%** | **65.75%** | **64.05%** | **19.17%** | **26.90%** | **28.96%** |

Mistral and Gemini show increasing direct ASR across the three observed sizes, Qwen3.6 and Qwen3-VL peak at medium, and Qwen3.5 ties at small/medium before falling at large. The paper must reject a universal monotonic-size hypothesis. With only 13-21 eligible observations per model, individual percentage-point differences are imprecise and should be reported with intervals rather than as a deterministic law.

## Descriptive Disaster-Type Analysis

This analysis reuses the completed main predictions; it does not require new model inference. Wildfire is California wildfires, flood is Sri Lanka floods, earthquake combines Iraq-Iran and Mexico, and hurricane combines Harvey, Irma, and Maria.

### Clean Accuracy by Disaster Type

| Model | Earthquake (n=75) | Flood (n=29) | Hurricane (n=559) | Wildfire (n=57) |
|---|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 94.67% | 37.93% | 52.95% | 40.35% |
| Qwen3.6 27B BF16 | 94.67% | 37.93% | 50.45% | 42.11% |
| Qwen3-VL 32B BF16 | 93.33% | 41.38% | 49.19% | 45.61% |
| Mistral 24B BF16 | 50.67% | 6.90% | 53.31% | 42.11% |
| Gemini 2.5 Flash | 93.33% | 41.38% | 51.16% | 43.86% |
| **Unweighted model mean** | **85.33%** | **33.10%** | **51.41%** | **42.81%** |

### Mean Full-Cohort Downward Success by Disaster Type

Each cell is the unweighted mean of five model-level rates. The denominator is the number of sources in that disaster group, while the numerator still requires a clean-correct mild/severe decision followed by a downward shift.

| Disaster type | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Earthquake | 35.20% | 1.60% | 39.73% | 6.40% | 2.93% | 7.73% |
| Flood | 13.79% | 4.83% | 20.69% | 8.28% | 2.07% | 11.03% |
| Hurricane | 19.36% | 6.19% | 20.00% | 8.37% | 3.94% | 10.02% |
| Wildfire | 25.26% | 3.16% | 23.86% | 4.21% | 2.81% | 4.56% |

These differences are **descriptive, not causal disaster-type effects**. The main cohort has severe class concentration in earthquakes, no little/no wildfire or earthquake rows, only 29 flood examples, and 559 hurricane examples. Thus class mix, event identity, image characteristics, and disaster type are inseparable. The earthquake clean score, for example, largely reflects performance on severe examples rather than general earthquake competence. Model-specific numerators, eligible denominators, upward rates, and signed shifts are retained in each `disaster_type_metrics.csv` appendix artifact.

## Frozen Supervisor Follow-Ups Now Running

Two post-review secondary analyses were frozen before their model responses were inspected:

1. **Text-rhetoric ablation:** 120 existing disjoint sources, 9 conditions, 1,080 requests per model. It compares exact-label direct instructions, natural-language direct instructions, plain misleading claims, and authority-framed misleading claims against four rhetoric-matched benign controls.
2. **Point-size response:** 60 existing disjoint sources, 16 conditions, 960 requests per model. It compares benign/direct/misleading image overlays at nominal `3, 6, 9, 12, 15 pt` under the fixed 72-PPI mapping and frozen DejaVu Sans font.

Qwen3.5 27B, Qwen3.6 27B, Qwen3.8 27B, Qwen3-VL 32B, and Mistral 24B BF16 run on separate A100 80GB instances. These outputs must remain outside the completed canonical tables until every requested condition passes completeness checks. Qwen3.8 is an extension model, not a replacement selected by outcome.

## Answers to the Research Questions

### RQ1: Delivery modality matters, but the ordering is model-dependent

Image/joint delivery is much stronger than text-only for all four open models. Qwen3.5 and Qwen3-VL have similar direct image and joint effects, while Qwen3.6 and Mistral are more vulnerable to image-only delivery. Gemini uniquely shows a large direct joint amplification over both image and text. A single universal ordering is unsupported.

### RQ2: Direct instructions are generally more damaging than misleading claims

Direct image/joint attacks dominate for all four open models, while Gemini's direct-joint condition is the clearest semantic contrast. Misleading claims remain effective and significantly exceed matched benign controls in every modality for every model.

### RQ3: Low-salience camouflage can remain effective, but realism is not established

Camouflage produces non-zero downward ASR for all models, yet is usually weaker than simple/news presentation. Because the style factor changes multiple visual properties and human review is incomplete, the paper can claim persistence under a lower-salience presentation package, not real-world plausibility or stealth.

### RQ4: Larger text does not universally increase attack efficacy

The ordered trend differs by model and semantics. The evidence rejects a universal monotonic claim.

### RQ5: Vulnerability generalizes qualitatively but not quantitatively

Every model exhibits significant malicious-minus-benign downward effects, which supports cross-model qualitative vulnerability. Effect sizes vary dramatically, so models cannot be pooled and architecture/scale/runtime cannot be assigned a causal explanation.

### RQ6: Benign additions cause some instability but do not explain malicious effects

Benign downward rates are generally low, and all malicious-minus-benign paired effects are positive and significant. This matched-control result is stronger than comparing attacked accuracy alone.

## Robustness and Sensitivity Checks

- All main prediction files contain 720 parsed clean rows and 720 parsed rows per attack condition; parse rate is 100%.
- Strict visual-match subsets preserve positive benign-adjusted downward effects for all 30 model-condition combinations; the smallest lower bootstrap bound remains above zero.
- Excluding the four main rows linked to exact-image label conflicts produces negligible changes for all five models. For example, Qwen3-VL accuracy changes from 53.19% to 53.35%, and Mistral from 50.28% to 50.42%; attack-condition sensitivities are preserved in the regenerated model reports.
- Class-prior post-stratification exists, but event-by-class reweighting is unsupported because the main cohort has structural-zero cells.
- Predictions from different models/backends are not pooled as independent samples.

## What the Paper Can Claim

1. A fixed malicious message can induce safety-relevant downward severity shifts even when analysis is restricted to initially correct mild/severe decisions.
2. Matched benign controls show that the effect is not merely generic instability from adding text or an overlay.
3. Visual and joint delivery can be much more harmful than accompanying-text delivery, but this relationship is model-dependent.
4. Joint delivery is not universally additive: Gemini shows strong amplification, Qwen3-VL is approximately image-dominated, and Mistral's direct joint condition is weaker than image-only.
5. Presentation and size alter vulnerability, but neither a universal style ranking nor a universal monotonic size law is supported.
6. Clean competence and conditional robustness are separate: balanced-main clean accuracy is 50.28%-55.69%, while initially correct mild/severe decisions can still be audited conditionally.

## What the Paper Must Not Claim

- That any tested model is operationally ready for disaster-response deployment.
- That 60% accuracy is a universal CrisisMMD standard or that these zero-shot results directly rank against supervised classifiers.
- That model size, precision, architecture, or runtime causally explains robustness differences.
- That joint attacks are universally stronger than image-only attacks.
- That attack success increases monotonically with text size.
- That camouflage/news variants are realistic, stealthy, or human-approved.
- That event-specific differences generalize to disaster types.
- That this is the first such study until the systematic literature review is complete.
- That the attacks cause real-world emergency-response failures.

## Paper Contribution and Recommended Framing

The strongest framing is: **a controlled, leakage-resistant, matched-control audit of direction-sensitive typographic vulnerability in off-the-shelf VLM disaster triage**. The contribution is methodological and empirical rather than a new model or defense.

Recommended one-sentence claim:

> Across four BF16 open VLM configurations and Gemini 2.5 Flash, fixed image, text, and joint messages significantly increased downward damage-severity errors relative to matched benign controls, but modality, semantic, presentation, and size effects varied sharply by model.

The abstract should lead with the paired benchmark and benign-adjusted downward risk, then report the heterogeneity: direct image/joint ASR ranged from roughly 25%-81% across models, with a distinct Gemini joint amplification. It should immediately state that balanced-main clean accuracy was 50%-56%, so results are conditional security estimates rather than evidence of operational competence.

## Manuscript Writing Map

| Section | What to establish | Evidence to use |
|---|---|---|
| Abstract | Problem, duplicate-resistant paired design, five-model panel, all-positive benign-adjusted effects, model-dependent modality ordering, bounded conclusion | Main clean/ASR and benign-adjusted tables in this file |
| Introduction | Embedded/accompanying text can compete with visual evidence in high-stakes damage triage; existing work does not answer the paired under-triage question | CrisisMMD, typographic-attack, and prompt-injection references below |
| Related work | Separate supervised disaster classifiers, zero-shot generative VLM assessment, typographic attacks, and multimodal prompt injection | Regime-aware references below; do not compare raw scores across unlike splits |
| Dataset | Explain 18,082 -> 3,526 -> 3,474 -> 3,095/2,628 -> V3 cohorts; distinguish custom main from official test | Dataset construction and literature-basis sections above |
| Threat model | Fixed benign/direct/misleading payloads delivered by image, text, or both; attacker does not change ground truth | Fixed experimental design above and payload YAML |
| Models and prompt | Four BF16 open VLMs on GCP A100/vLLM plus Gemini; frozen P5/V4; deterministic decoding | Prompt/inference table above and model locks |
| Metrics | Downward ASR, induced severe/critical under-triage, benign-adjusted paired risk difference | Metric definitions above |
| Main results | Clean context first, then malicious effects, benign controls, severe-case risk, and cross-model heterogeneity | Main result tables above |
| Secondary results | Natural/official clean context, presentation-style, and size mechanisms | Three secondary tables above |
| Discussion | No universal modality order; direct usually stronger; joint is model-dependent; camouflage persists but realism is unvalidated; size is non-monotonic | RQ answers above |
| Limitations | Conditional denominators, custom cohort, event/class confounding, synthetic English payloads, cross-service preprocessing, training contamination, no operational outcomes, pending visual review | Claims boundaries and active decisions above |
| Conclusion | Matched benign controls reveal direction-sensitive vulnerability across five models, with large model-specific variation | Recommended one-sentence claim above |

### Recommended Research Questions

1. How does delivery through the image, accompanying text, or both affect downward severity errors?
2. Do direct output instructions and misleading low-damage claims differ in effect?
3. Do malicious effects exceed modality-matched benign instability?
4. How do bundled presentation style and text size modify vulnerability?
5. Are qualitative vulnerability and modality ordering consistent across models?

### Recommended Results Order

1. Report clean metrics and exact eligible denominators without qualification labels.
2. Show downward ASR for all six malicious main conditions model by model.
3. Lead the inferential claim with malicious-minus-benign paired risk differences and corrected tests.
4. Show induced severe and critical under-triage to establish safety direction.
5. Explain model heterogeneity and the absence of a universal modality order.
6. Present natural/official clean results as context, not as a second attack experiment.
7. Keep presentation-style and size analyses secondary and denominator-aware.
8. End with sensitivity results and visual-review status.

## Future Work and Mitigation Agenda

1. **Input-trust separation:** mark OCR text, accompanying social text, and system/operator instructions as different trust domains; evaluate whether structured provenance labels reduce instruction following from untrusted content.
2. **Cross-modal consistency and abstention:** detect conflicts between visible damage evidence and textual low-damage claims, then abstain or route the case to a trained human rather than forcing a severity label.
3. **Attack-aware prompting and training:** compare frozen attack-aware prompts, adversarial instruction tuning, and fine-tuning only in a new predeclared study; do not retrofit defenses to the current outcomes.
4. **Human-in-the-loop agency guidance:** study how emergency-management analysts interpret model rationales, warnings, and uncertainty; define escalation rules and audit logs with disaster agencies before any operational recommendation.
5. **External and multilingual validation:** repeat on another disaster dataset, non-English payloads, naturally occurring text, and newer events to test whether CrisisMMD-specific wording, 2017 imagery, and English-only attacks drive the result.
6. **Cleaner disaster-type estimation:** construct a new main-first, within-class event-proportional V4 cohort with enough observations in every event-by-class cell. The present disaster-type table cannot separate event from class.
7. **Perceptual validation:** complete blinded human review and measure damage-region overlap so readability, plausibility, camouflage, and semantic occlusion can be evaluated rather than inferred from geometry.
8. **Richer text attacks:** extend the frozen rhetoric follow-up to paraphrases, multilingual claims, source-attribution cues, temporal claims, and adaptive attacks while controlling length and semantic target.

The current paper may motivate these safeguards, but it cannot claim that they are effective until tested. Its immediate practical implication is narrower: disaster-facing VLM systems should treat image-embedded and accompanying text as potentially untrusted and preserve human oversight for consequential triage.

## Remaining Work Before Submission

1. Complete the two-reviewer blinded visual validation for readability, plausibility, and critical-damage occlusion; the current 303 review rows are blank.
2. Complete primary-source related-work verification and avoid a first-of-kind claim until finished.
3. Import and validate the five open-model text-rhetoric and point-size follow-up outputs; keep them secondary and add Qwen3.8 only after its requested matrix is complete.
4. Finish replacing stale placeholders in `paper.md` from this reference, preserving all accepted caveats.
5. Verify model revisions, environment locks, privacy/licensing, and every final table denominator before release.
6. Disclose the retired P7 sensitivity as a protocol deviation and retain prompt dependence as a limitation.

The original paper-facing main, natural-clean, official-test, presentation-style, and relative-size inference runs are complete for the selected five-model panel, and the label-conflict sensitivity reports have been regenerated. The newly frozen text-rhetoric/point-size follow-ups and Qwen3.8 extension are secondary additions prompted by review; they do not invalidate the completed canonical matrix.

## References for Manuscript Drafting

### Disaster and CrisisMMD Literature

1. Alam, F., Ofli, F., and Imran, M. (2018). “CrisisMMD: Multimodal Twitter Datasets from Natural Disasters.” *Proceedings of ICWSM 2018*. [DOI](https://doi.org/10.1609/icwsm.v12i1.14983).
2. Ofli, F., Alam, F., and Imran, M. (2020). “Analysis of Social Media Data using Multimodal Deep Learning for Disaster Response.” *ISCRAM 2020*. [Preprint](https://arxiv.org/abs/2004.11838).
3. Alam, F., Ofli, F., Imran, M., Alam, T., and Qazi, U. (2020). “Deep Learning Benchmarks and Datasets for Social Media Image Classification for Disaster Response.” *ASONAM 2020*, 151-158. [DOI](https://doi.org/10.1109/ASONAM49781.2020.9381294).
4. Agarwal, M., Leekha, M., Sawhney, R., and Shah, R. R. (2020). “Crisis-DIAS: Towards Multimodal Damage Analysis—Deployment, Challenges and Assessment.” *AAAI 2020*. [DOI](https://doi.org/10.1609/aaai.v34i01.5369).
5. Imran, M., Alam, F., Qazi, U., Peterson, S., and Ofli, F. (2020). “Rapid Damage Assessment Using Social Media Images by Combining Human and Machine Intelligence.” [Preprint](https://arxiv.org/abs/2004.06675).
6. Shetty, N. P., Bijalwan, Y., Chaudhari, P., Shetty, J., and Muniyal, B. (2025). “Disaster Assessment from Social Media Using Multimodal Deep Learning.” *Multimedia Tools and Applications*, 84, 18829-18854. [DOI](https://doi.org/10.1007/s11042-024-19818-0).

### Typographic Attack and Multimodal Injection Literature

7. Cheng, H. et al. (2024). “Unveiling Typographic Deceptions: Insights of the Typographic Vulnerability in Large Vision-Language Models.” *ECCV 2024*. [Official paper](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07650.pdf).
8. Wang, X., Zhao, Z., and Larson, M. (2025). “Typographic Attacks in a Multi-Image Setting.” *NAACL 2025*, 12594-12604. [DOI](https://doi.org/10.18653/v1/2025.naacl-long.626).
9. Cao, Y. et al. (2025). “SceneTAP: Scene-Coherent Typographic Adversarial Planner against Vision-Language Models in Real-World Environments.” *CVPR 2025*, 25050-25059. [Official paper](https://openaccess.thecvf.com/content/CVPR2025/html/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.html).
10. Downer, G., Craven, S., Ruck, D., and Thomas, J. (2025). “Text2VLM: Adapting Text-Only Datasets to Evaluate Alignment Training in Visual Language Models.” *Proceedings of Machine Learning Research*, 299, 28-41. [Paper](https://proceedings.mlr.press/v299/downer25a.html).
11. Nagaraja, N. et al. (2025/2026). “Image-based Prompt Injection: Hijacking Multimodal LLMs through Visually Embedded Adversarial Instructions.” *FLLM 2025*. [Preprint record](https://arxiv.org/abs/2603.03637).
12. Zhan, Q. et al. (2024). “InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.” *Findings of ACL 2024*. [ACL Anthology](https://aclanthology.org/2024.findings-acl.624/).
13. Deng, A. et al. (2025). “Words or Vision: Do Vision-Language Models Have Blind Faith in Text?” *CVPR 2025*. [Official paper](https://openaccess.thecvf.com/content/CVPR2025/html/Deng_Words_or_Vision_Do_Vision-Language_Models_Have_Blind_Faith_in_CVPR_2025_paper.html).
14. Qraitem, M. et al. (2025). “Web Artifact Attacks Disrupt Vision Language Models.” *ICCV 2025*. [Official paper](https://openaccess.thecvf.com/content/ICCV2025/html/Qraitem_Web_Artifact_Attacks_Disrupt_Vision_Language_Models_ICCV_2025_paper.html).

### Statistical Methods

15. Wilson, E. B. (1927). “Probable Inference, the Law of Succession, and Statistical Inference.” *Journal of the American Statistical Association*, 22(158), 209-212. [DOI](https://doi.org/10.1080/01621459.1927.10502953).
16. McNemar, Q. (1947). “Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages.” *Psychometrika*, 12(2), 153-157. [DOI](https://doi.org/10.1007/BF02295996).
17. Holm, S. (1979). “A Simple Sequentially Rejective Multiple Test Procedure.” *Scandinavian Journal of Statistics*, 6(2), 65-70. [DOI](https://doi.org/10.2307/4615733).
18. Efron, B., and Tibshirani, R. (1986). “Bootstrap Methods for Standard Errors, Confidence Intervals, and Other Measures of Statistical Accuracy.” *Statistical Science*, 1(1), 54-75. [DOI](https://doi.org/10.1214/ss/1177013815).
19. Wei, L., and Hutson, A. D. (2013). “A Comment on Sample Size Calculations for Binomial Confidence Intervals.” *Journal of Applied Statistics*, 40(2), 311-319. [DOI](https://doi.org/10.1080/02664763.2012.740629).
20. Lachin, J. M. (1992). “Power and Sample Size Evaluation for the McNemar Test with Application to Matched Case-Control Studies.” *Statistics in Medicine*, 11(9), 1239-1251. [DOI](https://doi.org/10.1002/sim.4780110909).

### Model and Runtime Sources

21. Qwen Team. “Qwen3.5-27B.” Official model card and citation entry. [Model card](https://huggingface.co/Qwen/Qwen3.5-27B).
22. Qwen Team. “Qwen3.6-27B.” Official model card. [Model card](https://huggingface.co/Qwen/Qwen3.6-27B).
23. Qwen Team. “Qwen3.8-27B.” Official model card. [Model card](https://huggingface.co/Qwen/Qwen3.8-27B).
24. Qwen Team. “Qwen3-VL-32B-Instruct.” Official model card. [Model card](https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct).
25. Mistral AI. “Mistral-Small-3.1-24B-Instruct-2503.” Official model card. [Model card](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503).
26. Google. “Gemini 2.5 Flash.” Official Gemini API model documentation and model card. [Documentation](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash); [model card](https://modelcards.withgoogle.com/assets/documents/gemini-2.5-flash.pdf).
27. MLX-VLM. Official inference package for VLMs on Apple Silicon. [Repository](https://github.com/Blaizzy/mlx-vlm).
28. vLLM. Official multimodal model-serving documentation. [Documentation](https://docs.vllm.ai/en/latest/models/supported_models/).

Before submission, convert these entries to the target venue's BibTeX style and verify every author list/model-specific citation from the primary source. These references justify the dataset provenance, duplicate-control rationale, typographic threat, and statistical tools; they do not by themselves support a first-of-kind claim.

## Evidence Boundary

This document is the single reader-facing synthesis. Canonical open-model numerical evidence comes from the completed model-specific CSV reports under `reports/v3/gcp_a100/`; Gemini evidence remains under `reports/v3/final_analysis/models/gemini_2_5_flash/`. Dataset evidence comes from `reports/v3/dataset_protocol_audit.md`, split validation from `reports/v3/split_validation.json`, and accepted protocol decisions from `docs/PAPER_DECISIONS.md`. Historical MLX repeats, V2, 8-bit, 4-bit, and exploratory 9B results are not imported into the paper-facing conclusions.
