# V3 final analysis

> This report treats deployment readiness and conditional adversarial robustness as distinct questions. All attack rates condition on the explicitly reported eligible clean-correct denominator.

## 1. Models and clean competence

Model: `Qwen/Qwen3.8-27B` (`qwen38_27b_bf16__gcp_a100`).

Clean n=720, parsed=720, accuracy=0.528, macro-F1=0.524, MAE=0.582.

Clean-correct: total=380, mild=92, severe=157, mild-or-severe=249.

## 2. Main adversarial results

- `benign_image`: downward ASR 0.052 (13/249).
- `benign_text`: downward ASR 0.004 (1/249).
- `benign_joint`: downward ASR 0.044 (11/249).
- `direct_image`: downward ASR 0.241 (60/249).
- `direct_text`: downward ASR 0.124 (31/249).
- `direct_joint`: downward ASR 0.430 (107/249).
- `misleading_image`: downward ASR 0.177 (44/249).
- `misleading_text`: downward ASR 0.100 (25/249).
- `misleading_joint`: downward ASR 0.205 (51/249).

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
