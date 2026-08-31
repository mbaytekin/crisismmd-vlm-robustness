# De-identified human-rating exports

This directory contains the two complete independent rating exports and the
five-row adjudication record used to produce `../RESULTS.md`.

- `human_review__reviewer-1.csv`: 234 independently rated images.
- `human_review__reviewer-2.csv`: the same 234 images, rated independently.
- `ADJUDICATION.csv`: final resolution of all five field-level disagreements.

`reviewer-1` and `reviewer-2` are repository-only pseudonyms. Their numbering
has no temporal, quality, or exclusion meaning and is not used in the paper.
The exported rating values, sample identifiers, conditions, relative image
paths, and notes are unchanged; only the private source rater codes were
replaced. The files contain no model outputs, tweet text, ground-truth severity
labels, personal names, contact details, or API credentials.

The manuscript reports participants in aggregate as “two independent human
raters.” Use `../RESULTS.md` for the paper-facing statistics and claim limits.
