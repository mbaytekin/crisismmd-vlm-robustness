# Current paper and release checklist

This is the living checklist for the completed six-model CrisisMMD robustness
paper. The accepted decision record is
[`docs/PAPER_DECISIONS.md`](PAPER_DECISIONS.md); the canonical numbers are in
[`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md). Historical
candidate screens, quantized runs, deployment gates, and abandoned prompt
proposals are not paper-facing evidence.

## Completed empirical work

- [x] Six-model main matrix: 720 sources, clean plus nine paired conditions.
- [x] Natural clean (3,474) and official clean (529) characterization.
- [x] Presentation-style (120) and relative-size (60) secondary analyses.
- [x] Descriptive disaster-type tables with event/class confounding caveat.
- [x] Text-rhetoric follow-up for all six models: 0/18 corrected contrasts.
- [x] Nominal point-size follow-up for all six models: 0/48 corrected contrasts.
- [x] Full-cohort downward and upward rates, matched-benign effects, severe and
  critical under-triage, and transition summaries.
- [x] Six clean-to-attacked 3x3 mean transition matrices in
  `manuscript/figures/transition_matrices.pdf`.

## Current manuscript checks

- [x] Primary downward estimand is the exact success count divided by all 720
  sources; eligible-only ASR is explicitly secondary.
- [x] Six-model panel and all 36 main matched-control effects are synchronized.
- [x] Generated overlay captions do not claim realism, stealth, or plausibility;
  readability and non-occlusion are stated only for the audited sample.
- [x] The completed aggregate human-audit report is frozen at
  `reports/v3/manual_review/RESULTS.md`; private rater files remain gitignored.
- [ ] Add exact primary `n/720` cells and full-cohort risk-difference intervals
  to the appendix if they are needed for camera-ready auditability.
- [ ] Add complete model-specific 3x3 count matrices when the corresponding
  canonical prediction artifacts are available; do not infer missing cells
  from rounded means.
- [ ] Expand the point-size appendix metadata with realized pixels, relative
  height, line count, occupied area, and renderer details from the frozen
  artifact record.

## Human visual review gate

- [x] Freeze the exact 234-image blinded gallery and sampled image list.
- [x] Collect two independent passes using only `yes`, `no`, or `uncertain`.
- [x] Compute raw agreement, three-class kappa, conservative binary kappa, and
  adjudicated rates; resolve all five disagreements.
- [x] Preserve the original 720-source intent-to-treat analysis. The narrowed
  D036 protocol has no composite `approve` field and therefore defines no
  review-passed model subset.
- [x] Add only sample-bounded readability and critical-non-occlusion findings;
  continue to prohibit realism, stealth, and plausibility claims.

Detailed instructions and claim gates are in
[`docs/HUMAN_EVALUATION.md`](HUMAN_EVALUATION.md) and
[`reports/v3/manual_review/PROTOCOL.md`](../reports/v3/manual_review/PROTOCOL.md).

## Release gate

- [ ] Verify immutable model revisions and environment locks.
- [ ] Verify CrisisMMD/model licenses and the anonymous archive contents.
- [ ] Confirm no raw tweets, raw images, model weights, caches, or raw outputs
  enter the public source package.
- [ ] Compile the active `manuscript/main.tex` with the official workshop style.
- [ ] Check pages, fonts, references, tables, matrix figure readability, and
  privacy/anonymity after the final edits.
- [ ] Freeze the manuscript snapshot and archive run manifests/artifact locks.

## Eliminated decisions (keep only this marker)

| Former material | Status | Current rule |
|---|---|---|
| Earlier clean-screen/gate policy | ELIMINATED from paper-facing use | Clean metrics are descriptive; no deployment gate is reported. |
| Earlier candidate/precision panel | ELIMINATED from paper-facing use | Use only the six completed paper models. |
| Abandoned alternative-prompt sensitivity | ELIMINATED from study and manuscript | Do not run or discuss it; state only that prompt dependence is unresolved. |
| Historical pilot and development screens | ELIMINATED from paper-facing evidence | Keep only as internal provenance, never as main results. |

Do not delete immutable raw provenance merely to make filenames look cleaner;
the provenance boundary is recorded in D029. Those files are not supplied to a
manuscript-writing model.
