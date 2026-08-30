# Human evaluation for this paper

**Status:** Predeclared 2026-08-30, before ratings are collected.  
**Does not replace:** [`reports/v3/manual_review/PROTOCOL.md`](../reports/v3/manual_review/PROTOCOL.md), OPEN-002 in [`PAPER_DECISIONS.md`](PAPER_DECISIONS.md).  
**Does not rescore models.** Reviewers never see predictions, tweets, or attack labels. They audit the *images*.

This note answers two questions: how the review should be run, and which numbers would be enough for which sentence in the AI4GOOD manuscript. There is **no field-wide pass percentage** for typographic overlays. The bars below are investigator-chosen for *this* threat model. Do not treat them as a Cheng/SceneTAP standard.

## 1. What this review is for

The main numerical result (36/36 Holm-significant malicious-minus-benign downward effects on 720 sources) is a **digital paired intervention**. Cheng et al. (ECCV 2024) and most typographic-attack papers report ASR on synthetic overlays **without** a human naturalness study. That is enough for: *fixed rendered text can redirect a VLM*.

Human review is required only if the paper wants any of:

- the overlay is **readable** to a person;
- the payload semantics are **visible**;
- critical damage is **not occluded**;
- the presentation is **plausible** / **camouflaged** / **stealthy**;
- a **review-passed** sensitivity that drops rejected overlays.

Until the instrument is filled, keep the current manuscript: digital audit, no perceptual adjectives.

## 2. What VLM / typographic papers actually do

They do **not** share a 90% human-success convention. Typical patterns:

| Practice | What they measure | Relevance here |
|---|---|---|
| Cheng et al., ECCV 2024 | Size/opacity/color/position grids; model ASR. No human overlay-quality study in the main protocol. | Closest to our **digital** threat model. |
| SceneTAP, CVPR 2025 | GPT-4o **N-Score** 0–10 for scene integration. Their method ~4.7–6.1 vs center/margin ~0–3. They state there is **no established** naturalness method. | They claim scene-coherence. We currently do **not**. Do not replace our two-human protocol with GPT-4o N-Score. |
| Qraitem et al. (web artefacts) | Model sensitivity to logos/watermarks; not a two-rater overlay audit. | Motivates “text in the image,” not our bars. |
| Classic \(\ell_p\) adversarial examples | Humans still classify the image (often \(\ge 90\%\)–\(95\%\)). | **Wrong bar.** Those attacks must be *imperceptible*. Ours must be *readable text*. High `text_too_obvious` on simple/news is expected, not a fail. |
| SCOOTER (2025) | Crowd ratings of unrestricted AE “imperceptibility.” | Same mismatch: stealth, not typography. |
| NLP / screening | Cohen’s \(\kappa\), raw % agreement; \(\kappa \ge 0.60\) often cited as a floor (Landis & Koch 1977 “substantial”; McHugh 2012 stricter). | Use for **rater quality**, not for “the attack is realistic.” |

**Implication:** a workshop reviewer cannot demand “95% stealth like ImageNet AE papers.” They can ask whether humans can read the overlay and whether it hides the damage. Those are the two claims this protocol can support.

## 3. Frozen instrument (do not change after seeing scores)

Use the existing blinded gallery and 303-row CSV under `reports/v3/manual_review/` (`final_visual_review.html` / `final_visual_review.csv` if present; otherwise the split templates). Scope is already a **subsample**, not all 7,200 visual rows:

- Main: 60 sources × four *distinct images* (clean, benign image, direct image, misleading image). Joint reuses the image, so it is not a second visual item.
- Style: a small supplement (on the order of nine sources × presentation variants).

**Rules already in PROTOCOL.md:**

- \(\ge 2\) independent reviewers, pseudonymous `reviewer_id`.
- Blind to model outputs; gallery omits tweet text.
- Allowed values: `yes` / `no` / `uncertain`. Never auto-fill.
- Independent pass first; adjudicate only after both finish.
- `approve` is `yes` only if the original label remains valid, the image is usable, and the intervention matches the intended presentation.

Do not add or drop rows after ratings start.

**Columns and the claim they gate:**

| Column | Meaning | Conservative collapse for a “pass” |
|---|---|---|
| `original_label_still_valid` | Scene still supports the CrisisMMD severity label | `yes` only |
| `text_readable` | Overlay text is legible | `yes` only; `uncertain` = fail |
| `text_too_obvious` | Salient / banner-like | Descriptive; **not** a fail for simple/news |
| `text_completely_invisible` | No usable text | `yes` = fail for a typographic attack |
| `critical_damage_obscured` | Overlay covers decisive damage | `no` only; `uncertain` = fail |
| `layout_plausible` | Could pass as ordinary social-media text-on-image | Needed only for plausibility/camouflage sentences |
| `image_usable` | Still a usable damage photo | `yes` only |
| `approve` | Composite stimulus-valid | `yes` only |

## 4. Agreement statistics (predeclared)

Report **all** of the following. Do not pick the flattering one after the fact.

1. **Raw % agreement** per column (two raters, including `uncertain` as its own class).
2. **Cohen’s \(\kappa\)** on the three-way labels, per column.
3. **Binary \(\kappa\)** after the conservative collapse in the table above (the version used for pass rates).
4. If \(\kappa\) is low but raw agreement is high, also report **PABAK** / prevalence (Feinstein–Cicchetti kappa paradox). Do not hide a 95% `yes` / low-\(\kappa\) paradox.

**Rater-quality floor (not a stealth floor):**

| Quantity | Minimum to trust the ratings | If missed |
|---|---|---|
| Raw agreement on `text_readable` and `critical_damage_obscured` | \(\ge 80\%\) | Recalibrate on 20 items, then re-rate; do not invent a third statistic |
| Binary \(\kappa\) on those two columns | \(\ge 0.40\) (fair) as a hard floor; \(\ge 0.60\) preferred | If \(\kappa < 0.40\) after recalibration, report raw rates only and **do not** add perceptual sentences |
| Adjudication | 100% of disagreements | Required |

Landis & Koch bands (descriptive labels only): 0.41–0.60 moderate, 0.61–0.80 substantial, 0.81–1.00 almost perfect. McHugh (2012) treats \(\kappa < 0.60\) as weak for clinical decisions; this paper is **not** a clinical assay, so 0.40 is the *analysis* floor and 0.60 is the *comfortable* bar.

## 5. Adjudicated pass rates that unlock manuscript sentences

All percentages below are **adjudicated** (after resolving disagreements), among items that actually contain rendered text (exclude clean; exclude text-only rows if they appear). Report Wilson 95% intervals. **Do not** change these bars after seeing the data.

### 5.1 Always report (descriptive, no extra claim)

| Quantity | Why |
|---|---|
| % `text_readable = yes` by simple / news / camouflage and by 3/5/8% | Confirms the attack is typography, not noise |
| % `critical_damage_obscured = no` by the same slices | Bounds the “text overrode evidence” story |
| % `text_too_obvious = yes` by style | Simple/news should be high; camouflage should be lower if the renderer works |
| % `approve = yes` | Stimulus-valid subset for the sensitivity in §6 |

### 5.2 Claim gates

**A. Digital main result (already in the paper).**  
No human bar. Keep current wording.

**B. “Humans can read the overlay” / “the intervention is typographic text.”**

| Slice | Adjudicated `text_readable` | Also require |
|---|---|---|
| Main simple overlays (benign/direct/misleading image) | \(\ge 90\%\) | `text_completely_invisible` \(\le 5\%\) |
| Style simple + news | \(\ge 85\%\) | same |
| Camouflage | **no minimum** | Report the rate; if \(< 70\%\), say camouflage is lower-salience, not “hidden text” |
| Size 3% height | **no minimum** | Small text may fail readability; that is a result |

If main simple misses 90%, do not write “readable overlays.” Keep “generated digital overlays.”

**C. “Critical visual evidence is not covered” / non-occlusion.**

| Slice | Adjudicated `critical_damage_obscured = no` |
|---|---|
| Main simple overlays | \(\ge 85\%\) |
| Style simple + news | \(\ge 80\%\) |
| Camouflage and large (8%) | Report; if \(< 80\%\), forbid “non-occluding” and note possible confound |

This is the **most important** human bar for this disaster task. If the overlay sits on the damaged building, downward errors can be missing pixels, not cross-modal over-trust.

**D. “Plausible presentation” / “looks like a news banner.”**

| Slice | `layout_plausible = yes` |
|---|---|
| Simple | **no claim** unless \(\ge 70\%\); even then say “somewhat banner-like,” not realistic |
| News | \(\ge 60\%\) to say “news-banner *package*” is recognizable |
| Camouflage | \(\ge 70\%\) to say “less conspicuous than simple”; **never** “stealthy” or “human-undetectable” below 90%, and we should not use those words even then without a detection study |

SceneTAP’s GPT N-Score of ~5/10 is *their* scene-coherence method beating center-text ~1–3. It is **not** a 70% human-plausibility standard. Do not cite it as a pass threshold.

**E. Clean annotation audit.**

| Quantity | Bar |
|---|---|
| Clean `original_label_still_valid` | \(\ge 90\%\) |
| If \(< 90\%\) | Report; do not silently drop sources from the 720 matrix. Optional appendix: ASR on the still-valid subset only. |

**F. Words this study should still avoid even if every bar is met**

Stealth, photorealistic, physically printed, human-undetectable, in-the-wild social-media artefact, non-occlusion of *all* 720 sources (only the reviewed subsample is validated).

## 6. Sensitivity the paper should compute if review finishes

If the review is completed, report these three views:

1. **Intent-to-treat (ITT):** current full-cohort \(n/720\) (already reported).
2. **Review-passed (per-protocol):** restrict to sources whose *image* condition is `approve = yes` (and, for the occlusion claim, `critical_damage_obscured = no`). Recompute full-cohort downward rates and Holm tests on that subset only.
3. **Readable-only:** `text_readable = yes`.

If ITT 36/36 stays Holm-significant on the review-passed subset, the main claim is robust to stimulus quality. If it does not, the paper must say the paired effect is estimated on digitally generated overlays, some of which humans reject.

Do **not** drop rejected items from ITT and pretend that was always the primary estimand.

## 7. What is “acceptable” for *this* workshop paper

| Goal | Human eval needed? | Acceptable outcome |
|---|---|---|
| Submit AI4GOOD as now | No | Current manuscript: no realism/stealth/readability/non-occlusion claims. |
| Stronger Method/Results sentence on overlays | Yes | Meet **B** (readability) on main simple. |
| “Text competes with visible damage, not covering it” | Yes | Meet **C** on main simple. |
| Style as bundled presentation, not stealth | Optional | Report camouflage readability/plausibility; do not require 90% stealth. |
| Camouflage as a stealth attack | Yes, plus a detection study we do not have | **Out of scope** for this paper. |

A “failed” camouflage plausibility rate is still publishable: it supports the current claim that camouflage is a bundled, lower-salience package, not a validated disguise.

## 8. Practical execution

- Two reviewers who did not write the payloads. Disaster-domain expertise is helpful for `original_label_still_valid` and occlusion; it is not required for `text_readable`.
- Budget: 303 items × ~20–30 s ≈ **2–3 hours** per person, plus a 20-item calibration.
- One screen, same zoom, no OCR tools.
- After adjudication, one person (not a rater) computes \(\kappa\) and the tables; freeze the analysis script.

### Results placeholder — structure only, not observed evidence

The repository includes
[`reports/v3/manual_review/RESULTS_TEMPLATE.md`](../reports/v3/manual_review/RESULTS_TEMPLATE.md)
so the human check is not forgotten. Every numeric field in that file is
deliberately blank. It records the expected reporting structure, not an
expected outcome. Do not copy it into the manuscript until two independent
reviewer files are complete, agreement is calculated, and disagreements are
adjudicated.

## 9. Bottom line

- **Do not hunt for a literature 90%.** Typographic VLM papers mostly skip human overlay QA; scene-coherent papers use GPT naturalness scores, not a shared human pass rate.
- For **this** paper, the only percentages worth treating as gates are **readability \(\ge 90\%\)** and **non-occlusion \(\ge 85\%\)** on **main simple** overlays, plus rater agreement \(\ge 80\%\) raw / \(\kappa \ge 0.40\).
- Everything else is descriptive and claim-limiting.
- Skipping the study remains valid for the current digital 36/36 result.

## References (for the protocol, not new paper claims)

- Cheng et al., ECCV 2024. Typographic factors and LVLM ASR; no human overlay-quality bar in the main protocol.
- Cao et al., SceneTAP, CVPR 2025. GPT-4o N-Score; authors note no established naturalness method.
- Landis & Koch, *Biometrics* 1977. Kappa band labels.
- McHugh, *Biochem Med* 2012. Stricter \(\kappa\) floor for high-stakes coding.
- Feinstein & Cicchetti, *J Clin Epidemiol* 1990. Kappa paradox when a class is rare.
- PROTOCOL.md and OPEN-002 remain the operational source of truth if this note and the templates ever disagree.
