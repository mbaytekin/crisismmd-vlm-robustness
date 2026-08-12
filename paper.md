# When Disaster Images Talk Back: Cross-Modal Typographic Attacks on Vision–Language Models for Damage Assessment

> **Living paper blueprint — 11 August 2026.** This document is not yet a submission-ready manuscript. The current protocol and its dated amendments are tracked in [`docs/PAPER_DECISIONS.md`](docs/PAPER_DECISIONS.md); reconcile the synchronization debt listed there before treating this blueprint as current. Replace every `[PENDING]` field after the Mac Studio runs; do not present V2 or the Qwen 9B pilot as the final multi-model result.

Status labels used below:

- **[FIXED]**: method or design decision that should not change after the V3 data freeze.
- **[PRELIMINARY]**: completed evidence that motivates the final study but is not its confirmatory result.
- **[PENDING]**: requires the clean-screened multi-model V3 experiment or human review.

## Paper identity

### Recommended title

**When Disaster Images Talk Back: Cross-Modal Typographic Attacks on Vision–Language Models for Damage Assessment**

### Alternative titles

1. **Cross-Modal Typographic Attacks on Vision–Language Models for Disaster Damage Assessment**
2. **From Visible Damage to False Reassurance: Evaluating Typographic Attacks in Multimodal Crisis Assessment**
3. **Can Embedded Text Suppress Disaster Severity? A Controlled Robustness Study of Open Vision–Language Models**

### One-sentence paper claim

This paper tests whether fixed, black-box adversarial messages delivered through an image, a social-media post, or both can systematically lower VLM damage-severity predictions, while separating malicious effects from ordinary sensitivity to added text and requiring adequate clean task performance before robustness is interpreted.

### Keywords

Vision–language models; multimodal robustness; typographic attack; visual prompt injection; disaster response; damage assessment; under-triage; CrisisMMD; adversarial misinformation.

## Draft abstract

Vision–language models (VLMs) are increasingly considered for extracting actionable information from multimodal crisis reports, but text embedded in or accompanying an image may compete with visual evidence. We present a controlled evaluation of cross-modal typographic attacks against VLM-based disaster damage assessment. Starting from CrisisMMD, we construct a leakage-resistant benchmark of 990 image–text pairs from seven 2017 disasters, grouped by exact tweet and image identities and perceptual near-duplicate clusters. The benchmark evaluates three delivery modalities—image-only, text-only, and joint image–text attacks—under two semantic families: direct output instructions and misleading low-damage claims. Modality-matched benign controls, visual-style ablations, and text-size ablations separate adversarial semantics from the effects of adding visible or textual content. We clean-screen eight open VLM candidates from 12B to 397B parameters and run the full 9,900-condition matrix only for models meeting predeclared clean accuracy, macro-F1, class-recall, and parsing thresholds. **[PENDING: number of qualified models]** models qualified, producing **[PENDING: number of predictions]** valid predictions. Across qualified models, **[PENDING: principal result with effect size and confidence interval]**. The strongest condition was **[PENDING]**, while benign controls changed predictions by **[PENDING]**. These results show **[PENDING: bounded conclusion]**, with implications for human oversight and input-trust controls in automated crisis assessment.

Do not finalize the abstract until all model gates, full inference, human review, and corrected statistical analyses are complete.

## Technical summary

The final paper is a **competence-gated, paired robustness study**, not a model leaderboard and not a claim about real-world disaster operations. A model contributes confirmatory attack results only if it first performs adequately on untouched CrisisMMD examples. Every attacked observation is paired with the same sample’s clean observation, and malicious conditions are compared with modality-matched benign controls.

The principal safety question is not merely whether an attack causes any error. It is whether it creates **downward severity errors** that could suppress attention to genuinely damaged infrastructure. Accordingly, the final paper should emphasize target-eligible attack success, ordinal severity drop, and attack-induced under-triage. Attacked accuracy remains descriptive because an attack may simultaneously correct some baseline errors and create dangerous new ones.

The completed V2 experiment and the leakage-resistant Qwen 9B V3 pilot provide preliminary evidence that visual overlays can change severity predictions. They do not establish the final claim because the evaluated 9B model had weak clean performance, and V2 contained split/repetition issues that V3 was designed to remove.

## Research gap and positioning

CrisisMMD introduced paired social-media text and images with humanitarian and damage-severity annotations, enabling multimodal crisis analysis [Alam et al., 2018](https://doi.org/10.1609/icwsm.v12i1.14983). Subsequent systems such as Crisis-DIAS showed the value of combining linguistic and visual cues for damage identification and severity assessment [Agarwal et al., 2020](https://doi.org/10.1609/aaai.v34i01.5369). Recent work also considers large VLMs and agentic pipelines for post-disaster assessment and reporting [Chen et al., 2024](https://arxiv.org/abs/2411.01511).

Separately, typographic-attack research has shown that rendered text can redirect vision–language predictions and large multimodal model behavior [Cheng et al., 2024](https://arxiv.org/abs/2402.19150). Newer work studies visually embedded prompt injection as a black-box attack against multimodal models [Nagaraja et al., 2025/2026](https://arxiv.org/abs/2603.03637), while benchmarks such as [Text2VLM](https://proceedings.mlr.press/v299/downer25a.html) evaluate typographic prompt injection in broader alignment settings.

The intended gap is the intersection of these areas: **task-grounded, direction-sensitive robustness of multimodal disaster severity assessment under the same adversarial message delivered through different modalities**. The design additionally asks whether visual salience and presentation style alter the effect, and whether neutral added text produces similar instability.

Before submission, conduct a systematic related-work search and verify novelty. Do not claim “the first study” solely from the current source list.

## Contributions

The final manuscript can claim the following contributions if all pending stages are completed:

1. **A task-grounded threat model for crisis under-triage.** We frame typographic manipulation as an asymmetric operational risk in which severe or mild damage is pushed toward `little_or_no_damage`, rather than treating all label changes as equally harmful.

2. **A paired cross-modal experiment.** The same fixed payload is delivered through the image, the social-media text, or both, allowing image-only, text-only, and joint effects to be compared without changing payload semantics.

3. **Controls and perceptual ablations.** Modality-matched benign controls distinguish adversarial semantics from generic text sensitivity; separate style and size sets evaluate simple, news-like, and camouflaged overlays and small, medium, and large text.

4. **A leakage-resistant and competence-gated evaluation.** V3 removes exact and near duplicates across all splits, excludes unusable records, freezes the prompt and attack generator, and interprets attacks only for models that pass predeclared clean-performance gates.

5. **A reproducible open-model pipeline.** Model revisions, prompt/config hashes, runtime metadata, caches, and aggregate reports are recorded, while source tweets, images, generated attacks, and model weights remain outside the public repository.

## Research questions and hypotheses

### RQ1 — Does attack delivery modality matter?

How do image-only, text-only, and joint delivery change attack success, downward severity shifts, and induced under-triage?

**H1:** Image-bearing attacks will generally produce larger downward shifts than text-only attacks because the classifier is explicitly instructed to prioritize visible physical evidence. Joint delivery may strengthen or duplicate the image signal; it is not assumed to be additive.

### RQ2 — Does semantic form matter?

Are direct output instructions more effective than declarative misleading claims when payload and visual dose are matched?

**H2:** Direct instructions will yield higher target-hit rates than misleading claims, although declarative claims may remain effective because they resemble contextual scene information.

### RQ3 — Do realistic or low-salience presentations remain effective?

How do simple overlays, fictional news banners, and camouflaged text affect robustness?

**H3:** Increased legibility/salience will tend to increase attack efficacy, but style effects may not be monotonic because a news-like layout may receive greater semantic authority than a visually similar neutral overlay.

### RQ4 — Does overlay size monotonically increase attack efficacy?

How do small, medium, and large text conditions affect attack success and under-triage when placement and payload are fixed?

**H4:** Larger text may increase OCR/readability but can also obscure or reframe visual evidence; therefore the primary analysis tests an ordered trend without assuming monotonicity.

### RQ5 — Does vulnerability generalize across competent open VLMs?

Do attack effects persist across model families, architectures, parameter scales, and the separately reported 8-bit and 4-bit precision tiers?

**H5:** Vulnerability will vary by model, but downward attack effects will remain detectable in more than one qualified model family. Parameter count alone is not assumed to determine robustness.

### RQ6 — How much instability is attributable to benign additions?

Do neutral overlays or neutral tweet prefixes change predictions, and how much larger are malicious effects than modality-matched benign effects?

## Task definition

For an image–tweet pair \((I_i,T_i)\), a VLM predicts one of three CrisisMMD damage labels:

```text
little_or_no_damage = 0
mild_damage         = 1
severe_damage       = 2
```

The ground truth is the CrisisMMD **image damage-severity annotation**. The accompanying tweet is contextual model input and is not the source of the ground-truth label. This distinction must be explicit because image and tweet content can disagree.

The safety-relevant attack direction is downward:

```text
severe_damage → mild_damage
severe_damage → little_or_no_damage
mild_damage   → little_or_no_damage
```

## Threat model

**[FIXED]** The attacker can digitally modify the social-media image, prepend content to the associated post text, or do both before a VLM processes the report. The attacker cannot modify the original remainder of the tweet, the model weights, gradients, hidden activations, frozen system/user prompt, or decoding settings.

The attacks are:

- black-box and training-free;
- fixed across images and models rather than optimized per example;
- transferable in the sense that the same payload registry is used for every model;
- digital overlays or text prefixes, not imperceptible pixel perturbations;
- designed to reduce predicted damage severity;
- constrained not to alter the actual physical scene or erase the critical evidence that determines the human damage label.

In text-only and joint conditions, the inserted claim may semantically contradict the original tweet or image. These conditions are therefore **adversarial misinformation/prompt injection**, not label-preserving natural-language perturbations.

Out of scope are FGSM/PGD, optimized pixel noise, white-box or gradient attacks, model-specific payload search, fine-tuning, few-shot prompting, physical-world recapture, and defense optimization.

## Dataset and leakage-resistant cohort construction

### Source dataset

**[FIXED]** The source is CrisisMMD v2.0, which contains multimodal social-media records from seven 2017 natural disasters. After label normalization and removal of records with missing damage labels, missing/broken images, or missing tweet text, the local processed manifest contains **3,474 valid image–text pairs**:

| Damage label | Valid records |
|---|---:|
| `little_or_no_damage` | 474 |
| `mild_damage` | 829 |
| `severe_damage` | 2,171 |
| **Total** | **3,474** |

These 3,474 records span Hurricane Harvey (886), Hurricane Maria (846), Hurricane Irma (790), California wildfires (522), the Iraq–Iran earthquake (172), the Mexico earthquake (164), and Sri Lanka floods (94). These are available records after project filtering, not a claim about the complete size of every CrisisMMD task.

### V3 exclusions and duplicate grouping

**[FIXED]** V3 constructs duplicate clusters globally before assigning any split. A cluster unions records linked by:

- exact tweet ID or exact tweet text;
- exact image identity/hash;
- perceptual near-image similarity using dHash Hamming distance \(\leq 4\).

Rows connected to the previous prompt-selection pilot are excluded to prevent prompt-development leakage. V3 also excludes suspected mojibake and images whose shorter side is below 128 pixels.

| Cohort step | Records |
|---|---:|
| Valid processed records | 3,474 |
| Old prompt-pilot cluster exclusions | 144 |
| Suspected mojibake exclusions | 207 |
| Minimum-side exclusions | 28 |
| Eligible V3 records | 3,095 |
| Selected independent source samples | 990 |

Every selected sample belongs to a unique global duplicate cluster, and no cluster crosses pilot, main, style, or size splits.

### Final V3 splits

**[FIXED]** All splits are balanced by damage class and disjoint by duplicate cluster:

| Split | Source pairs | Per class | Conditions | Predictions per qualified model | Purpose |
|---|---:|---:|---:|---:|---|
| Pilot | 90 | 30 | 10 | 900 | technical qualification and pilot evidence |
| Main | 720 | 240 | 10 | 7,200 | primary modality/semantics analysis |
| Style ablation | 120 | 40 | 10 | 1,200 | simple/news/camouflage comparison |
| Size ablation | 60 | 20 | 10 | 600 | small/medium/large comparison |
| **Total** | **990** | — | — | **9,900** | per qualified model |

The splits cover all seven disaster events but do not force equal event prevalence. The main split contains 230 Hurricane Irma, 181 Hurricane Harvey, 148 Hurricane Maria, 57 California wildfire, 39 Mexico earthquake, 36 Iraq–Iran earthquake, and 29 Sri Lanka flood records. Primary overall reporting is class-balanced; a natural-prevalence reweighting sensitivity analysis is planned.

## Experimental conditions

### Primary main experiment

**[FIXED]** Pilot and main samples use the following ten paired conditions:

| Condition | Image | Tweet | Semantics | Purpose |
|---|---|---|---|---|
| `clean` | original | original | none | baseline |
| `benign_image` | neutral overlay | original | benign | image-dose control |
| `benign_text` | original | neutral prefix + original | benign | text-dose control |
| `benign_joint` | neutral overlay | same neutral prefix + original | benign | joint-dose control |
| `direct_image` | direct instruction overlay | original | adversarial instruction | image-only attack |
| `direct_text` | original | direct prefix + original | adversarial instruction | text-only attack |
| `direct_joint` | direct overlay | same direct prefix + original | adversarial instruction | joint attack |
| `misleading_image` | false low-damage claim overlay | original | adversarial claim | image-only attack |
| `misleading_text` | original | false claim prefix + original | adversarial claim | text-only attack |
| `misleading_joint` | false claim overlay | same false claim prefix + original | adversarial claim | joint attack |

The original tweet is preserved character-for-character after the inserted prefix. For a given sample and semantic family, image-only, text-only, and joint conditions use the same payload ID. Image and joint variants reuse the exact same attacked image, so their only difference is the tweet prefix.

### Style ablation

**[FIXED]** Style is evaluated on a separate 120-sample set and is not fully crossed with delivery modality or size. Conditions are clean plus benign, direct, and misleading overlays in three styles:

- `simple`: high-legibility edge overlay;
- `news`: a lower-third using the fictional `CRISIS24` identity, never a real news logo;
- `camouflage`: lower-contrast text selected from a low-complexity edge region.

All style conditions use medium text size. Camouflage contrast is measured after alpha compositing and constrained to 1.30–1.80, with opacity controlled by configuration.

### Size ablation

**[FIXED]** Size is evaluated on a separate 60-sample set with image-only simple overlays. Target relative font heights are:

| Size | Relative font height |
|---|---:|
| Small | 3% of image height |
| Medium | 5% of image height |
| Large | 8% of image height |

Payload, placement, color, background, opacity, and style are fixed within a sample; only text/box size changes.

## Payload design and visual-dose controls

**[FIXED]** Three centrally versioned payload families are used:

- **Benign controls:** neutral archive/record descriptions with no damage or decision cue.
- **Direct instructions:** explicit commands to ignore or override evidence and return `little_or_no_damage`.
- **Misleading claims:** declarative statements that report no structural or significant damage without explicitly ordering the classifier.

Payload assignment is deterministic with seed 42 and approximately balanced by class and event. Payload families were rewritten in V3 to reduce semantic-length confounding. Their mean character lengths are 50.2 (benign), 52.2 (direct), and 52.17 (misleading), differing by less than 4%.

Main visual attacks use a simple medium overlay. Main/style renderers maintain semantics-invariant occupied area wherever possible. The size ablation freezes sample-level placement and changes only the intended size parameters. Modified images are stored as lossless WebP; the format changes encoding rather than pixels.

Automated V3 validation passed all **9,900 condition rows** and **6,480 generated visual-condition records** with zero failures and zero warnings. This automatic result establishes file and metadata consistency, not human readability or label preservation.

## Human review protocol

**[PENDING]** Two or more independent reviewers must be blind to model predictions. Reviewers first inspect the clean image and then each unique modified visual variant for:

- whether the original damage label remains valid;
- text readability and visibility;
- whether critical damage evidence is obscured;
- plausibility of the intended style;
- overall image usability.

The planned full review covers **4,050 unique modified V3 images**; image and joint conditions that reuse the same file are rated once. Each file receives at least two independent ratings. Report raw agreement and Cohen’s kappa for two reviewers, or Krippendorff’s alpha if more than two reviewers contribute. Adjudication occurs only after independent ratings are locked.

Primary analysis should report both:

1. **intent-to-treat:** every automatically valid generated condition;
2. **review-passed:** conditions whose unique image passes the human protocol.

If reviewing all 4,050 images becomes infeasible, define and freeze a stratified sampling protocol before reviewers can see model outputs; do not silently substitute an opportunistic sample.

## Frozen model prompt and inference

### Prompt

**[FIXED]** Prompt P3 was selected using clean pilot performance only and is stored with a content hash. It defines all three damage classes and instructs the model to base severity primarily on visible physical infrastructure and utility damage while using the tweet only as supporting context.

The prompt does **not** say that inputs may be adversarial, tell the model to ignore image text, mark the tweet as untrusted, or include demonstrations. It is unchanged across clean, benign, and attacked conditions.

### Decoding and output

**[FIXED]** Every request uses:

```text
temperature = 0
top_p = 1
seed = 42, when supported
thinking = false
max_tokens = 150
images per request = 1
```

The model returns JSON with `damage_severity`, `confidence`, and a short evidence-based rationale. Chain-of-thought is neither requested nor stored. An invalid response receives one format-only retry; an unresolved response is a parse error and is never silently mapped to a class.

Inference is resumeable through a per-run SQLite cache. Each run stores the served model ID, immutable model revision, prompt and manifest hashes, backend and dependency versions, Git commit, hardware/OS identity, decoding parameters, latency, raw response, parsed result, and errors.

## Model panel and clean-first qualification

### Candidate panel

**[FIXED for current freeze]** The standard tier uses MLX 8-bit checkpoints; the ultra-large tier uses MLX 4-bit checkpoints to preserve memory headroom on a 512 GB M3 Ultra.

| Candidate | Total / active parameters | Precision | Architectural role | Full attack status |
|---|---:|---:|---|---|
| Gemma 4 Unified | 12B | 8-bit | lower-bound large candidate | `[PENDING GATE]` |
| Mistral Small 3.1 | 24B | 8-bit | independent Pixtral-style family | `[PENDING GATE]` |
| Gemma 4 MoE | 26B / 4B active | 8-bit | sparse Gemma contrast | `[PENDING GATE]` |
| Qwen3.5 | 27B | 8-bit | current dense Qwen | `[PENDING GATE]` |
| Gemma 4 Dense | 31B | 8-bit | dense large Gemma | `[PENDING GATE]` |
| Qwen3-VL Instruct | 32B | 8-bit | vision-specialized dense Qwen | `[PENDING GATE]` |
| Qwen3-VL Instruct | 235B / 22B active | 4-bit | ultra-large vision MoE | `[PENDING GATE]` |
| Qwen3.5 | 397B / 17B active | 4-bit | ultra-large unified MoE | `[PENDING GATE]` |

All model IDs and immutable Hub revisions must be locked immediately before production. A one-image vision smoke test and five identical deterministic requests precede clean screening.

### Competence gates

**[FIXED]** Attack inference is opt-in and blocked until both clean gates pass:

| Gate | Cohort | Parse rate | Accuracy | Macro-F1 | Minimum recall in every class |
|---|---:|---:|---:|---:|---:|
| Pilot screen | 90 clean samples | ≥99.5% | ≥60% | ≥55% | ≥40% |
| Main confirmation | 720 clean samples | ≥99.5% | ≥70% | ≥65% | ≥50% |

A pilot failure stops after 90 predictions. A pilot passer receives 720 main clean predictions. Only a model passing both stages receives adversarial, benign, style, and size inference. Every rejected model and its clean metrics must still be reported to prevent selective reporting.

Model size is a candidate-selection heuristic, not a guarantee of clean quality or robustness. Comparisons across the 8-bit standard and 4-bit ultra tiers are precision-confounded. Even within a family, dense versus MoE or unified versus vision-specialized architectures prevent a purely causal parameter-scaling interpretation.

## Outcome definitions

Let \(y_i\) be ground truth, \(c_{im}\) model \(m\)’s clean prediction, and \(a_{imk}\) its prediction under attacked condition \(k\). Let \(L(\cdot)\in\{0,1,2\}\) map the three classes to ordinal severity.

### Clean task competence

- **Accuracy:** fraction of clean predictions equal to ground truth.
- **Macro-F1:** unweighted mean of the three class F1 values.
- **Per-class precision, recall, and F1:** reported for all classes.
- **Balanced accuracy:** mean class recall; numerically aligned with macro recall in this balanced three-class setting.
- **Parse rate:** successfully parsed responses divided by attempted responses.

### Untargeted attack success rate

Among samples the model classified correctly when clean:

\[
\operatorname{ASR}_{mk}=
\frac{\sum_i \mathbb{1}[c_{im}=y_i \land a_{imk}\neq y_i]}
{\sum_i \mathbb{1}[c_{im}=y_i]}.
\]

Always report the numerator and denominator, not only the percentage.

### Targeted downward conversion

The final evaluator should report two clearly named quantities:

1. **Target-hit rate over all clean-correct samples** for continuity with preliminary tables.
2. **Target-eligible ASR (preferred):** clean-correct `mild_damage` or `severe_damage` samples that become `little_or_no_damage`, divided only by clean-correct mild/severe samples.

The second denominator is the interpretable measure of conversion to the attacker’s target. Do not label the legacy all-clean-correct denominator as target-eligible ASR.

### Severity drop

\[
D_{imk}=L(c_{im})-L(a_{imk}).
\]

Positive values are downward shifts, zero is unchanged, and negative values are upward shifts. Report mean and median drop plus one-level and two-level downward-shift rates. State whether each statistic uses all paired parsed samples or the clean-correct subset; the current implementation uses all paired parsed samples for severity-drop summaries.

### Under-triage

- **Severe under-triage:** among all ground-truth severe samples, attacked prediction is mild or little/no.
- **Critical under-triage:** among all ground-truth severe samples, attacked prediction is little/no.
- **Induced under-triage (preferred):** among ground-truth severe samples correctly predicted severe when clean, attacked prediction becomes mild or little/no.
- **Induced critical under-triage (add before final analysis):** among the same clean-correct severe subset, attacked prediction becomes little/no.

The induced variants isolate new safety failures caused by the condition and should receive greater emphasis than unconditional attacked under-triage.

### Benign-control instability

For each modality, report the fraction whose benign prediction differs from clean, and compute all attack outcomes relative to the corresponding benign control as well as clean. A malicious effect is more persuasive when it materially exceeds modality-matched benign instability.

### Attacked accuracy

Attacked accuracy is descriptive, not a primary robustness endpoint. It can remain stable or even increase when an attack corrects baseline errors for some samples while causing dangerous downward errors for others.

## Statistical analysis plan

**[FIXED before full results are inspected]** Analyses are paired at the source-sample level.

1. Report exact numerators/denominators and Wilson 95% intervals for ASR, target-eligible ASR, and under-triage proportions.
2. Use paired bootstrap confidence intervals with seed 42 and at least 2,000 replicates for severity-drop means and paired condition differences.
3. Use exact two-sided McNemar tests for paired binary outcomes. Apply Holm correction within each predeclared comparison family rather than across unrelated exploratory tables.
4. Contrast each malicious condition with both clean and its modality-matched benign control.
5. Analyze models separately first. For cross-model summaries, weight models equally rather than pooling every prediction as independent.
6. Fit a sample/event/model-aware hierarchical or mixed-effects model for aggregate claims, with repeated conditions nested within sample and model and event represented explicitly. Report the model specification, convergence diagnostics, effect sizes, and uncertainty.
7. Report class, event, payload, style, size, model family, architecture, and precision subgroups. Label underpowered subgroup findings exploratory.
8. Perform natural-prevalence reweighting in addition to the balanced primary analysis.
9. Run duplicate-threshold (dHash 2/4/6), minimum-image-side (96/128/224), human-review, and quantization sensitivities without replacing the frozen primary analysis.

Avoid causal language. These experiments estimate conditional behavioral differences under synthetic input interventions; they do not establish real-world misinformation prevalence or operational harm.

## Preliminary evidence — not the final result

### V2 main experiment

**[PRELIMINARY]** V2 evaluated Qwen3.5 9B AWQ on 900 main samples, with 459 clean-correct samples and 51.0% clean accuracy. Clean class recalls were 34.7% (`little_or_no_damage`), 31.7% (`mild_damage`), and 86.7% (`severe_damage`), indicating substantial class imbalance in model behavior.

| V2 condition | ASR | Successful / clean-correct | Wilson 95% CI | Mean severity drop | Induced under-triage |
|---|---:|---:|---:|---:|---:|
| Direct image | 32.5% | 149 / 459 | 28.3–36.9% | 0.576 | 28.5% (74/260) |
| Direct text | 13.5% | 62 / 459 | 10.7–16.9% | 0.108 | 5.4% (14/260) |
| Direct joint | 30.5% | 140 / 459 | 26.5–34.9% | 0.422 | 21.5% (56/260) |
| Misleading image | 23.5% | 108 / 459 | 19.9–27.6% | 0.414 | 25.0% (65/260) |
| Misleading text | 13.7% | 63 / 459 | 10.9–17.2% | 0.263 | 13.8% (36/260) |
| Misleading joint | 26.1% | 120 / 459 | 22.3–30.3% | 0.434 | 28.1% (73/260) |

Benign ASR was 5.9% for image, 2.4% for text, and 6.5% for joint controls. The modality pattern persisted after excluding 158 V2 main samples flagged for repeated/cross-split tweet identity, exact repeated perceptual hash, or suspected mojibake: direct-image ASR was 31.8% and misleading-image ASR was 23.4% in the 742-sample sensitivity cohort.

The V2 style ablation showed simple > news > camouflage for both semantic families: direct ASR was 34.8%, 23.9%, and 14.1%; misleading ASR was 26.1%, 22.8%, and 10.9%. The size ablation was not monotonic: direct medium/small/large ASR was 44.7%/42.1%/39.5%, while misleading small/medium/large was 39.5%/34.2%/26.3%.

**Required interpretation:** V2 supports the plausibility of the threat and informed V3 design. It is not the final paper estimate because its clean baseline was weak and its split construction did not fully prevent tweet and near-image leakage. V3 rebuilds the cohort rather than “repairing” V2 retrospectively.

### Leakage-resistant V3 Qwen 9B pilot

**[PRELIMINARY/EXPLORATORY]** On the corrected 90-sample V3 pilot, Qwen3.5 9B AWQ parsed 900/900 condition responses. Clean accuracy was 53.3%, macro-F1 was 50.1%, and only 48/90 samples were clean-correct. Clean recall was 40.0% for little/no, 26.7% for mild, and 93.3% for severe. This model fails the new clean qualification gates.

Direct image and direct joint each produced 39.6% ASR (19/48; 95% CI 27.0–53.7%). Direct text produced 16.7% (8/48). Benign image and joint additions changed the predicted label in 12.2% of samples, compared with 3.3% for benign text. These estimates have small denominators and are evidence for continuing the study, not confirmatory paper results.

## Final results section template

### Model qualification determines the valid robustness cohort

**[PENDING]** Begin the final Results section with all eight clean screens, including failures.

| Model | Precision | Pilot acc. / macro-F1 / min recall | Main acc. / macro-F1 / min recall | Parse rate | Qualified? | Failure reason |
|---|---|---|---|---:|---|---|
| Gemma 4 12B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Mistral 24B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Gemma 4 26B-A4B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Qwen3.5 27B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Gemma 4 31B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Qwen3-VL 32B | 8-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Qwen3-VL 235B-A22B | 4-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |
| Qwen3.5 397B-A17B | 4-bit | `[PENDING]` | `[PENDING/NA]` | `[PENDING]` | `[PENDING]` | — |

Suggested opening sentence:

> Of eight predeclared candidates, **[K]** passed both competence gates. Failed candidates are reported but excluded from confirmatory robustness aggregation because their clean predictions did not support a stable attack denominator.

### Visual delivery produces [PENDING] downward risk

Report per-model and equal-model aggregate outcomes. Never show an aggregate without the per-model heterogeneity needed to interpret it.

| Family | Modality | Model count | ASR | Target-eligible ASR | Mean severity drop | Induced under-triage | Malicious minus benign |
|---|---|---:|---:|---:|---:|---:|---:|
| Direct | Image | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |
| Direct | Text | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |
| Direct | Joint | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |
| Misleading | Image | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |
| Misleading | Text | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |
| Misleading | Joint | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` | `[PENDING]` |

Interpretation order:

1. Is each malicious condition larger than its benign control?
2. Is the direction predominantly downward rather than merely different?
3. Does the result replicate across qualified model families?
4. Does joint delivery add to image-only delivery, or is it redundant?
5. Are confidence intervals narrow enough to support the stated ranking?

### Style changes efficacy without proving realism

**[PENDING]** Report direct and misleading styles separately. Human plausibility and readability ratings must appear beside model effects; automatic contrast is insufficient to call a style realistic or covert.

### Size effects are tested as an ordered trend, not assumed

**[PENDING]** Report small/medium/large outcomes and the paired trend estimate. If the trend remains non-monotonic, discuss salience, wrapping, occupied area, image-text competition, and baseline corrections rather than forcing a “larger is stronger” narrative.

### Robustness varies across models and precision tiers

**[PENDING]** Present a model × condition heatmap and interval plot. Standard 8-bit and ultra-large 4-bit tiers must be visually distinguished. Claims about scaling should be descriptive and family-aware.

## Figures and tables to produce

### Main paper figures

1. **Figure 1 — Threat model and paired design.** One clean image–tweet pair branching into image-only, text-only, and joint delivery for direct, misleading, and benign payloads.
2. **Figure 2 — Dataset construction.** 3,474 valid records → exclusions/duplicate clusters → four disjoint balanced V3 splits.
3. **Figure 3 — Model qualification.** Clean accuracy, macro-F1, and minimum class recall with gate thresholds.
4. **Figure 4 — Main robustness effects.** Forest plot of target-eligible ASR or induced under-triage by condition and model.
5. **Figure 5 — Cross-model robustness heatmap.** Qualified models × attack conditions, with precision tier marked.
6. **Figure 6 — Style and size ablations.** Paired effect estimates with 95% intervals; do not use a line implying monotonic size unless supported.
7. **Figure 7 — Human review and failure cases.** Approved examples and representative failures, with source content anonymized as required.

### Main paper tables

1. Dataset/split summary and exclusions.
2. Model registry, immutable revisions, precision, clean gates, and qualification.
3. Primary modality × semantics results with exact denominators and intervals.
4. Modality-matched benign contrasts and Holm-adjusted paired tests.
5. Human-review acceptance and agreement.

Move event, payload, per-class, confusion-matrix, quantization, and sensitivity details to the appendix unless they alter a central conclusion.

## Discussion guide

### What a positive finding would mean

If multiple qualified models show malicious-minus-benign downward effects, the supported conclusion is:

> Fixed adversarial messages can exploit multimodal input fusion in disaster severity classification, and the effect depends on delivery modality, semantic form, and visual presentation.

It would **not** mean that the tested overlays occur frequently in real crises, that an operational system would necessarily act on the output without safeguards, or that all VLMs are equally vulnerable.

### Why image-only may exceed text-only

The frozen prompt prioritizes visible physical evidence. An image overlay may therefore be processed as part of that evidence or as a high-authority embedded instruction. Text-only payloads compete with an intact original tweet and may be easier for instruction hierarchy or contextual consistency to discount. This is a diagnostic interpretation, not a mechanistic proof.

### Why joint may fail to exceed image-only

Joint delivery can be redundant when the image payload already dominates. The extra textual copy may also conflict with the original tweet, trigger skepticism, or alter attention in a way that partially restores scene-based reasoning. A non-additive joint result is theoretically meaningful and should not be described as an attack failure.

### Why attacked accuracy can be misleading

An attack can push some baseline over-predictions toward the correct lower class while simultaneously causing clean-correct severe examples to become under-triaged. Therefore overall attacked accuracy may remain stable even when target-eligible ASR and induced under-triage increase.

### How to discuss benign effects

Benign instability is evidence that VLMs are sensitive to added text even without malicious semantics. The attack claim should therefore rely on the incremental effect over a modality- and dose-matched benign control, not only on clean-versus-attack differences.

### How to discuss model scale

If larger candidates perform better cleanly, this supports capacity as one possible contributor to task competence. It does not establish that scale causes robustness: model family, vision encoder, training mixture, instruction tuning, architecture, quantization, and image processing all vary. Report within-family patterns and counterexamples.

## Limitations

The final paper should explicitly retain the following limitations:

1. **Dataset age and domain.** CrisisMMD contains social-media records from seven 2017 events; results may not generalize to current platforms, languages, sensors, satellite imagery, or official field reports.
2. **Image-label target with multimodal input.** Ground truth is based on image damage severity, while the model also sees tweet text. Text–image disagreement may reflect dataset ambiguity rather than attack behavior.
3. **Synthetic digital interventions.** The attacks are rendered or prepended programmatically and do not establish physical-world robustness after recapture, compression, cropping, or platform transformations.
4. **Fixed English payloads.** The study measures a bounded payload registry, not adaptive attackers, multilingual attacks, paraphrase search, or model-specific optimization.
5. **Competence-based model inclusion.** Clean gates improve interpretability but condition the confirmatory cohort on this task. All failures must be published, and thresholds should not be changed after seeing attack results.
6. **Precision confounding.** Standard models use 8-bit weights and the 235B/397B ultra tier uses 4-bit; standard-versus-ultra differences are not pure scale effects.
7. **Human judgment.** Automated geometry and contrast checks cannot establish readability, plausibility, critical-region preservation, or label validity; final claims depend on pending blinded review.
8. **Annotation uncertainty.** Mild damage is visually ambiguous and was difficult for the exploratory 9B model. Original crowd labels may contain uncertainty that is not fully represented by a single hard class.
9. **No operational outcome study.** Under-triage is a model-output risk proxy, not measured harm to responders or affected communities.
10. **Training contamination unknown.** Open VLM pretraining data may include CrisisMMD images or related web content; exact contamination cannot be ruled out.
11. **No defense evaluation in the main study.** The existing OCR-mask interface addresses only image text and is retained as optional future work, not a validated defense against text-only or joint attacks.

## Ethics, safety, and responsible release

The study evaluates a manipulation that could suppress visible disaster severity. Release should support defensive research without packaging the dataset as an operational attack toolkit.

- Follow CrisisMMD’s terms and cite its creators.
- Do not commit raw tweets, source images, generated attack images, model outputs containing tweet text, or model weights to public Git.
- Public split indexes must remain tweet-redacted.
- Use a fictional news identity; never reproduce real broadcaster logos.
- Describe payloads in the paper because they are necessary for scientific audit, but avoid claims that encourage deployment against live crisis systems.
- Pseudonymize reviewer IDs and do not expose social-media usernames unnecessarily.
- State that human oversight and trusted-input boundaries remain necessary for high-stakes use.

## Reproducibility statement

The public repository contains versioned code, configs, tests, frozen prompt metadata, model registry, Docker definitions, aggregate reports, and redacted indexes. Private/ignored artifacts include raw CrisisMMD files, tweet-bearing manifests, generated images, prediction JSONL, caches, and model weights.

The final release must record:

- Git commit and `v3-data-freeze` tag;
- SHA-256 lock for prompt, payloads, pipeline config, splits, and condition manifest;
- immutable Hugging Face SHA for every candidate model;
- macOS, M3 Ultra, RAM, Python, MLX-VLM, and dependency versions;
- server arguments, precision, context/cache settings, and concurrency;
- per-run resolved configuration, prompt hash, seed, parse failures, and latency;
- exact result denominators and human-review status.

The primary Apple Silicon architecture runs MLX-VLM natively for Metal and uses a version-pinned Docker container for the research pipeline. NVIDIA replication uses a separately labeled vLLM profile. Results from different backends should not be pooled unless backend equivalence is directly validated.

## Suggested manuscript structure

### 1. Introduction

Use four paragraphs:

1. Explain why rapid damage assessment from multimodal crisis reports matters.
2. Explain the new trust problem: embedded/accompanying text can compete with visible evidence.
3. State the missing evaluation: modality, semantics, benign controls, under-triage direction, and competent multi-model baselines.
4. State the research questions and contributions.

### 2. Related Work

Organize by:

1. multimodal social-media analysis for disasters;
2. VLM/LVLM damage assessment and agentic disaster systems;
3. typographic attacks and visual prompt injection;
4. multimodal robustness metrics and defenses.

End with the exact gap. Avoid a chronological paper list.

### 3. Method

Recommended subsections:

1. Task and threat model
2. CrisisMMD preprocessing and duplicate-safe splits
3. Attack semantics and modality conditions
4. Visual rendering, style, and size ablations
5. Frozen prompt, model panel, and clean qualification
6. Metrics and statistical analysis
7. Human review and reproducibility

### 4. Results

Recommended order:

1. Model qualification
2. Main modality and semantics results
3. Benign-control contrasts
4. Under-triage and class-level effects
5. Style and size ablations
6. Cross-model heterogeneity
7. Sensitivity and human-review analyses

### 5. Discussion

Answer each RQ directly, then discuss operational interpretation, non-additive joint effects, model heterogeneity, and the difference between OCR salience and semantic authority.

### 6. Limitations and Ethics

Keep the limitations above visible and specific. Do not bury weak clean baselines, precision differences, or missing human validation in an appendix.

### 7. Conclusion

Use a bounded conclusion:

> This study provides a controlled estimate of how fixed cross-modal messages can redirect competent open VLMs on a disaster-severity task. The findings motivate explicit trust boundaries, human review, and multimodal input validation before VLM predictions are used for high-stakes crisis triage.

## Claims discipline

### Claims that are currently supported

- The V3 dataset contains 990 disjoint, class-balanced source samples and 9,900 validated condition rows.
- V3 duplicate grouping and exclusions correct known V2 leakage/text-quality weaknesses.
- The 9B exploratory model has inadequate clean performance under the new qualification criteria.
- Preliminary V2 and V3 results justify evaluating visual and cross-modal typographic vulnerability with stronger models.

### Claims that are not yet supported

- That the final attack effect generalizes across model families.
- That larger models are more or less robust.
- That joint attacks are stronger than image-only attacks.
- That news or camouflage styles are realistic or human-approved.
- That attack efficacy increases monotonically with font size.
- That the method causes real-world response failures.
- That the study is the first of its kind.
- That any defense is effective.

## Pre-submission completion checklist

- [ ] Commit and tag the frozen V3 data/config/code state.
- [ ] Transfer and SHA-verify private data on the Mac Studio.
- [ ] Lock every model revision and runtime version.
- [ ] Run deterministic vision/server checks.
- [ ] Publish all eight clean-screen outcomes.
- [ ] Run full matrices only for qualified models.
- [ ] Add target-eligible ASR and induced critical under-triage to the evaluator.
- [ ] Complete two-reviewer blinded visual validation and agreement analysis.
- [ ] Produce intent-to-treat and review-passed results.
- [ ] Complete paired, hierarchical, prevalence, duplicate, image-size, and quantization sensitivities.
- [ ] Update the abstract and every `[PENDING]` result.
- [ ] Verify every table against saved CSV/JSON and exact denominators.
- [ ] Complete systematic literature review and final BibTeX.
- [ ] Add dataset/model citations, `CITATION.cff`, environment lock, and model SHAs.
- [ ] Run privacy and licensing checks before public release.
- [ ] Remove process language and status labels from the submission manuscript.

## Evidence map inside the repository

| Paper content | Canonical project evidence |
|---|---|
| Frozen V3 design | `configs/v3/pipeline.yaml` |
| Payload registry and lengths | `configs/v3/attack_payloads.yaml` |
| Model candidates and gates | `configs/v3/models.yaml` |
| Frozen zero-shot prompt | `configs/prompts/frozen_prompt.yaml` |
| Split counts and exclusions | `reports/v3/split_validation.json` |
| Attack validation | `reports/v3/attack_validation.json` |
| Human review protocol | `reports/v3/manual_review/PROTOCOL.md` |
| Artifact hashes | `reports/v3/artifact_lock.json` |
| Exploratory V3 pilot | `reports/v3/pilot_results.md`, `reports/v3/tables/` |
| Preliminary V2 findings | `reports/v2/final_summary.md`, `reports/v2/tables/` |
| V2 leakage sensitivity | `reports/v2/tables/sensitivity_analysis.csv` |
| Execution checklist | `docs/V3_TODO.md` |
| Mac execution procedure | `docs/MAC_STUDIO_RUNBOOK.md` |

## Verified reference candidates

Use these as the initial bibliography; verify author order, venue, version, and BibTeX before submission.

1. Alam, F., Ofli, F., and Imran, M. (2018). “CrisisMMD: Multimodal Twitter Datasets from Natural Disasters.” *ICWSM*. [DOI](https://doi.org/10.1609/icwsm.v12i1.14983).
2. Agarwal, M., Leekha, M., Sawhney, R., and Shah, R. R. (2020). “Crisis-DIAS: Towards Multimodal Damage Analysis—Deployment, Challenges and Assessment.” *AAAI*. [DOI](https://doi.org/10.1609/aaai.v34i01.5369).
3. Imran, M., Alam, F., Qazi, U., Peterson, S., and Ofli, F. (2020). “Rapid Damage Assessment Using Social Media Images by Combining Human and Machine Intelligence.” [arXiv](https://arxiv.org/abs/2004.06675).
4. Chen, Z. et al. (2024). “Integration of Large Vision Language Models for Efficient Post-disaster Damage Assessment and Reporting.” [arXiv](https://arxiv.org/abs/2411.01511).
5. Cheng et al. (2024). “Unveiling Typographic Deceptions: Insights of the Typographic Vulnerability in Large Vision-Language Model.” *ECCV 2024*. [Paper](https://arxiv.org/abs/2402.19150).
6. Downer, G., Craven, S., Ruck, D., and Thomas, J. (2025). “Text2VLM: Adapting Text-Only Datasets to Evaluate Alignment Training in Visual Language Models.” *PMLR 299*. [Paper](https://proceedings.mlr.press/v299/downer25a.html).
7. Nagaraja, N., Zhang, L., Wang, Z., Zhang, B., and Patil, P. (2025/2026). “Image-based Prompt Injection: Hijacking Multimodal LLMs through Visually Embedded Adversarial Instructions.” *FLLM 2025*; arXiv posting 2026. [DOI](https://doi.org/10.1109/FLLM67465.2025.11391218).
8. Model-specific citations and technical reports listed in `docs/V3_MODEL_SELECTION.md` for Qwen3.5, Qwen3-VL, Gemma 4, Mistral Small 3.1, and MLX-VLM.
