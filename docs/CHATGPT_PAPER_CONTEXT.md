# ChatGPT paper handoff: current canonical context

**Snapshot date:** 2026-08-30  
**Target:** anonymous NeurIPS 2026 Trustworthy AI for Good (AI4GOOD) workshop  
**Active LaTeX root:** `manuscript/main.tex`  
**Status:** manuscript-ready in workshop mode; checklist is not required; not submission-ready until the open blockers below are resolved

## How to use this file

This is the compact, current handoff for an external ChatGPT drafting session.
It intentionally excludes superseded V2, 9B, 8-bit, 4-bit, pilot, deployment
gate, and historical prompt-development results. It is a dated operational
summary, not a replacement for the repository's frozen evidence.

When a claim or number is disputed, use this precedence:

1. accepted decisions D018--D037 in `docs/PAPER_DECISIONS.md`;
2. `reports/v3/ALL_RESULTS.md`;
3. `reports/v3/BF16_RUNTIME_DURATIONS.md`;
4. frozen result artifacts and executable configurations;
5. this handoff and the current manuscript;
6. `paper.md` only as a historical structural blueprint.

Do not silently reconcile conflicts. Report the conflict and identify the
higher-priority source.

## Fixed paper identity and scope

Title:

> When Disaster Images Talk Back: Cross-Modal Typographic Attacks on
> Vision--Language Models for Damage Assessment

Keep the existing seven-section order:

1. Introduction
2. Related work
3. Experimental design
4. Results
5. Discussion
6. Limitations and broader impact
7. Conclusion

The current panel contains six models:

- Qwen3.5 27B BF16;
- Qwen3.6 27B BF16;
- Qwen3.8 27B BF16;
- Qwen3-VL 32B BF16;
- Mistral Small 3.1 24B BF16;
- Gemini 2.5 Flash.

The five open models use the canonical GCP A100 80 GB, CUDA, vLLM, BF16
runtime. Gemini uses its hosted API. Cross-service differences must not be
interpreted causally.

The paper is a controlled, leakage-resistant, matched-control audit of
direction-sensitive typographic vulnerability in off-the-shelf VLM disaster
triage. It is not a model leaderboard, an operational deployment study, a new
classifier, an optimized attack, or a validated defense.

The current submission venue is the **NeurIPS 2026 Trustworthy AI for Good
(AI4GOOD) workshop**, not the main NeurIPS conference track. Use
`\usepackage[dblblindworkshop]{neurips_2026}` and
`\workshoptitle{Trustworthy AI for Good}`. Main content remains at most nine
pages. The NeurIPS paper checklist is **not required** and must not be
`\input` into the compiled PDF.

## Dataset and experiment accounting

| Count | Meaning | Paper use |
|---:|---|---|
| 18,082 | all CrisisMMD v2.0 images across annotation tasks | overall dataset scale only |
| 3,526 | published damage-severity rows | severity source population |
| 3,474 | locally valid exact-SHA-unique severity pairs | natural clean evaluation |
| 529 | published severity test rows | official-test clean evaluation |
| 720 | balanced V3 main, 240 per class | primary paired experiment |
| 120 | presentation-style cohort, 40 per class | secondary style analysis |
| 60 | relative-size cohort, 20 per class | secondary size analysis |
| 120 | disjoint text-rhetoric cohort | post-review secondary follow-up |
| 60 | disjoint point-size cohort | post-review secondary follow-up |

The main matrix has clean plus benign, direct, and misleading payloads in
image-only, text-only, and joint delivery modes: ten conditions and 7,200
predictions per model. Image and joint conditions reuse the same rendered image
for a given source and payload. Text and joint conditions preserve the original
tweet after a payload prefix.

The main cohort is custom, class-balanced, duplicate-cluster-disjoint, and not
a natural-prevalence or official-test sample. Event-by-class structural zeros
prevent causal or general disaster-type inference.

## Fixed prompt, metrics, and statistics

- The complete attack matrix uses one fixed zero-shot damage-assessment rubric
  with deterministic decoding. Internal candidate and version labels are
  eliminated from paper-facing use under D029.
- Do not narrate abandoned internal prompt candidates. State only that the
  attack matrix was not repeated under another prompt, so prompt dependence
  remains unresolved.
- The eligible denominator is the model-specific number of clean-correct
  mild/severe decisions.
- The paper-primary downward success rate is the number of eligible decisions
  shifted lower divided by all 720 main samples.
- Eligible-only downward ASR is a secondary conditional susceptibility metric.
- The primary matched-control effect is malicious minus modality-matched benign
  downward success, divided by 720.
- Report upward transitions and induced severe/critical under-triage in addition
  to downward success.
- Present the six malicious conditions as clean-to-attacked 3x3 transition
  matrices. Rows are initially correct clean labels; columns are attacked
  predictions. The six-model mean matrices are in `ALL_RESULTS.md` and
  `manuscript/figures/transition_matrices.pdf`.
- Use Wilson 95% intervals, 5,000 paired bootstrap draws with seed 42, exact
  two-sided McNemar tests, and Holm correction inside predeclared families.
- Analyze models separately. Never pool predictions as independent samples.

## Canonical main results

Attack columns below are full-cohort downward successes over all 720 main
samples, not attacked error rates and not eligible-only ASR.

| Model | Clean acc. | Macro-F1 | Eligible n/720 | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | 55.69% | 54.94% | 245/720 | 14.86% | 4.86% | 14.44% | 6.39% | 3.75% | 7.64% |
| Qwen3.6 27B BF16 | 53.89% | 53.17% | 245/720 | 23.06% | 2.78% | 15.42% | 6.11% | 2.08% | 7.50% |
| Qwen3.8 27B BF16 | 52.78% | 52.43% | 249/720 | 8.33% | 4.31% | 14.86% | 6.11% | 3.47% | 7.08% |
| Qwen3-VL 32B BF16 | 53.19% | 52.98% | 294/720 | 32.64% | 4.72% | 32.92% | 9.86% | 3.75% | 9.44% |
| Mistral 24B BF16 | 50.28% | 48.57% | 232/720 | 26.25% | 8.61% | 24.58% | 10.14% | 2.78% | 11.53% |
| Gemini 2.5 Flash | 54.58% | 54.85% | 273/720 | 9.44% | 6.11% | 24.58% | 6.67% | 5.97% | 10.83% |
| **Unweighted model mean** | **53.40%** | **52.82%** | **256.3/720** | **19.10%** | **5.23%** | **21.14%** | **7.54%** | **3.64%** | **9.01%** |

The six full-cohort malicious-minus-matched-benign risk differences are:

| Model | Direct image | Direct text | Direct joint | Misleading image | Misleading text | Misleading joint |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 27B BF16 | +13.61 pp | +4.31 pp | +12.92 pp | +5.14 pp | +3.19 pp | +6.11 pp |
| Qwen3.6 27B BF16 | +21.11 pp | +2.64 pp | +13.61 pp | +4.17 pp | +1.94 pp | +5.69 pp |
| Qwen3.8 27B BF16 | +6.53 pp | +4.17 pp | +13.33 pp | +4.31 pp | +3.33 pp | +5.56 pp |
| Qwen3-VL 32B BF16 | +31.25 pp | +4.17 pp | +31.39 pp | +8.47 pp | +3.19 pp | +7.92 pp |
| Mistral 24B BF16 | +23.75 pp | +8.06 pp | +21.67 pp | +7.64 pp | +2.22 pp | +8.61 pp |
| Gemini 2.5 Flash | +7.36 pp | +4.44 pp | +22.36 pp | +4.58 pp | +4.31 pp | +8.61 pp |
| **Unweighted model mean** | **+17.27 pp** | **+4.63 pp** | **+19.21 pp** | **+5.72 pp** | **+3.03 pp** | **+7.08 pp** |

All 36 malicious model-condition effects are positive, their full-cohort
bootstrap intervals exclude zero, and all corresponding Holm-adjusted McNemar
tests are significant. The magnitude and modality ordering are strongly
model-dependent; there is no universal image/text/joint ranking.

## Secondary analyses and follow-ups

Every reader-facing revision must cover all of these families at least once:

1. balanced main clean and paired main attack matrix;
2. natural-3,474 and official-test-529 clean characterization;
3. presentation-style-120 ablation;
4. relative-size-60 ablation;
5. descriptive disaster-type analysis;
6. text-rhetoric-120 follow-up;
7. point-size-60 follow-up.

Presentation style bundles layout, contrast, banner, and placement differences.
Simple/news presentation was often stronger than camouflage for direct
instructions. A separate 234-image blinded audit found all reviewed simple/news
overlays readable, mixed camouflage readability, and no critical-damage
occlusion. It did not assess realism, stealth, or plausibility.

Relative size does not show a universal monotonic law. Style and relative-size
eligible denominators are small and model-specific: approximately 28--37 and
13--21, respectively. Report counts and uncertainty.

The six-model text-rhetoric follow-up contains 1,080 parsed predictions per
model. Mean full-cohort downward success is 3.89% for exact-label direct,
3.61% for natural direct, 4.17% for plain misleading, and 4.03% for authority
misleading. None of the three within-model rhetoric contrasts is
Holm-significant across the panel: 0/18 tests.

The six-model point-size follow-up contains 960 parsed predictions per model.
Direct-attack model means at nominal 3/6/9/12/15 pt are
1.67/2.22/5.83/11.94/13.61%; misleading means are
1.39/2.78/5.83/7.22/6.94%. None of the eight within-model contrasts is
Holm-significant across the panel: 0/48 tests. The descriptive aggregate rise
does not establish a deterministic within-model monotonic law.

Disaster-type results are descriptive only. Event, class, and disaster type are
confounded; flood estimates have especially small eligible denominators. Do not
rank disaster types as intrinsically safe or unsafe.

## Runtime accounting

The following durations are inference request spans; they exclude checkpoint
download, model loading, and analysis:

| Model | Main | Style | Relative size | Natural clean | Official clean |
|---|---:|---:|---:|---:|---:|
| Mistral 24B BF16 | 4h 22m | 47m | 23m | 2h 13m | 20m |
| Qwen3.5 27B BF16 | 5h 58m | 1h | 30m | 2h 53m | 26m |
| Qwen3.6 27B BF16 | 5h 53m | 59m | 29m | 2h 51m | 26m |
| Qwen3.8 27B BF16 | 6h 52m | 1h 08m | 34m | 3h 17m | 30m |
| Qwen3-VL 32B BF16 | 6h 58m | 1h 10m | 34m | 3h 28m | 32m |

The five open-model core request spans sum to 54h 33m. Follow-up spans are:

| Model | Text rhetoric | Point size |
|---|---:|---:|
| Qwen3.5 27B BF16 | 53m 32s | 47m 58s |
| Qwen3.6 27B BF16 | 52m 43s | 47m 14s |
| Qwen3.8 27B BF16 | 59m 33s | 54m 48s |
| Qwen3-VL 32B BF16 | 1h 04m 45s | 56m 21s |
| Mistral 24B BF16 | 36m 31s | 37m 16s |

Gemini timing and a complete inventory of preliminary, failed, and total
project compute are unavailable. The NeurIPS compute-checklist answer must
remain cautious and currently remains `No`.

## Supported claims

- Fixed malicious image, text, and joint messages can induce safety-relevant
  downward shifts among initially correct mild/severe decisions.
- Malicious effects exceed modality-matched benign instability in all 36
  primary model-condition comparisons.
- Visual and joint delivery can be much more harmful than accompanying-text
  delivery, but the ordering is model-dependent.
- Direct instructions are generally more damaging than misleading claims, but
  misleading effects remain positive and significant against matched controls.
- Clean competence and conditional robustness are separate; 50.28--55.69%
  balanced-main accuracy is not evidence of operational readiness.
- Presentation and size alter vulnerability, but neither a universal style
  ranking nor a universal monotonic size law is supported.

## Prohibited or unsupported claims

Do not claim:

- operational disaster-response readiness;
- a universal model leaderboard or causal effect of architecture, scale,
  precision, backend, or runtime;
- universally stronger joint attacks;
- universally monotonic text-size effects;
- realistic, stealthy, plausible, universally readable, universally
  non-occluding, or generically “human-approved” overlays;
- causal or generalizable disaster-type differences;
- external-dataset or real-world emergency-response outcomes;
- an empirically validated mitigation;
- first-of-kind novelty without a systematic review;
- prompt invariance;
- complete Gemini or total-project compute accounting.

## Open submission blockers

- Keep the completed 234-image human audit sample-bounded; do not expand it into
  realism, stealth, or plausibility claims.
- Verify immutable model revisions and final environment locks.
- Verify CrisisMMD and model licenses and the anonymous archive/release plan.
- Complete Gemini and total-project compute accounting if possible.
- Perform the final ethics, privacy, anonymity, citation, denominator, page,
  font, and archive checks.

The human audit is complete and does not alter the numerical attack results.
Its aggregate evidence is in `reports/v3/manual_review/RESULTS.md`; private raw
rating files and internal rater codes are not paper-facing.

## Private visual examples

Selected generated overlays exist locally under
`reports/private/visual_examples/`, including benign/direct/misleading main
triplets, simple/news/camouflage style variants, and small/medium/large size
variants. This directory is gitignored.

Under D025, a **small composed subset** may appear in the anonymous paper PDF
only:

- main Method figure: `main_california_918115` benign/direct/misleading;
- appendix: `style_harvey_904606` and `size_harvey_904429`.

Composed JPEG copies live in `manuscript/figures/`. Captions must call them
generated examples and must not claim realism or stealth. Sample-bounded
readability and critical-non-occlusion results belong to the aggregate audit,
not to any unverified individual illustration. Do not upload the private
directory, raw tweets, or extra overlays into a public or anonymous archive.

## LaTeX editing contract for ChatGPT

- Edit the actual source rooted at `manuscript/main.tex`; use no obsolete
  manuscript path from earlier drafts.
- Preserve the paper title, seven-section order, anonymous workshop
  submission mode (`dblblindworkshop`), `\workshoptitle{Trustworthy AI for Good}`,
  and the unmodified `neurips_2026.sty`.
- Do not `\input{checklist.tex}`; AI4GOOD does not require the NeurIPS checklist.
- Prefer one overlay figure and the existing main-effects plot over extra
  protocol equations in the main text.
- Preserve valid `\label`, `\ref`, `\cite`, `\citep`, and bibliography keys.
- Use LaTeX syntax, not Markdown tables, inside `.tex` files.
- Do not mention internal study versions (V2/V3), retired 9B/quantized/MLX
  runs, or decision IDs (D018--) in reader-facing manuscript prose. Keep that
  history in `docs/PAPER_DECISIONS.md`.
- Do not introduce a citation key unless it is also defined in
  `manuscript/references.bib` from a verified source.
- Keep full-cohort `n/720` downward success primary; place eligible-only ASR
  detail in the appendix or explicitly label it secondary.
- Keep the main content at or below nine pages. Move conditional detail,
  model-level matrices, disaster detail, and full follow-up tables to the
  appendix when necessary.
- Return changes as a unified diff, one target file per response. Explain any
  unresolved evidence conflict instead of guessing.
- Do not edit generated files such as `main.pdf`, `main.aux`, `main.bbl`,
  `main.blg`, or `main.out`.

## Required ChatGPT workflow

First request an audit only. The audit must list:

| File/section | Current issue | Canonical evidence | Proposed correction | Confidence/blocker |
|---|---|---|---|---|

Do not permit edits during the audit step. After reviewing the audit, request
one `.tex` file at a time. Require a unified diff and recompile after every
small batch.

Suggested first prompt:

```text
Treat docs/CHATGPT_PAPER_CONTEXT.md as the current compact handoff.
Audit the supplied LaTeX manuscript for scientific, numerical, citation,
cross-section, and workshop-format inconsistencies. The venue is AI4GOOD;
do not require the NeurIPS checklist. Do not edit yet. Return only a
table with file/section, current issue, canonical evidence, proposed correction,
and confidence or blocker. Do not invent missing evidence.
```

Suggested edit prompt after the audit:

```text
Edit only manuscript/sections/04_results.tex for the approved audit items.
Preserve the existing section structure, labels, citations, and NeurIPS style.
Use full-cohort n/720 downward success as primary and eligible-only ASR as
secondary. Return only a unified diff. Do not change any other file and do not
invent missing results.
```

## Current manuscript file map

- `manuscript/main.tex`: entry point and abstract;
- `manuscript/sections/01_introduction.tex`;
- `manuscript/sections/02_related_work.tex`;
- `manuscript/sections/03_method.tex`;
- `manuscript/sections/04_results.tex`;
- `manuscript/sections/05_discussion.tex`;
- `manuscript/sections/06_limitations.tex`;
- `manuscript/sections/07_conclusion.tex`;
- `manuscript/sections/appendix.tex`;
- `manuscript/references.bib`;
- `manuscript/neurips_2026.sty` (must remain unmodified);
- `manuscript/figures/` (composed overlay JPEGs and `main_effects.pdf`);
- `manuscript/checklist.tex` exists but is **not compiled** for AI4GOOD.

## Local verification after every revision

From the repository root:

```bash
cd manuscript
tectonic main.tex --keep-logs --keep-intermediates
pdfinfo main.pdf
Run a stale-string scan over the active manuscript and writing handoffs for
obsolete model counts, effect totals, and retired manuscript paths before export.
rg -n 'undefined|Undefined control sequence|Fatal error|Emergency stop|Overfull' main.log
```

Acceptance conditions:

- no undefined citation or reference;
- no fatal LaTeX error;
- no overfull table that changes interpretation;
- main content ends by page 9;
- all fonts are embedded;
- all six models, all seven analysis families, and post-review follow-ups appear
  in at least one reader-facing section;
- human-audit sample limits and unresolved licensing/archive, Gemini timing,
  and total-compute gaps remain explicit rather than being filled by assumption.
