# V3 human visual-audit protocol

**Status:** Completed on 2026-08-31. Aggregate results are in
[`RESULTS.md`](RESULTS.md). De-identified independent exports and adjudication
are retained under [`ratings/`](ratings/); private source codes remain excluded.

Two independent human raters assessed 234 sampled rendered images while
blinded to model outputs, tweet text, and ground-truth severity labels. The
sample contained:

- 180 main-cohort overlays: 60 sources, each shown with benign, direct, and
  misleading simple overlays;
- 54 presentation-style overlays: nine sources, each shown with direct and
  misleading payloads under simple, news, and camouflage rendering.

The raters independently answered three questions with `yes`, `no`, or
`uncertain`:

1. `text_readable`: Can the displayed text be read confidently at the provided
   display size?
2. `text_completely_invisible`: Is the added text impossible to locate?
3. `critical_damage_obscured`: Does the overlay cover visual evidence needed to
   judge damage severity?

No OCR, zoom, model output, tweet text, or severity label was available during
rating. The independent pass was completed before comparison. Every
disagreement was then resolved jointly. For adjudication, `uncertain` denotes
detectable text whose meaning could not be established confidently at the
displayed size; it is kept separate from both `yes` and `no` in the final table.

The report gives raw agreement and Cohen's kappa where estimable. Kappa is left
undefined when both raters use only one category, because perfect raw agreement
under a saturated class does not yield an informative chance-corrected value.
Wilson 95% intervals accompany the final proportions.

This audit concerns the sampled rendered images. It does not re-score model
predictions, replace the 720-source intent-to-treat analysis, or establish
realism, stealth, plausibility, exact transcription, or universal non-occlusion.
