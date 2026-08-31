# Human visual audit — aggregate results

**Status:** Complete, 2026-08-31

**Scope:** 234 sampled rendered images; two independent human raters; all five
independent-pass disagreements adjudicated. De-identified rating exports are
available under [`ratings/`](ratings/); private source codes are not paper-facing.

## Design

Two independent human raters assessed 234 sampled rendered images while blinded
to model outputs, tweet text, and ground-truth severity labels.

The sample comprised 180 simple overlays from 60 main-cohort sources (benign,
direct, and misleading for each source) and 54 presentation-style overlays from
nine sources (direct and misleading under simple, news, and camouflage
rendering). The raters judged text readability, whether the text was completely
invisible, and whether the overlay obscured critical damage evidence. They used
`yes`, `no`, or `uncertain` and rated independently before adjudication.

## Independent-pass agreement

| Field | Raw agreement | Cohen's kappa | Interpretation |
|---|---:|---:|---|
| Text readability, three classes | 229/234 (97.9%) | 0.634 | Five disagreements, all on camouflage |
| Text readability, conservative binary collapse | 232/234 (99.1%) | 0.853 | `yes` versus `uncertain/no` |
| Text completely invisible | 234/234 (100%) | Not estimable | Both raters used only `no` |
| Critical damage obscured | 234/234 (100%) | Not estimable | Both raters used only `no` |

All five readability disagreements were adjudicated. The final decisions were
three `uncertain` and two `no`. Here, `uncertain` means that text was detectable
but its meaning could not be established confidently at the displayed size.

## Adjudicated outcomes

| Review slice | Images | Readable `yes` | `uncertain` | `no` | Readable rate, Wilson 95% CI |
|---|---:|---:|---:|---:|---:|
| Main simple overlays | 180 | 180 | 0 | 0 | 100% [97.91, 100] |
| Style supplement: simple | 18 | 18 | 0 | 0 | 100% [82.41, 100] |
| Style supplement: news | 18 | 18 | 0 | 0 | 100% [82.41, 100] |
| Style supplement: camouflage | 18 | 10 | 6 | 2 | 55.56% [33.72, 75.44] |
| **All reviewed overlays** | **234** | **226** | **6** | **2** | **96.58% [93.40, 98.26]** |

Across all 234 images, text was never judged completely invisible and critical
damage was never judged obscured. Thus the observed rates were 234/234 for text
remaining detectable (Wilson 95% CI 98.38–100) and 234/234 for critical damage
remaining unobscured (Wilson 95% CI 98.38–100).

## Paper interpretation

The audit supports a sample-bounded statement that the simple and news overlays
were readable and that none of the reviewed overlays covered critical damage.
It also reveals an important qualification: camouflage text was confidently
readable in only 10 of 18 reviewed images, with six uncertain and two unreadable
judgments after adjudication.

These findings do not change model predictions, attack success rates, or the
36/36 matched-control result. They address a narrower alternative explanation:
within the reviewed sample, the effect cannot be attributed to overlays simply
covering the decisive damage evidence. The audit does not establish realism,
stealth, plausibility, human susceptibility to the message, or performance over
every source and renderer used elsewhere in the study.
