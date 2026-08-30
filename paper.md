# When Disaster Images Talk Back: Cross-Modal Typographic Attacks on Vision–Language Models for Damage Assessment

> **Paper-facing working draft — 30 August 2026.** Canonical numerical results come from [`reports/v3/ALL_RESULTS.md`](reports/v3/ALL_RESULTS.md), and protocol interpretation follows accepted decisions D018-D029 in [`docs/PAPER_DECISIONS.md`](docs/PAPER_DECISIONS.md). The five open-model results use the common GCP A100/CUDA-vLLM execution family; Gemini uses its hosted Batch API. V2, Qwen 9B, 8-bit, 4-bit, and local MLX repeats are historical or audit evidence rather than primary paper results. The blinded visual review remains open, so readability, plausibility, and critical-damage non-occlusion are not yet empirical claims.

## Paper identity

### Recommended title

**When Disaster Images Talk Back: Cross-Modal Typographic Attacks on Vision–Language Models for Damage Assessment**

### Alternative titles

1. **Cross-Modal Typographic Attacks on Vision–Language Models for Disaster Damage Assessment**
2. **From Visible Damage to False Reassurance: Evaluating Typographic Attacks in Multimodal Crisis Assessment**
3. **Can Embedded Text Suppress Disaster Severity? A Controlled Robustness Study of Open Vision–Language Models**

### One-sentence paper claim

This paper tests whether fixed, black-box adversarial messages delivered through an image, a social-media post, or both can systematically lower initially correct VLM damage-severity predictions, while separating malicious effects from ordinary sensitivity to added text and reporting clean task competence separately from conditional robustness.

### Keywords

Vision–language models; multimodal robustness; typographic attack; visual prompt injection; disaster response; damage assessment; under-triage; CrisisMMD; adversarial misinformation.

## Draft abstract

Vision–language models (VLMs) are increasingly considered for extracting actionable information from multimodal crisis reports, but text embedded in or accompanying an image may compete with visual evidence. We present a controlled evaluation of cross-modal typographic attacks against VLM-based disaster damage assessment. Starting from CrisisMMD, we construct leakage-resistant, duplicate-cluster-disjoint cohorts totaling 990 image–text pairs from seven 2017 disasters. The main benchmark evaluates the same fixed benign, direct-instruction, and misleading low-damage messages through image-only, text-only, and joint delivery; separate cohorts test presentation style and relative text size. Six model configurations produced 43,200 parsed main predictions on a balanced 720-source cohort. Balanced-main clean accuracy was modest, ranging from 50.28% to 55.69%. Across models, the mean full-cohort downward-shift rates were 21.25%, 5.42%, and 22.39% for direct image, text, and joint delivery, versus 7.83%, 3.67%, and 9.39% for misleading delivery. After subtracting modality-matched benign downward shifts, the corresponding mean effects remained positive at 19.42, 4.72, 20.39, 6.00, 2.97, and 7.39 percentage points; all 36 model-condition paired contrasts were positive, with bootstrap intervals excluding zero and Holm-adjusted McNemar tests significant. Upward shifts were rare, averaging at most 0.60% of the full cohort. These findings show that fixed untrusted messages can systematically suppress initially correct damage-severity judgments across heterogeneous VLMs, especially through visual and joint delivery, while modest clean competence and the synthetic intervention design preclude deployment claims.

## Technical summary

The paper is a **clean-characterized, paired directional robustness study**, not a model leaderboard or an operational deployment assessment. Clean performance is reported continuously without a pass/fail threshold. The headline attack outcome is the number of clean-correct mild/severe decisions shifted downward divided by all 720 main samples; the model-specific eligible-only rate is retained as a conditional susceptibility measure. Every modified observation is paired with its clean source, and every malicious condition is contrasted with its modality-matched benign control.

The principal safety question is not whether any label changes, but whether an intervention creates **downward severity errors** that could suppress attention to damaged infrastructure. The main presentation therefore uses clean-to-attacked transition matrices, full-cohort downward and upward rates, benign-adjusted paired effects, and induced severe/critical under-triage. A signed mean severity drop remains supplementary because opposite-direction shifts can cancel.

The canonical panel comprises Qwen3.5 27B BF16, Qwen3.6 27B BF16, Qwen3.8 27B BF16, Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, and Gemini 2.5 Flash. Historical V2 and Qwen 9B experiments motivated V3 but do not contribute to the primary tables.

## Research gap and positioning

CrisisMMD introduced paired social-media text and images with humanitarian and damage-severity annotations, enabling multimodal crisis analysis [Alam et al., 2018](https://doi.org/10.1609/icwsm.v12i1.14983). Dataset studies subsequently showed that social-media image splits can leak exact and near duplicates and proposed duplicate-audited evaluation construction [Alam et al., 2020](https://doi.org/10.1109/ASONAM49781.2020.9381294). Ofli et al. studied multimodal informativeness and humanitarian categorization but excluded damage severity from their multimodal task because its annotation is image-only [Ofli et al., 2020](https://idl.iscram.org/files/ferdaofli/2020/2272_FerdaOfli_etal2020.pdf). More recent CrisisMMD work reports that severity remains difficult under strong class imbalance [Shetty et al., 2025](https://doi.org/10.1007/s11042-024-19818-0). Crisis-DIAS demonstrates multimodal damage identification and severity assessment [Agarwal et al., 2020](https://doi.org/10.1609/aaai.v34i01.5369), while DisasTeller studies large-VLM post-disaster assessment and reporting [Chen et al., 2026](https://doi.org/10.1038/s41467-025-68216-z).

Separately, typographic-attack research shows that rendered text can redirect VLM predictions [Cheng et al., 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07650.pdf), including in multi-image settings [Wang et al., 2025](https://aclanthology.org/2025.naacl-long.626/). SceneTAP studies scene-coherent typography [Cao et al., 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.html), and Words or Vision? examines conflicts between visual and textual evidence [Deng et al., 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Deng_Words_or_Vision_Do_Vision-Language_Models_Have_Blind_Faith_in_CVPR_2025_paper.html). InjecAgent formalizes indirect prompt injection through untrusted external content [Zhan et al., 2024](https://aclanthology.org/2024.findings-acl.624/), while Text2VLM evaluates typographic prompt injection in broader alignment settings [Downer et al., 2025](https://proceedings.mlr.press/v299/downer25a.html).

The intended gap is the intersection of these areas: **task-grounded, direction-sensitive robustness of multimodal disaster severity assessment under the same adversarial message delivered through different modalities**. The design additionally asks whether visual salience and presentation style alter the effect, and whether neutral added text produces similar instability.

The primary sources above support the task, leakage-control, and attack-design rationale. They do not justify an absolute “first study” claim, which is therefore omitted.

## Contributions

The manuscript makes the following bounded contributions:

1. **A task-grounded threat model for crisis under-triage.** We frame typographic manipulation as an asymmetric operational risk in which severe or mild damage is pushed toward `little_or_no_damage`, rather than treating all label changes as equally harmful.

2. **A paired cross-modal experiment.** The same fixed payload is delivered through the image, the social-media text, or both, allowing image-only, text-only, and joint effects to be compared without changing payload semantics.

3. **Matched controls and presentation ablations.** Modality-matched benign controls distinguish malicious semantics from generic text sensitivity; separate style and relative-size cohorts evaluate simple, news-like, and camouflaged overlays and 3%, 5%, and 8% image-height text. Human realism and readability remain unvalidated until the blinded review is completed.

4. **A leakage-resistant, clean-characterized evaluation.** V3 removes exact and near duplicates across all splits, excludes unusable records, freezes the prompt and attack generator, and separates descriptive clean competence from conditional attack effects on clean-correct decisions.

5. **A reproducible heterogeneous-model evaluation.** Five BF16 open VLMs are evaluated on a common A100/vLLM execution family and one hosted Gemini model is evaluated through its Batch API. Model revisions, prompt/config hashes, runtime metadata, and aggregate reports are recorded while restricted source data and weights remain outside public Git.

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

### RQ5 — Does vulnerability recur across heterogeneous VLMs?

Do attack effects persist across five BF16 open VLMs and one provider-managed hosted VLM?

**H5:** Vulnerability will vary by model, but downward attack effects will remain detectable in more than one evaluated model family. Parameter count alone is not assumed to determine robustness.

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
- rendered without changing the underlying scene; whether an overlay obscures critical evidence is assessed by the open blinded visual review and is not assumed from geometry alone.

In text-only and joint conditions, the inserted claim may semantically contradict the original tweet or image. These conditions are therefore **adversarial misinformation/prompt injection**, not label-preserving natural-language perturbations.

Out of scope are FGSM/PGD, optimized pixel noise, white-box or gradient attacks, model-specific payload search, fine-tuning, few-shot prompting, physical-world recapture, and defense optimization.

## Dataset and leakage-resistant cohort construction

### Source dataset

**[FIXED]** The source is CrisisMMD v2.0, which contains **18,082 real images across all annotation tasks**, not 18,082 damage-severity examples. The official damage-severity subset contains **3,526 image rows**: 475 little/no, 839 mild, and 2,212 severe [official CrisisNLP description](https://crisisnlp.qcri.org/crisismmd). After label/path/text validation and exact image SHA-256 deduplication, the local processed manifest contains **3,474 exact-SHA-unique image–text pairs**:

| Damage label | Valid records |
|---|---:|
| `little_or_no_damage` | 474 |
| `mild_damage` | 829 |
| `severe_damage` | 2,171 |
| **Total** | **3,474** |

These 3,474 records span Hurricane Harvey (886), Hurricane Maria (846), Hurricane Irma (790), California wildfires (522), the Iraq–Iran earthquake (172), the Mexico earthquake (164), and Sri Lanka floods (94). The 52-row difference from the official 3,526 is fully accounted for by 42 repeated exact-SHA groups: 94 official rows collapse to 42 retained images. Eleven exact-byte image groups (28 official rows) have conflicting severity labels; four retained V3 main rows belong to those groups. We preserve the frozen cohort and report an exclusion sensitivity rather than silently changing labels after inference. Full evidence is in `reports/v3/dataset_protocol_audit.md`.

### Published split and secondary clean cohorts

**[FIXED]** The published severity files contain 2,468 training, 529 development, and 529 test rows. Their per-class counts are arithmetically consistent with a 70/15/15 stratified partition, but the released severity split metadata does not document the exact sampling algorithm or seed; we therefore report the observed files rather than infer an undocumented procedure. The official test split has 71 little/no, 126 mild, and 332 severe examples; a constant severe prediction therefore achieves 62.8% accuracy. It is useful as a natural-imbalance, literature-comparability clean benchmark, but it is not an appropriate source for a universal 60% competence threshold.

The official 529 rows are not substituted for the primary attack cohort. Under the V3 duplicate definition, the published train and test files share 62 tweet IDs, 10 exact image hashes, and 106 duplicate clusters; the official test also overlaps existing prompt-development and V3 experiment cohorts. Because the models are evaluated zero-shot, train/test overlap is not ordinary supervised leakage in this study, but prompt/cohort overlap means the official test result must be labeled secondary and post-hoc.

Two clean-only evaluations supplement the paired attack design:

| Clean cohort | n | Distribution | Role | Uncertainty unit |
|---|---:|---|---|---|
| All locally valid severity records | 3,474 | natural local prevalence | broad clean competence and event sensitivity | global duplicate cluster |
| Published official test | 529 | published natural prevalence | literature comparability | global duplicate cluster |

The 3,474-row evaluation reports overall accuracy, macro-F1, ordinal MAE, per-class recall, event and event-by-class metrics, leave-one-event-out sensitivity, and duplicate-cluster bootstrap intervals. It is clean-only: generating nine attacks for every source record is not required to characterize natural-distribution competence.

### V3 exclusions and duplicate grouping

**[FIXED]** V3 constructs duplicate clusters globally before assigning any split. A cluster unions records linked by:

- exact tweet ID or exact tweet text;
- exact image identity/hash;
- perceptual near-image similarity using dHash Hamming distance \(\leq 4\).

Rows connected to the previous prompt-selection pilot are excluded to prevent prompt-development leakage. V3 also excludes suspected mojibake and images whose shorter side is below 128 pixels. This leaves 3,095 eligible rows in **2,628 independent duplicate clusters**.

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

**[FIXED]** All splits are balanced by damage class and disjoint by duplicate cluster. The 720 rows are a custom paired experimental cohort, not the published 529-row test split and not a natural-prevalence sample:

| Split | Source pairs | Per class | Conditions | Predictions per completed model | Purpose |
|---|---:|---:|---:|---:|---|
| Pilot | 90 | 30 | 10 | 900 | technical validation and prompt sensitivity |
| Main | 720 | 240 | 10 | 7,200 | primary modality/semantics analysis |
| Style ablation | 120 | 40 | 10 | 1,200 | simple/news/camouflage comparison |
| Size ablation | 60 | 20 | 10 | 600 | small/medium/large comparison |
| **Total** | **990** | — | — | **9,900** | per completed full V3 suite |

Selection is deterministic with seed 42. Labels are processed from rarest to most common. Auxiliary cohorts are filled from smallest to largest (size, pilot, style, then main), and each split/class repeatedly draws from its currently least represented event before a stable-hash tie-break. This creates broad event coverage and preserves cluster disjointness, but it is not event-proportional and was not derived from a published CrisisMMD split. In particular, the auxiliary cohorts consumed all eligible California and Sri Lanka little/no clusters before main selection; main little/no examples therefore come only from Hurricanes Harvey, Irma, and Maria.

The main split contains 230 Hurricane Irma, 181 Hurricane Harvey, 148 Hurricane Maria, 57 California wildfire, 39 Mexico earthquake, 36 Iraq–Iran earthquake, and 29 Sri Lanka flood records. A worst-case binomial 95% interval at n=720 has an approximately 3.7 percentage-point half-width; a class-specific n=240 estimate has approximately 6.3 points. These are retrospective precision descriptions, not an a priori power calculation. Primary attack reporting remains class-balanced; natural-prevalence **class-prior** reweighting, exact-label-conflict exclusion, and the separate 3,474-row clean evaluation are sensitivity analyses. Event-by-class population reweighting is not identified because main has structural zero cells (for example, no California or Sri Lanka little/no samples and no Iraq–Iran mild samples); event-specific estimates remain descriptive.

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

### Presentation-style ablation

**[FIXED]** Presentation style is evaluated on a separate 120-sample set (40 per class) and is not fully crossed with delivery modality or size. Conditions are clean plus benign, direct, and misleading overlays in three presentation strategies:

- `simple`: high-legibility edge overlay;
- `news`: a lower-third using the fictional `CRISIS24` identity, never a real news logo;
- `camouflage`: lower-contrast text selected from a low-complexity edge region.

All conditions use nominal medium text size and retain the same payload assignment within sample and semantics. These variants are a **bundled presentation contrast**, not an isolated typography-style intervention: contrast, background, occupied area, and placement policy differ by design. News always uses a bottom lower-third, simple uses deterministic top/bottom placement, and camouflage chooses a low-complexity top or bottom edge region. Consequently, model differences may be attributed to the presentation package but not to any single component. Camouflage contrast is measured after alpha compositing and constrained to 1.30–1.80, with opacity controlled by configuration.

The style cohort is exactly class-balanced, event-diversified, and globally duplicate-cluster-disjoint, but it is not event-proportional. A worst-case full-cohort binomial 95% interval has an approximate 8.8 percentage-point half-width. Conditional attack denominators can be smaller and are always reported exactly.

### Size ablation

**[FIXED]** Size is evaluated on a separate 60-sample set with image-only simple overlays. Target relative font heights are:

| Size | Relative font height |
|---|---:|
| Small | 3% of image height |
| Medium | 5% of image height |
| Large | 8% of image height |

Payload, placement, color, background, opacity, and style are fixed within a sample; only text/box size changes.

The size cohort is exactly class-balanced and cluster-disjoint. Its 60-source size gives an approximate worst-case 12.3 percentage-point binomial 95% half-width before restriction to clean-correct mild/severe samples. It is therefore a secondary paired mechanism analysis rather than a high-precision prevalence estimate. A monotonic size claim requires compatible sample-level patterns and paired intervals; an aggregate line alone is insufficient.

The multi-image typographic-attack formulation is consistent with Wang et al. (NAACL 2025). Cheng et al. (ECCV 2024) supports controlled typography-size experiments, and SceneTAP (CVPR 2025) motivates treating placement and scene integration as meaningful attack factors. No existing CrisisMMD protocol specifies a canonical style/size ablation distribution.

## Payload design and visual-dose controls

**[FIXED]** Three centrally versioned payload families are used:

- **Benign controls:** neutral archive/record descriptions with no damage or decision cue.
- **Direct instructions:** explicit commands to ignore or override evidence and return `little_or_no_damage`.
- **Misleading claims:** declarative statements that report no structural or significant damage without explicitly ordering the classifier.

Payload assignment is deterministic with seed 42 and approximately balanced by class and event. Payload families were rewritten in V3 to reduce semantic-length confounding. Their mean character lengths are 50.2 (benign), 52.2 (direct), and 52.17 (misleading), differing by less than 4%.

Main visual attacks use a simple medium overlay. Main/style renderers maintain semantics-invariant occupied area wherever possible. The size ablation freezes sample-level placement and changes only the intended size parameters. Modified images are stored as lossless WebP; the format changes encoding rather than pixels.

Automated V3 validation passed all **9,900 condition rows** and **6,480 generated visual-condition records** with zero failures and zero warnings. This automatic result establishes file and metadata consistency, not human readability or label preservation.

## Human review protocol

**[OPEN HUMAN REVIEW]** Two or more independent reviewers must be blind to model predictions and tweet text. Reviewers inspect the clean image and selected modified visual variants for:

- whether the original damage label remains valid;
- text readability and visibility;
- whether critical damage evidence is obscured;
- plausibility of the intended style;
- overall image usability.

The frozen paper-facing review instrument samples **60 main source images** (20 per class, diversified across available events) and shows clean, benign-image, direct-image, and misleading-image variants. A separate **9-source style supplement** (3 per class) shows clean plus direct/misleading simple, news, and camouflage variants. Each row receives at least two independent ratings. Report raw agreement and Cohen's kappa for two reviewers, or Krippendorff's alpha if more than two reviewers contribute. Adjudication occurs only after independent ratings are locked.

The primary automated analysis remains intent-to-treat. A review-passed sensitivity may additionally report:

1. **intent-to-treat:** every automatically valid generated condition;
2. **review-passed:** conditions whose unique image passes the human protocol.

The sampling instrument is generated before reviewers see model outputs and must not be changed in response to attack results.

## Frozen model prompt and inference

### Prompt

**[FIXED]** One zero-shot damage-assessment rubric is locked with a content hash. It defines all three damage classes and instructs the model to base severity on visible physical infrastructure and utility damage while using the tweet only as supporting context. The rubric was selected on the 180-example development split, so Qwen3.5 27B results on that split are post-hoc; the untouched 720-example main split supplies its paper-facing clean estimate. Internal candidate and version names are eliminated from paper-facing use under D029.

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

## Model panel and clean characterization

### Canonical panel

The paper panel was consolidated after completion to models with a complete common matrix: main, natural clean, official-test clean, presentation-style, and relative-size outputs. Historical quantized runs are excluded from primary tables.

| Paper label | Exact served identity | Precision/service | Canonical runtime |
|---|---|---|---|
| Qwen3.5 27B BF16 | `Qwen/Qwen3.5-27B` | BF16 | GCP A100 / CUDA-vLLM |
| Qwen3.6 27B BF16 | `Qwen/Qwen3.6-27B` | BF16 | GCP A100 / CUDA-vLLM |
| Qwen3.8 27B BF16 | `Qwen/Qwen3.8-27B` | BF16 | GCP A100 / CUDA-vLLM |
| Qwen3-VL 32B BF16 | `Qwen/Qwen3-VL-32B-Instruct` | BF16 | GCP A100 / CUDA-vLLM |
| Mistral 24B BF16 | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | BF16 | GCP A100 / CUDA-vLLM |
| Gemini 2.5 Flash | `gemini-2.5-flash` | provider-managed | Gemini Batch API |

Exact resolved configs, model identities, prompt hashes, and run manifests are retained with each result. Local MLX repeats are audit evidence only and are not mixed into canonical percentages.

### Clean characterization and conditional attack denominator

**[AMENDED 2026-08-26]** The untouched 720-example main result is reported with parse rate, accuracy, macro-F1, ordinal MAE, confusion matrix, and per-class recall. These values are descriptive; the manuscript applies no clean-performance pass/fail or deployment threshold.

The conditional downward-ASR denominator contains only ground-truth mild/severe samples classified correctly when clean. The headline full-cohort rate uses the same success count over all 720 main samples, making clean competence visible while preserving the direction of harm. Model-specific eligible counts are reported explicitly and limit interpretation; they do not create a qualification label.

Model size is not treated as a causal predictor of robustness. Family, vision encoder, architecture, training data, serving stack, and provider behavior differ, so cross-model comparisons remain descriptive even though the five open checkpoints share BF16 precision and a common execution family.

## Outcome definitions

Let \(y_i\) be ground truth, \(c_{im}\) model \(m\)'s clean prediction, and \(a_{imk}\) its prediction under condition \(k\). Let \(L(\cdot)\in\{0,1,2\}\) map the three classes to ordinal severity.

### Clean task competence

- **Accuracy:** fraction of clean predictions equal to ground truth.
- **Macro-F1:** unweighted mean of the three class F1 values.
- **Per-class precision, recall, and F1:** reported for all classes.
- **Balanced accuracy:** mean class recall; numerically aligned with macro recall in this balanced three-class setting.
- **Parse rate:** successfully parsed responses divided by attempted responses.

### Downward outcomes

Define a downward success as a clean-correct mild/severe prediction that moves to a lower ordinal class under condition \(k\).

1. **Full-cohort downward success rate (headline):** downward successes divided by all 720 main samples. This equals the eligible share multiplied by conditional downward ASR and therefore incorporates clean competence once.
2. **Conditional downward ASR:** the same success count divided by the model-specific number of clean-correct mild/severe samples. This measures susceptibility conditional on an initially correct actionable decision.
3. **Generic ASR:** any clean-correct prediction becoming wrong; retained only as supplementary continuity evidence.

Every percentage is accompanied by its numerator and denominator.

### Benign-adjusted effect

For modality \(r\), the primary paired contrast is

\[
\Delta_{mkr}=\frac{\sum_i (S^{\text{malicious}}_{imkr}-S^{\text{benign}}_{imr})}{720},
\]

where \(S\) is the downward-success indicator. Benign behavior is a matched control baseline, not a standard deviation. Clean correctness is already encoded in both indicators, so the contrast is not multiplied by clean accuracy again. A conditional version divides by the eligible denominator and is reported as a susceptibility analysis.

### Bidirectional transitions and severity shift

Clean-to-condition 3x3 transition matrices are the main directional presentation. Full-cohort upward shift counts clean-correct little/no or mild predictions that move to a higher class, divided by 720. The signed supplementary statistic \(D_{imk}=L(c_{im})-L(a_{imk})\) is positive for downward, zero for unchanged, and negative for upward shifts; it is not used alone because opposite directions can cancel.

### Under-triage

- **Severe under-triage:** among all ground-truth severe samples, attacked prediction is mild or little/no.
- **Critical under-triage:** among all ground-truth severe samples, attacked prediction is little/no.
- **Induced under-triage (preferred):** among ground-truth severe samples correctly predicted severe when clean, attacked prediction becomes mild or little/no.
- **Induced critical under-triage:** among the same clean-correct severe subset, attacked prediction becomes little/no.

The induced variants isolate new safety failures caused by the condition and should receive greater emphasis than unconditional attacked under-triage.

### Attacked accuracy

Attacked accuracy is descriptive, not a primary robustness endpoint. It can remain stable or even increase when an attack corrects baseline errors for some samples while causing dangerous downward errors for others.

## Statistical analysis plan

Analyses are paired at the source-sample level and follow the frozen evaluator.

1. Report exact numerators/denominators and Wilson 95% intervals for downward, upward, and under-triage proportions.
2. Use 5,000 paired bootstrap draws with seed 42 for malicious-minus-benign risk differences and paired condition effects.
3. Use exact two-sided McNemar tests for paired binary outcomes. Apply Holm correction within each predeclared comparison family rather than across unrelated exploratory tables.
4. Contrast each malicious condition with both clean and its modality-matched benign control.
5. Analyze models separately first. For cross-model summaries, weight models equally rather than pooling every prediction as independent.
6. Report class, payload, style, size, and disaster-type subgroups as exploratory when denominators are small or the design is confounded.
7. Report natural-distribution and official-test clean benchmarks separately from the balanced main cohort; do not pool their predictions with attack outcomes.
8. For presentation-style and size ablations, compare variants within semantics using paired downward-risk differences, paired bootstrap intervals, exact McNemar tests, and Holm correction. Avoid monotonic language unless model-level paired results support it.
9. Retain exact-image label-conflict exclusion and strict visual-match analyses as sensitivities without replacing the frozen intent-to-treat primary analysis.

A hierarchical model, duplicate-threshold sweep, minimum-image-side sweep, and quantization comparison were considered in earlier planning but are not part of the completed confirmatory analysis and are not claimed as completed.

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

**[PRELIMINARY/EXPLORATORY]** On the corrected 90-sample V3 pilot, Qwen3.5 9B AWQ parsed 900/900 condition responses. Clean accuracy was 53.3%, macro-F1 was 50.1%, and only 48/90 samples were clean-correct. Clean recall was 40.0% for little/no, 26.7% for mild, and 93.3% for severe. These values and the small eligible denominator make the run exploratory rather than paper-facing evidence.

Direct image and direct joint each produced 39.6% ASR (19/48; 95% CI 27.0–53.7%). Direct text produced 16.7% (8/48). Benign image and joint additions changed the predicted label in 12.2% of samples, compared with 3.3% for benign text. These estimates have small denominators and are evidence for continuing the study, not confirmatory paper results.

## Results

### Clean competence is modest and model-specific

All main responses parsed successfully. Balanced-main clean accuracy ranged from 50.28% to 55.69%, and the clean-correct mild/severe denominator ranged from 232 to 294. These results describe task behavior but do not establish operational readiness.

| Model | Accuracy | Macro-F1 | Ordinal MAE | Little recall | Mild recall | Severe recall | Eligible n/720 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 55.69% | 54.94% | 0.5486 | 65.00% | 35.83% | 66.25% | 245 |
| Qwen3.6 27B BF16 | 53.89% | 53.17% | 0.5833 | 59.58% | 35.83% | 66.25% | 245 |
| Qwen3.8 27B BF16 | 52.78% | 52.43% | 0.5819 | 54.58% | 38.33% | 65.42% | 249 |
| Qwen3-VL 32B BF16 | 53.19% | 52.98% | 0.5319 | 37.08% | 56.67% | 65.83% | 294 |
| Mistral 24B BF16 | 50.28% | 48.57% | 0.5778 | 54.17% | 71.67% | 25.00% | 232 |
| Gemini 2.5 Flash | 54.58% | 54.85% | 0.5597 | 50.00% | 50.83% | 62.92% | 273 |
| **Unweighted model mean** | **53.40%** | **52.82%** | **0.5639** | **53.41%** | **48.20%** | **58.61%** | **256.3** |

The unweighted mean row-normalized clean confusion matrix is shown below. Each model contributes equally; this is not a pooled 4,320-sample estimate.

| Ground truth | Pred. little/no | Pred. mild | Pred. severe |
|---|---:|---:|---:|
| Little/no | 53.41% | 40.70% | 5.91% |
| Mild | 27.43% | 48.20% | 24.37% |
| Severe | 23.47% | 17.92% | 58.61% |

### Visual and joint delivery produce the largest downward effects

Attack columns report clean-correct mild/severe decisions shifted downward, divided by all 720 main samples. This is the clean-performance-aware population rate requested in D022, not attacked error rate.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 14.86% | 4.86% | 14.44% | 6.39% | 3.75% | 7.64% |
| Qwen3.6 27B BF16 | 23.06% | 2.78% | 15.42% | 6.11% | 2.08% | 7.50% |
| Qwen3.8 27B BF16 | 8.33% | 4.31% | 14.86% | 6.11% | 3.47% | 7.08% |
| Qwen3-VL 32B BF16 | 32.64% | 4.72% | 32.92% | 9.86% | 3.75% | 9.44% |
| Mistral 24B BF16 | 26.25% | 8.61% | 24.58% | 10.14% | 2.78% | 11.53% |
| Gemini 2.5 Flash | 9.44% | 6.11% | 24.58% | 6.67% | 5.97% | 10.83% |
| **Unweighted model mean** | **19.10%** | **5.23%** | **21.14%** | **7.54%** | **3.64%** | **9.01%** |

Conditional eligible-only ASRs were substantially larger because their denominators exclude clean errors: the unweighted means were 53.64%, 14.88%, and 58.75% for direct image/text/joint, and 21.27%, 10.12%, and 25.41% for misleading image/text/joint. Full model-specific values appear in Appendix B.

### Malicious effects exceed matched benign instability

The table reports malicious minus modality-matched benign full-cohort downward rates. All 36 model-condition contrasts were positive; their 5,000-draw paired-bootstrap intervals excluded zero and their Holm-adjusted exact McNemar tests were significant.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | +13.61 pp | +4.31 pp | +12.92 pp | +5.14 pp | +3.19 pp | +6.11 pp |
| Qwen3.6 27B BF16 | +21.11 pp | +2.64 pp | +13.61 pp | +4.17 pp | +1.94 pp | +5.69 pp |
| Qwen3.8 27B BF16 | +6.53 pp | +4.17 pp | +13.33 pp | +4.31 pp | +3.33 pp | +5.56 pp |
| Qwen3-VL 32B BF16 | +31.25 pp | +4.17 pp | +31.39 pp | +8.47 pp | +3.19 pp | +7.92 pp |
| Mistral 24B BF16 | +23.75 pp | +8.06 pp | +21.67 pp | +7.64 pp | +2.22 pp | +8.61 pp |
| Gemini 2.5 Flash | +7.36 pp | +4.44 pp | +22.36 pp | +4.58 pp | +4.31 pp | +8.61 pp |
| **Unweighted model mean** | **+17.27 pp** | **+4.63 pp** | **+19.21 pp** | **+5.72 pp** | **+3.03 pp** | **+7.08 pp** |

Matched benign downward rates were small but nonzero: mean image, text, and joint rates were 1.83%, 0.69%, and 2.00%. These are control rates, not uncertainty estimates.

### Transition matrices expose direction and magnitude

The unweighted mean row-normalized clean-to-attacked matrices below include all three clean-correct starting classes. Rows are clean labels and columns are attacked labels. They therefore expose both under-triage and severity inflation rather than reducing the result to a signed scalar. Full 3x3 model-specific count matrices are retained in Appendix D.

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

Upward shifts were rare but were measured symmetrically from the same paired predictions. Each value below is the number of clean-correct little/no or mild decisions shifted to a higher class divided by all 720 sources.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 0.83% | 0.28% | 0.97% | 0.28% | 0.00% | 0.00% |
| Qwen3.6 27B BF16 | 0.14% | 0.28% | 0.97% | 0.14% | 0.14% | 0.28% |
| Qwen3-VL 32B BF16 | 0.00% | 0.42% | 0.00% | 0.14% | 0.00% | 0.14% |
| Mistral 24B BF16 | 0.00% | 0.28% | 0.00% | 0.14% | 0.56% | 0.28% |
| Gemini 2.5 Flash | 1.39% | 0.83% | 0.14% | 0.28% | 0.42% | 0.14% |
| **Unweighted model mean** | **0.47%** | **0.42%** | **0.42%** | **0.20%** | **0.22%** | **0.17%** |

Direct image and joint delivery therefore predominantly created downward rather than symmetric instability. The upward table prevents that asymmetry from being assumed by construction.

### Style changes efficacy without establishing realism

Conditional downward ASR on the 120-source style cohort used only 28-37 eligible cases per model. Simple and news presentations were generally more effective than camouflage, but model heterogeneity and small denominators require a secondary interpretation.

| Model | Direct simple | Direct news | Direct camo | Misleading simple | Misleading news | Misleading camo |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 41.94% | 32.26% | 12.90% | 19.35% | 22.58% | 9.68% |
| Qwen3.6 27B BF16 | 56.25% | 34.38% | 15.62% | 12.50% | 18.75% | 9.38% |
| Qwen3-VL 32B BF16 | 81.08% | 83.78% | 21.62% | 24.32% | 29.73% | 16.22% |
| Mistral 24B BF16 | 67.86% | 53.57% | 32.14% | 32.14% | 39.29% | 17.86% |
| Gemini 2.5 Flash | 25.00% | 16.67% | 8.33% | 22.22% | 16.67% | 13.89% |
| **Unweighted model mean** | **54.42%** | **44.13%** | **18.13%** | **22.11%** | **25.40%** | **13.40%** |

These values do not establish that news or camouflage renders are realistic, readable, or non-occluding. Those claims remain conditional on the blinded review.

### Relative size effects are not universally monotonic

The completed size experiment used target font heights of 3%, 5%, and 8% of image height on a separate 60-source cohort. Eligible denominators ranged from 13 to 21.

| Model | Direct 3% | Direct 5% | Direct 8% | Misleading 3% | Misleading 5% | Misleading 8% |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 70.00% | 70.00% | 50.00% | 25.00% | 25.00% | 35.00% |
| Qwen3.6 27B BF16 | 68.42% | 78.95% | 63.16% | 15.79% | 21.05% | 15.79% |
| Qwen3-VL 32B BF16 | 76.19% | 90.48% | 85.71% | 28.57% | 33.33% | 33.33% |
| Mistral 24B BF16 | 53.85% | 61.54% | 76.92% | 15.38% | 38.46% | 38.46% |
| Gemini 2.5 Flash | 22.22% | 27.78% | 44.44% | 11.11% | 16.67% | 22.22% |
| **Unweighted model mean** | **58.14%** | **65.75%** | **64.05%** | **19.17%** | **26.90%** | **28.96%** |

The direct mean peaks at 5%, and three model-level direct sequences are non-monotonic. The result therefore rejects a universal “larger text is stronger” law. The separate nominal-point follow-up is secondary and is not substituted for this frozen relative-size result.

### Secondary clean cohorts and disaster-type analysis

Natural-3,474 and official-test-529 are clean-only characterization cohorts. Mean accuracy/macro-F1 was 52.13%/46.14% on natural clean and 52.82%/46.84% on official test. The main attack cohort is globally class-balanced but event and class are confounded.

| Disaster type | n | Mean clean accuracy | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Earthquake | 75 | 85.33% | 35.20% | 1.60% | 39.73% | 6.40% | 2.93% | 7.73% |
| Flood | 29 | 33.10% | 13.79% | 4.83% | 20.69% | 8.28% | 2.07% | 11.03% |
| Hurricane | 559 | 51.41% | 19.36% | 6.19% | 20.00% | 8.37% | 3.94% | 10.02% |
| Wildfire | 57 | 42.81% | 25.26% | 3.16% | 23.86% | 4.21% | 2.81% | 4.56% |

These are descriptive group summaries, not causal disaster-type effects: group sizes differ sharply and multiple event-by-class cells are structurally empty.

Among cases that each model classified correctly and that could move downward, the conditional rates give a different view of susceptibility:

| Disaster type | Eligible n range per model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|---:|
| Earthquake | 38-71 | 44.97% | 1.94% | 48.91% | 8.50% | 4.10% | 10.17% |
| Flood | 2-12 | 51.21% | 12.12% | 60.30% | 20.76% | 5.15% | 27.58% |
| Hurricane | 139-186 | 67.16% | 21.49% | 68.46% | 29.03% | 13.81% | 34.99% |
| Wildfire | 23-26 | 58.91% | 7.24% | 55.10% | 9.65% | 6.41% | 10.55% |

Earthquake has the highest clean accuracy and the lowest conditional image/joint susceptibility for several contrasts, yet its high number of initially correct eligible cases gives it high full-cohort direct risk. Hurricane has middling clean competence but the largest conditional susceptibility across all six attack conditions. Flood cannot be called reliable merely because some full-cohort rates are low: its clean accuracy is only 33.10% and its eligible denominators are as small as two. Reliability must therefore be described on two axes, clean competence and conditional attack susceptibility, rather than as a single disaster ranking.

## Figures and tables

### Main paper figures

1. **Figure 1 — Threat model and paired design.** One clean image–tweet pair branching into image-only, text-only, and joint delivery for direct, misleading, and benign payloads.
2. **Figure 2 — Dataset construction.** 3,474 valid records → exclusions/duplicate clusters → four disjoint balanced V3 splits.
3. **Figure 3 — Model clean competence.** Clean accuracy, macro-F1, and per-class recall without a pass/fail reference line.
4. **Figure 4 — Main robustness effects.** Forest plot of full-cohort downward and benign-adjusted effects by condition and model.
5. **Figure 5 — Severity transition matrices.** Six 3x3 clean-to-attacked matrices showing downward, unchanged, and upward cells; the generated artifact is `reports/v3/final_analysis/class_transition_heatmap.{png,svg}`.
6. **Figure 6 — Cross-model robustness heatmap.** Evaluated models × attack conditions, with exact precision marked.
7. **Figure 7 — Style and size ablations.** Paired effect estimates with 95% intervals; do not use a line implying monotonic size unless supported.
8. **Figure 8 — Human review and failure cases.** Add only after the two-reviewer visual audit is complete, with source content anonymized as required.

### Main paper tables

1. Dataset/split summary and exclusions.
2. Model registry, immutable revisions, precision, clean competence, and eligible denominators.
3. Primary modality × semantics results with exact denominators and intervals.
4. Modality-matched benign contrasts and Holm-adjusted paired tests.
5. Human-review acceptance and agreement, pending completion.

Move payload, per-class, model-specific confusion-matrix, and sensitivity details to the appendix unless they alter a central conclusion.

## Discussion guide

### What the observed finding means

All six evaluated models show positive malicious-minus-benign downward effects in all six main malicious conditions. The supported conclusion is:

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

### How to discuss model differences

No monotonic robustness ordering follows parameter count or clean accuracy. Model family, vision encoder, training mixture, instruction tuning, architecture, preprocessing, and hosted-service behavior vary. Report heterogeneity and counterexamples rather than a scale law.

## Limitations

The final paper should explicitly retain the following limitations:

1. **Dataset age and domain.** CrisisMMD contains social-media records from seven 2017 events; results may not generalize to current platforms, languages, sensors, satellite imagery, or official field reports.
2. **Image-label target with multimodal input.** Ground truth is based on image damage severity, while the model also sees tweet text. Text–image disagreement may reflect dataset ambiguity rather than attack behavior.
3. **Synthetic digital interventions.** The attacks are rendered or prepended programmatically and do not establish physical-world robustness after recapture, compression, cropping, or platform transformations.
4. **Fixed English payloads.** The study measures a bounded payload registry, not adaptive attackers, multilingual attacks, paraphrase search, or model-specific optimization.
5. **Conditional denominators.** Clean competence determines how many and which mild/severe decisions enter each model's attack denominator. Small or class-skewed denominators limit interpretation even when paired effects are estimable.
6. **Runtime and service heterogeneity.** The five open checkpoints are BF16 and share an A100/vLLM execution family, but Gemini is provider-managed and preprocessing still varies across families. Cross-model differences are not pure architecture effects.
7. **Human judgment.** Automated geometry and contrast checks cannot establish readability, plausibility, or critical-region preservation. The planned two-reviewer blinded audit is still incomplete, so the manuscript makes no empirical perceptual-validity claim.
8. **Annotation uncertainty.** Mild damage is visually ambiguous and was difficult for the exploratory 9B model. Original crowd labels may contain uncertainty that is not fully represented by a single hard class.
9. **No operational outcome study.** Under-triage is a model-output risk proxy, not measured harm to responders or affected communities.
10. **Training contamination unknown.** Open VLM pretraining data may include CrisisMMD images or related web content; exact contamination cannot be ruled out.
11. **No defense evaluation in the main study.** The existing OCR-mask interface addresses only image text and is retained as optional future work, not a validated defense against text-only or joint attacks.
12. **Custom balanced cohort.** The V3 main set is larger and more duplicate-resistant than the published test split but is custom, class-balanced, and event-equalizing rather than natural-prevalence or event-proportional. Event-specific causal/generalization claims are unsupported, and natural-distribution clean results must be reported separately.
13. **Exact-image label conflicts.** Eleven exact-byte image groups in the published severity files carry conflicting labels; four retained main rows originate from those groups. The frozen primary cohort is unchanged, with a conflict-exclusion sensitivity reported alongside it.
14. **Prompt dependence.** One fixed zero-shot prompt was used unchanged for the complete attack matrix. The study does not claim prompt invariance and does not discuss abandoned internal prompt candidates.

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
- GCP A100/CUDA-vLLM versions for the five canonical open models and provider metadata for Gemini;
- server arguments, precision, context/cache settings, and concurrency;
- per-run resolved configuration, prompt hash, seed, parse failures, and latency;
- exact result denominators and human-review status.

The canonical five-open-model results use GCP A100/CUDA-vLLM. Gemini is a separately identified hosted-service result. Local Apple Silicon/MLX repeats are retained for audit only and are not pooled with canonical predictions.

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
5. Frozen prompt, model panel, and clean characterization
6. Metrics and statistical analysis
7. Human review and reproducibility

### 4. Results

Recommended order:

1. Model clean competence and eligible denominators
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

> This study provides a controlled estimate of how fixed cross-modal messages can redirect VLM damage-severity predictions. Across six heterogeneous models, malicious image and joint delivery produced consistent benign-adjusted downward effects, while clean competence remained modest. The findings motivate explicit trust boundaries, human review, and multimodal input validation before VLM predictions are considered for high-stakes crisis triage.

## Claims discipline

### Claims that are currently supported

- The V3 dataset contains 990 disjoint, class-balanced source samples and 9,900 validated condition rows.
- V3 duplicate grouping and exclusions correct known V2 leakage/text-quality weaknesses.
- The canonical six-model main matrix contains 43,200 parsed predictions on the same 720 sources and ten conditions per model.
- All 36 model-condition malicious-minus-benign downward contrasts are positive and statistically supported under the frozen paired analysis.
- Image and joint delivery generally produce larger downward effects than text-only delivery, with meaningful model heterogeneity.
- Full-cohort upward shifts are rare relative to downward shifts under the malicious conditions.
- Relative-size effects are not universally monotonic, and style effects are secondary because eligible denominators are small.

### Claims that are not supported

- That the observed effect generalizes beyond the six evaluated configurations, CrisisMMD, English fixed payloads, or synthetic digital interventions.
- That larger models are more or less robust.
- That joint attacks are universally stronger than image-only attacks.
- That news or camouflage styles are realistic or human-approved.
- That attack efficacy increases monotonically with font size.
- That disaster-type differences are causal or event-general.
- That results are invariant to prompt choice.
- That the method causes real-world response failures.
- That the study is the first of its kind.
- That any defense is effective.

## Pre-submission completion checklist

- [ ] Commit and tag the frozen V3 data/config/code state.
- [ ] Transfer and SHA-verify private data on the Mac Studio.
- [x] Lock canonical model identities, prompt/config hashes, and runtime provenance.
- [x] Run deterministic vision/server checks.
- [x] Produce every selected model's main, natural-clean, and official-test outcomes.
- [x] Run the fixed six-model main matrix.
- [x] Freeze and validate the dedicated presentation-style and size ablation manifests.
- [x] Run the separate six-model presentation-style and relative-size ablation queue.
- [x] Add target-eligible ASR and induced critical under-triage to the evaluator.
- [ ] Complete two-reviewer blinded visual validation and agreement analysis.
- [ ] Produce the review-passed sensitivity after human review; intent-to-treat is complete.
- [x] Complete the accepted paired analysis, benign-adjusted contrasts, upward outcomes, and label-conflict sensitivities.
- [x] Update the abstract and canonical result tables.
- [x] Verify manuscript tables against saved CSV/JSON and exact denominators.
- [x] Verify the core bibliography against primary publisher/proceedings sources; export final venue-specific BibTeX during typesetting.
- [ ] Add dataset/model citations, `CITATION.cff`, environment lock, and model SHAs.
- [ ] Run privacy and licensing checks before public release.
- [ ] Remove the remaining repository/process language when converting this working draft to the venue template.

## Evidence map inside the repository

| Paper content | Canonical project evidence |
|---|---|
| Frozen V3 design | `configs/v3/pipeline.yaml` |
| Payload registry and lengths | `configs/v3/attack_payloads.yaml` |
| Final model panel and analysis protocol | `configs/v3/final_analysis_protocol.yaml` |
| Ablation design and model queue | `configs/v3/ablation_protocol.yaml`, `scripts/run_v3_ablations.sh` |
| Ablation dataset and RAM audits | `reports/v3/ablation_protocol/dataset_audit.md`, `reports/v3/ablation_protocol/ram_readiness.md` |
| Fixed zero-shot prompt | Exact text in the manuscript appendix; content hash in the artifact lock |
| Split counts and exclusions | `reports/v3/split_validation.json` |
| Dataset/split literature audit | `reports/v3/dataset_protocol_audit.md`, `reports/v3/dataset_protocol_audit.json` |
| Secondary clean cohort protocol | `configs/v3/dataset_evaluation.yaml` |
| Attack validation | `reports/v3/attack_validation.json` |
| Human review protocol | `reports/v3/manual_review/PROTOCOL.md` |
| Canonical paper-facing results | `reports/v3/ALL_RESULTS.md` |
| Supervisor feedback interpretation | `docs/SUPERVISOR_FEEDBACK_RESPONSE.md` |
| Canonical A100 model reports | `reports/v3/gcp_a100/models/*/` |
| Gemini report | `reports/v3/final_analysis/models/gemini_2_5_flash/` |
| Artifact hashes | `reports/v3/artifact_lock.json` |
| Exploratory V3 pilot | `reports/v3/pilot_results.md`, `reports/v3/tables/` |
| Preliminary V2 findings | `reports/v2/final_summary.md`, `reports/v2/tables/` |
| V2 leakage sensitivity | `reports/v2/tables/sensitivity_analysis.csv` |
| Execution checklist | `docs/V3_TODO.md` |
| Mac execution procedure | `docs/MAC_STUDIO_RUNBOOK.md` |

## Primary-source-verified references

The core bibliography below was checked against publisher, proceedings, or official model-card pages on 28 August 2026. Venue-specific BibTeX formatting remains a typesetting task, but these records should be used instead of secondary summaries or search-result metadata.

1. Alam, F., Ofli, F., and Imran, M. (2018). “CrisisMMD: Multimodal Twitter Datasets from Natural Disasters.” *Proceedings of the International AAAI Conference on Web and Social Media*, 12(1). [AAAI/DOI](https://doi.org/10.1609/icwsm.v12i1.14983).
2. Alam, F., Ofli, F., Imran, M., Alam, T., and Qazi, U. (2020). “Deep Learning Benchmarks and Datasets for Social Media Image Classification for Disaster Response.” *ASONAM 2020*. [IEEE/DOI](https://doi.org/10.1109/ASONAM49781.2020.9381294).
3. Ofli, F., Alam, F., and Imran, M. (2020). “Analysis of Social Media Data using Multimodal Deep Learning for Disaster Response.” *ISCRAM 2020*. [Official ISCRAM paper](https://idl.iscram.org/files/ferdaofli/2020/2272_FerdaOfli_etal2020.pdf).
4. Shetty, N. P., Bijalwan, Y., Chaudhari, P., Shetty, J., and Muniyal, B. (2025). “Disaster Assessment from Social Media Using Multimodal Deep Learning.” *Multimedia Tools and Applications*, 84, 18829-18854. [Springer/DOI](https://doi.org/10.1007/s11042-024-19818-0).
5. Agarwal, M., Leekha, M., Sawhney, R., and Shah, R. R. (2020). “Crisis-DIAS: Towards Multimodal Damage Analysis—Deployment, Challenges and Assessment.” *AAAI 2020*, 346-353. [AAAI/DOI](https://doi.org/10.1609/aaai.v34i01.5369).
6. Imran, M., Alam, F., Qazi, U., Peterson, S., and Ofli, F. (2020). “Rapid Damage Assessment Using Social Media Images by Combining Human and Machine Intelligence.” [Official arXiv record](https://arxiv.org/abs/2004.06675).
7. Chen, Z., Shamsabadi, E. A., Jiang, S., Shen, L., and Dias-da-Costa, D. (2026). “Integration of Large Vision Language Models for Efficient Post-disaster Damage Assessment and Reporting.” *Nature Communications*, 17, 1481. [Nature/DOI](https://doi.org/10.1038/s41467-025-68216-z).
8. Cheng, H., Xiao, E., Gu, J., Yang, L., Duan, J., Zhang, J., Cao, J., Xu, K., and Xu, R. (2024). “Unveiling Typographic Deceptions: Insights of the Typographic Vulnerability in Large Vision-Language Model.” *ECCV 2024*. [ECVA paper](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07650.pdf).
9. Wang, X., Zhao, Z., and Larson, M. (2025). “Typographic Attacks in a Multi-Image Setting.” *NAACL 2025*, 12594-12604. [ACL Anthology/DOI](https://doi.org/10.18653/v1/2025.naacl-long.626).
10. Cao, Y. et al. (2025). “SceneTAP: Scene-Coherent Typographic Adversarial Planner against Vision-Language Models in Real-World Environments.” *CVPR 2025*, 25050-25059. [CVF paper](https://openaccess.thecvf.com/content/CVPR2025/html/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.html).
11. Deng, A., Cao, T., Chen, Z., and Hooi, B. (2025). “Words or Vision? Do Vision-Language Models Have Blind Faith in Text?” *CVPR 2025*, 3867-3876. [CVF paper](https://openaccess.thecvf.com/content/CVPR2025/html/Deng_Words_or_Vision_Do_Vision-Language_Models_Have_Blind_Faith_in_CVPR_2025_paper.html).
12. Downer, G., Craven, S., Ruck, D., and Thomas, J. (2025). “Text2VLM: Adapting Text-Only Datasets to Evaluate Alignment Training in Visual Language Models.” *PMLR*, 299, 28-41. [PMLR paper](https://proceedings.mlr.press/v299/downer25a.html).
13. Zhan, Q., Liang, Z., Ying, Z., and Kang, D. (2024). “InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents.” *Findings of ACL 2024*, 10471-10506. [ACL Anthology/DOI](https://doi.org/10.18653/v1/2024.findings-acl.624).
14. Qraitem, M., Teterwak, P., Saenko, K., and Plummer, B. A. (2025). “Web Artifact Attacks Disrupt Vision Language Models.” *ICCV 2025*, 1048-1057. [CVF paper](https://openaccess.thecvf.com/content/ICCV2025/html/Qraitem_Web_Artifact_Attacks_Disrupt_Vision_Language_Models_ICCV_2025_paper.html).
15. Wei, L., and Hutson, A. D. (2013). “A Comment on Sample Size Calculations for Binomial Confidence Intervals.” *Journal of Applied Statistics*. [DOI](https://doi.org/10.1080/02664763.2012.740629).
16. Lachin, J. M. (1992). “Power and Sample Size Evaluation for the McNemar Test with Application to Matched Case-Control Studies.” *Statistics in Medicine*, 11(9). [DOI](https://doi.org/10.1002/sim.4780110909).

Official model records: [Qwen3.5-27B](https://huggingface.co/Qwen/Qwen3.5-27B), [Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B), [Qwen3-VL-32B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-32B-Instruct), [Mistral Small 3.1 24B](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503), and [Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash).

The earlier FLLM citation and concurrent 2026 preprint are excluded from the core verified list because they are unnecessary to the paper's novelty argument and their metadata was not as cleanly established from a primary proceedings record during this audit.

## Appendix A — Canonical model provenance

| Paper label | Served ID | Precision/service | Main predictions | Canonical backend |
|---|---|---|---:|---|
| Qwen3.5 27B BF16 | `Qwen/Qwen3.5-27B` | BF16 | 7,200 | GCP A100 / CUDA-vLLM |
| Qwen3.6 27B BF16 | `Qwen/Qwen3.6-27B` | BF16 | 7,200 | GCP A100 / CUDA-vLLM |
| Qwen3-VL 32B BF16 | `Qwen/Qwen3-VL-32B-Instruct` | BF16 | 7,200 | GCP A100 / CUDA-vLLM |
| Mistral 24B BF16 | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | BF16 | 7,200 | GCP A100 / CUDA-vLLM |
| Gemini 2.5 Flash | `gemini-2.5-flash` | provider-managed | 7,200 | Gemini Batch API |

## Appendix B — Model-specific conditional downward ASR

Values condition on each model's clean-correct mild/severe cases; denominators are shown in the Results clean table.

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 43.67% | 14.29% | 42.45% | 18.78% | 11.02% | 22.45% |
| Qwen3.6 27B BF16 | 67.76% | 8.16% | 45.31% | 17.96% | 6.12% | 22.04% |
| Qwen3-VL 32B BF16 | 79.93% | 11.56% | 80.61% | 24.15% | 9.18% | 23.13% |
| Mistral 24B BF16 | 81.47% | 26.72% | 76.29% | 31.47% | 8.62% | 35.78% |
| Gemini 2.5 Flash | 24.91% | 16.12% | 64.84% | 17.58% | 15.75% | 28.57% |

## Appendix C — Model-specific clean confusion matrices

Each cell is an exact count out of 240 for its ground-truth row. Triples are predictions in `[little/no, mild, severe]` order.

| Model | Truth little/no | Truth mild | Truth severe |
|---|---|---|---|
| Qwen3.5 27B BF16 | `[156, 70, 14]` | `[83, 86, 71]` | `[62, 19, 159]` |
| Qwen3.6 27B BF16 | `[143, 76, 21]` | `[73, 86, 81]` | `[67, 14, 159]` |
| Qwen3-VL 32B BF16 | `[89, 135, 16]` | `[36, 136, 68]` | `[30, 52, 158]` |
| Mistral 24B BF16 | `[130, 109, 1]` | `[64, 172, 4]` | `[57, 123, 60]` |
| Gemini 2.5 Flash | `[120, 107, 13]` | `[65, 122, 53]` | `[63, 26, 151]` |

## Appendix D — Model-specific malicious transition counts

Counts include all clean-correct starting classes. Each triple is the attacked prediction count in `[little/no, mild, severe]` order. The little/no and mild rows expose severity increases; the mild and severe rows expose under-triage.

| Model | Condition | Clean little/no row | Clean mild row | Clean severe row |
|---|---|---|---|---|
| Qwen3.5 | Direct image | `[156, 0, 0]` | `[61, 19, 6]` | `[45, 1, 113]` |
| Qwen3.5 | Direct text | `[155, 1, 0]` | `[23, 62, 1]` | `[6, 6, 147]` |
| Qwen3.5 | Direct joint | `[154, 2, 0]` | `[50, 31, 5]` | `[54, 0, 105]` |
| Qwen3.5 | Misleading image | `[156, 0, 0]` | `[24, 60, 2]` | `[5, 17, 137]` |
| Qwen3.5 | Misleading text | `[156, 0, 0]` | `[17, 69, 0]` | `[1, 9, 149]` |
| Qwen3.5 | Misleading joint | `[156, 0, 0]` | `[29, 57, 0]` | `[7, 19, 133]` |
| Qwen3.6 | Direct image | `[143, 0, 0]` | `[77, 8, 1]` | `[87, 2, 70]` |
| Qwen3.6 | Direct text | `[143, 0, 0]` | `[17, 67, 2]` | `[2, 1, 156]` |
| Qwen3.6 | Direct joint | `[143, 0, 0]` | `[59, 20, 7]` | `[51, 1, 107]` |
| Qwen3.6 | Misleading image | `[143, 0, 0]` | `[25, 60, 1]` | `[5, 14, 140]` |
| Qwen3.6 | Misleading text | `[143, 0, 0]` | `[12, 73, 1]` | `[0, 3, 156]` |
| Qwen3.6 | Misleading joint | `[143, 0, 0]` | `[29, 55, 2]` | `[4, 21, 134]` |
| Qwen3-VL | Direct image | `[89, 0, 0]` | `[128, 8, 0]` | `[106, 1, 51]` |
| Qwen3-VL | Direct text | `[89, 0, 0]` | `[27, 106, 3]` | `[3, 4, 151]` |
| Qwen3-VL | Direct joint | `[89, 0, 0]` | `[121, 15, 0]` | `[116, 0, 42]` |
| Qwen3-VL | Misleading image | `[88, 1, 0]` | `[40, 96, 0]` | `[6, 25, 127]` |
| Qwen3-VL | Misleading text | `[89, 0, 0]` | `[19, 117, 0]` | `[0, 8, 150]` |
| Qwen3-VL | Misleading joint | `[88, 1, 0]` | `[38, 98, 0]` | `[5, 25, 128]` |
| Mistral | Direct image | `[130, 0, 0]` | `[139, 33, 0]` | `[46, 4, 10]` |
| Mistral | Direct text | `[129, 1, 0]` | `[60, 111, 1]` | `[1, 1, 58]` |
| Mistral | Direct joint | `[130, 0, 0]` | `[133, 39, 0]` | `[39, 5, 16]` |
| Mistral | Misleading image | `[130, 0, 0]` | `[61, 110, 1]` | `[2, 10, 48]` |
| Mistral | Misleading text | `[127, 3, 0]` | `[15, 156, 1]` | `[0, 5, 55]` |
| Mistral | Misleading joint | `[129, 1, 0]` | `[68, 103, 1]` | `[3, 12, 45]` |
| Gemini | Direct image | `[120, 0, 0]` | `[49, 63, 10]` | `[17, 2, 132]` |
| Gemini | Direct text | `[120, 0, 0]` | `[35, 81, 6]` | `[5, 4, 142]` |
| Gemini | Direct joint | `[120, 0, 0]` | `[93, 28, 1]` | `[78, 6, 67]` |
| Gemini | Misleading image | `[118, 2, 0]` | `[30, 92, 0]` | `[2, 16, 133]` |
| Gemini | Misleading text | `[118, 2, 0]` | `[29, 92, 1]` | `[3, 11, 137]` |
| Gemini | Misleading joint | `[120, 0, 0]` | `[47, 74, 1]` | `[5, 26, 120]` |

Exact source tables: `reports/v3/gcp_a100/models/*/main/{clean_confusion_matrix,severity_shift_matrix,attack_metrics,benign_adjusted_effects}.csv` and `reports/v3/final_analysis/models/gemini_2_5_flash/`.
