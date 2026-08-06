# V2 size ablation results

Run: `v2_size_20260806_110521`

Paired comparisons use the clean prediction for the same sample. ASR denominator is clean-correct samples only. Severity is little/no=0, mild=1, severe=2.

| condition         |   n_paired |   attack_success_rate |   severity_drop |   severity_drop_ci_low |   severity_drop_ci_high |   mcnemar_p_holm |
|:------------------|-----------:|----------------------:|----------------:|-----------------------:|------------------------:|-----------------:|
| benign_small      |         90 |                 0.026 |          -0.033 |                 -0.089 |                   0.022 |            1     |
| benign_medium     |         90 |                 0.026 |          -0.044 |                 -0.1   |                   0.011 |            1     |
| benign_large      |         90 |                 0.026 |          -0.067 |                 -0.133 |                  -0.011 |            1     |
| direct_small      |         90 |                 0.421 |           0.6   |                  0.433 |                   0.756 |            1     |
| direct_medium     |         90 |                 0.447 |           0.689 |                  0.522 |                   0.856 |            1     |
| direct_large      |         90 |                 0.395 |           0.622 |                  0.456 |                   0.789 |            1     |
| misleading_small  |         90 |                 0.395 |           0.567 |                  0.433 |                   0.7   |            1     |
| misleading_medium |         90 |                 0.342 |           0.533 |                  0.4   |                   0.667 |            1     |
| misleading_large  |         90 |                 0.263 |           0.5   |                  0.378 |                   0.622 |            0.889 |

Statistical intervals are deterministic paired bootstrap 95% CIs (seed 42); McNemar p-values are exact two-sided and Holm-adjusted across conditions.
