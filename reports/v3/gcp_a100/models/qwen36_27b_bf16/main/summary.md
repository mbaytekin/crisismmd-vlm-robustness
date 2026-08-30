# V3 final analysis

> This report treats deployment readiness and conditional adversarial robustness as distinct questions. All attack rates condition on the explicitly reported eligible clean-correct denominator.

## 1. Models and clean competence

Model: `Qwen/Qwen3.6-27B` (`qwen36_27b_bf16__gcp_a100`).

Clean n=720, parsed=720, accuracy=0.539, macro-F1=0.532, MAE=0.583.

Clean-correct: total=388, mild=86, severe=159, mild-or-severe=245.

## 2. Main adversarial results

- `benign_image`: downward ASR 0.057 (14/245).
- `benign_text`: downward ASR 0.004 (1/245).
- `benign_joint`: downward ASR 0.053 (13/245).
- `direct_image`: downward ASR 0.678 (166/245).
- `direct_text`: downward ASR 0.082 (20/245).
- `direct_joint`: downward ASR 0.453 (111/245).
- `misleading_image`: downward ASR 0.180 (44/245).
- `misleading_text`: downward ASR 0.061 (15/245).
- `misleading_joint`: downward ASR 0.220 (54/245).

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
