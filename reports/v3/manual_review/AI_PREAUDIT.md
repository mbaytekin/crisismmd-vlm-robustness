# AI-only visual pre-audit (not human validation)

**Status:** coordinator diagnostic; **not a human result, not paper evidence, and
not a replacement for the two-blinded-reviewer protocol**.

## Scope and grain

The frozen visual-review package contains 303 rows and 303 distinct image
paths: 60 main sources × four images (clean, benign, direct, misleading) and
9 style sources × seven images (clean plus direct/misleading simple, news, and
camouflage). All 303 paths opened successfully after pulling only the selected
files from the already-running GCP VM. The 69 clean references were used as
the visual baseline; the rates below are for attacked images only.

I inspected every contact-sheet cell at the image level. The rating unit is
one rendered image, not one model prediction. The three main attack messages
are visually distinct but preserve the same source image; they therefore do
not represent 180 independent source scenes.

## Descriptive observations

These are my own AI visual judgements, recorded to guide the coordinator before
human review. Wilson intervals are descriptive only and must not be reported as
human uncertainty intervals.

| Slice | n | Text readable | Text completely invisible | Text too obvious | Critical damage not obscured | Image usable |
|---|---:|---:|---:|---:|---:|---:|
| Main simple (benign/direct/misleading) | 180 | 180/180 (100%; Wilson 97.9–100.0) | 0/180 (0%; 0.0–2.1) | 180/180 (100%; 97.9–100.0) | 180/180 (100%; 97.9–100.0) | 180/180 (100%; 97.9–100.0) |
| Style simple | 18 | 18/18 (100%; 82.4–100.0) | 0/18 (0%; 0.0–17.6) | 18/18 (100%; 82.4–100.0) | 18/18 (100%; 82.4–100.0) | 18/18 (100%; 82.4–100.0) |
| Style news | 18 | 18/18 (100%; 82.4–100.0) | 0/18 (0%; 0.0–17.6) | 18/18 (100%; 82.4–100.0) | 18/18 (100%; 82.4–100.0) | 18/18 (100%; 82.4–100.0) |
| Style camouflage | 18 | 0/18 (0%; 0.0–17.6) | 18/18 (100%; 82.4–100.0) | 0/18 (0%; 0.0–17.6) | 18/18 (100%; 82.4–100.0) | 18/18 (100%; 82.4–100.0) |

### Interpretation

- The main and simple/news packages are visibly legible digital banners in this
  sample. That is a stimulus-quality observation, not evidence that humans in
  general will read them or that the intervention is realistic.
- Camouflage is effectively unreadable in all 18 inspected style attack images,
  while the underlying photographs remain usable and the decisive damage is
  still visible. This supports describing camouflage as a low-salience visual
  package; it does **not** support “stealth,” “human-undetectable,” or realism
  claims.
- No image-level critical-damage occlusion was apparent under this rubric. This
  is an AI pre-audit of a stratified subsample, not a non-occlusion result for
  all 720 sources.

## What this does and does not change

This report does not fill `RESULTS_TEMPLATE.md`, does not create reviewer
agreement or kappa values, and does not unlock any manuscript perceptual claim.
The independent human pass must remain blind to this report until both raters
finish. Human reviewers still need to rate the frozen CSV, resolve
disagreements, and provide raw agreement, three-class kappa, binary kappa, and
adjudicated Wilson intervals according to `PROTOCOL.md` and
`docs/HUMAN_EVALUATION.md`.

The AI pre-audit is useful for catching obvious rendering failures and for
setting coordinator expectations. It cannot establish original-label validity,
presentation plausibility, human readability, or reviewer quality.

