# Prompt-development audit (historical; not paper-facing evidence)

## Status

This began as a post-hoc exploratory prompt revision performed after inspection of
the Qwen3.5 27B `frozen_p3` clean pilot. The original `frozen_p3` file and its
results remain unchanged as the historical zero-shot baseline.

The selected rubric makes the evaluation scope operational: only visible damage
to man-made infrastructure and utilities is classified; hazard context,
vegetation damage, and emergency response do not establish infrastructure
damage by themselves; and severe damage requires visible destruction or loss
of function. The zero-shot and few-shot candidates use the same rubric and
output schema. The few-shot candidate adds six balanced synthetic text
demonstrations and no CrisisMMD examples. Internal candidate/version names are
eliminated from all paper-facing use under D029.

## Validation split

The comparison uses 180 previously unused source pairs, balanced at 60 per
class. All 180 duplicate clusters are disjoint from V3 pilot, main, style, and
size splits. The clean main split remains untouched. As of 2026-08-12, model
screening used this 180-sample split and the selected zero-shot prompt instead of the
earlier 90-sample pilot. For Qwen3.5 27B, this screen remains post-hoc because
the same split selected the prompt; its main result is confirmatory.

Only 66 unused independent `little_or_no_damage` clusters remained after the
existing exclusions, so a planned 100-per-class split was not feasible without
reuse. The final 60-per-class split is deterministic. All remaining little/no
clusters are from Hurricane Irma, which creates a class-event confound. Use the
split only for paired prompt selection, not event-general performance claims.

## Results

| metric | Selected zero-shot | Few-shot candidate |
|---|---:|---:|
| parsed | 180/180 | 180/180 |
| accuracy | 0.639 (115/180) | 0.628 (113/180) |
| macro F1 | 0.631 | 0.621 |
| little/no recall | 0.667 | 0.700 |
| mild recall | 0.433 | 0.417 |
| severe recall | 0.817 | 0.767 |
| mean latency | 6.87 s | 7.43 s |

Few-shot prompting changed nine predictions. Three zero-shot errors became
correct and five zero-shot correct predictions became errors. The paired
accuracy difference was -0.011, with a 95% paired bootstrap interval of
[-0.044, 0.017] and an exploratory exact McNemar p-value of 0.727. Few-shot
latency was 8.2% higher.

Both prompts exceeded the numerical V3 pilot thresholds on this larger
validation split, but this does not constitute a main-gate pass. Accuracy was
strongly associated with source annotation confidence: the selected zero-shot candidate scored 0.510 for
confidence <=0.67 and 0.744 for unanimous confidence 1.0.

## Selection

Select and lock the zero-shot rubric. It has
higher accuracy, macro F1, mild recall, severe recall, and lower latency. The
few-shot demonstrations add no supported quality benefit on the independent
validation split. Keep few-shot prompting out of the primary production
protocol and report it as a clean-prompt sensitivity analysis.

Do not modify the locked prompt text after this selection. Before any clean-main
run, record its prompt hash and update the protocol to disclose that it was
selected post-hoc on the independent prompt-validation split.

The locked prompt hash is
`1fa1a4a2b61c4aaadb95215385cd97915fd515ca4b19fc477ba98291cdf39ee6`.
Production scripts use the content-locked rubric. The immutable artifact lock
and the prompt text reproduced in the manuscript appendix are the paper-facing
references; internal filenames are implementation history only.
