# Human evaluation for this paper

**Status:** Completed 2026-08-31 under D036 and D037.

**Operational protocol:**
[`reports/v3/manual_review/PROTOCOL.md`](../reports/v3/manual_review/PROTOCOL.md)

**Aggregate results:**
[`reports/v3/manual_review/RESULTS.md`](../reports/v3/manual_review/RESULTS.md)

**De-identified audit exports:**
[`reports/v3/manual_review/ratings/`](../reports/v3/manual_review/ratings/)

## Purpose and scope

The model experiment is a digital paired intervention: it tests whether fixed
text can redirect a VLM's damage-severity decision. The human audit asks a
different, narrower question about the generated stimuli. It checks whether the
overlay can be read, whether it disappears completely, and whether it physically
covers the damage evidence that the model should inspect.

It does not ask people to predict damage labels, judge whether they believe the
message, or validate the model's answers. It therefore does not alter the primary
full-cohort estimand, eligible denominators, or 36/36 matched-control finding.

## Frozen design

Two independent human raters assessed 234 sampled rendered images while blinded
to model outputs, tweet text, and ground-truth severity labels.

- 180 main overlays: 60 sources × benign/direct/misleading simple rendering.
- 54 style overlays: nine sources × direct/misleading × simple/news/camouflage.
- Three ratings per image: `text_readable`, `text_completely_invisible`, and
  `critical_damage_obscured`.
- Allowed answers: `yes`, `no`, and `uncertain`.
- Independent rating came first; all disagreements were adjudicated afterward.

D036 retired the earlier 303-item, eight-field proposal before any ratings were
recorded. The retired fields would mainly have supported realism or plausibility
claims that this paper does not make. They must not be revived or mixed with the
completed three-field audit.

## Observed results

Before adjudication, the raters agreed on text readability for 229/234 images
(97.9%; three-class Cohen's kappa 0.634). Under the conservative binary collapse
of readable `yes` versus `uncertain/no`, agreement was 232/234 (99.1%; kappa
0.853). They agreed on every invisibility and critical-obscuration rating; kappa
is not estimable for those fields because both raters used only `no`.

After all five readability disagreements were adjudicated:

| Slice | Readable `yes` | `uncertain` | `no` |
|---|---:|---:|---:|
| Main simple | 180/180 | 0 | 0 |
| Style simple | 18/18 | 0 | 0 |
| Style news | 18/18 | 0 | 0 |
| Style camouflage | 10/18 | 6/18 | 2/18 |
| **All reviewed images** | **226/234** | **6/234** | **2/234** |

No reviewed overlay was judged completely invisible or to obscure critical
damage (both 234/234 in the desired direction). Wilson intervals and the full
aggregate table are reported in `RESULTS.md`.

## What the paper may now say

- All 180 reviewed main simple overlays were readable at the displayed size.
- All 36 reviewed simple/news style overlays were readable.
- Camouflage readability was mixed: 10/18 yes, six uncertain, and two no.
- None of the 234 reviewed overlays covered critical damage evidence.
- These statements apply only to the sampled rendered images.

The paper must still avoid describing the overlays as realistic, stealthy,
plausible, human-undetectable, physically robust, or universally non-occluding.
The audit did not test exact transcription, message credibility, human deception,
relative-height or point-size families, or every image in the 720-source cohort.

## Paper-facing identity rule

Report the participants only as “two independent human raters.” The repository
exports use the neutral pseudonyms `reviewer-1` and `reviewer-2`; these labels do
not enter the manuscript. Do not publish names, initials, internal source codes,
discarded pilot ratings, or private originals. Unless separately documented, do
not invent demographic expertise, compensation, institutional affiliation, or
recruitment details.
