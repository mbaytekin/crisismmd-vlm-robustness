# V3 final analysis

> This report treats deployment readiness and conditional adversarial robustness as distinct questions. All attack rates condition on the explicitly reported eligible clean-correct denominator.

## 1. Models and clean competence

Model: `mistralai/Mistral-Small-3.1-24B-Instruct-2503` (`mistral31_24b_bf16__gcp_a100`).

Clean n=720, parsed=720, accuracy=0.503, macro-F1=0.486, MAE=0.578.

Clean-correct: total=362, mild=172, severe=60, mild-or-severe=232.

## 2. Main adversarial results

- `benign_image`: downward ASR 0.078 (18/232).
- `benign_text`: downward ASR 0.017 (4/232).
- `benign_joint`: downward ASR 0.091 (21/232).
- `direct_image`: downward ASR 0.815 (189/232).
- `direct_text`: downward ASR 0.267 (62/232).
- `direct_joint`: downward ASR 0.763 (177/232).
- `misleading_image`: downward ASR 0.315 (73/232).
- `misleading_text`: downward ASR 0.086 (20/232).
- `misleading_joint`: downward ASR 0.358 (83/232).

## 3. Downward severity effects

Primary effects are in `attack_metrics.csv`; generic ASR is supplementary.

## 4. Class-conditional under-triage

Exact mild/severe transitions are in `class_transitions.csv`.

## 5. Benign-adjusted effects

Paired full-cohort and strict visual-match effects are in `benign_adjusted_effects.csv`.

## 6. Image vs text vs joint

Predeclared paired comparisons are in `statistical_tests.csv`.

## 7. Modality interaction patterns

The 3-bit I/T/J patterns and overlapping observational groups are in `modality_interactions.csv`.

## 8. Cross-model consistency

Models are analyzed separately. Cross-model direction summaries are produced only after multiple completed model runs exist.

## 9. Style ablation

Pending canonical V3 ablation inference; historical V2 results are not imported.

## 10. Size ablation

Pending canonical V3 ablation inference; historical V2 results are not imported.

## 11. Prompt-sensitivity result

An abandoned alternative-prompt sensitivity is not part of the study; the fixed zero-shot prompt remains the only paper-facing prompt.

## 12. Visual/occlusion limitations

Occupied-area and placement analyses are descriptive; damage-region overlap still requires human review.

## 13. What the results support

Claims must be limited to evaluated models, the fixed prompt, and clean-correct decisions.

## 14. What the results do NOT support

The analysis does not establish universal modality ordering, deployment safety, attack novelty, or causal event effects.
