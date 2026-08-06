# V2 main results

Run: `v2_main_20260805_202424`

Paired comparisons use the clean prediction for the same sample. ASR denominator is clean-correct samples only. Severity is little/no=0, mild=1, severe=2.

| condition        |   n_paired |   attack_success_rate |   severity_drop |   severity_drop_ci_low |   severity_drop_ci_high |   mcnemar_p_holm |
|:-----------------|-----------:|----------------------:|----------------:|-----------------------:|------------------------:|-----------------:|
| benign_image     |        900 |                 0.059 |          -0.011 |                 -0.031 |                   0.008 |            1     |
| benign_text      |        900 |                 0.024 |           0.02  |                  0.007 |                   0.033 |            1     |
| benign_joint     |        900 |                 0.065 |          -0.009 |                 -0.03  |                   0.012 |            1     |
| direct_image     |        900 |                 0.325 |           0.576 |                  0.519 |                   0.63  |            1     |
| direct_text      |        900 |                 0.135 |           0.108 |                  0.071 |                   0.144 |            1     |
| direct_joint     |        900 |                 0.305 |           0.422 |                  0.366 |                   0.477 |            1     |
| misleading_image |        900 |                 0.235 |           0.414 |                  0.372 |                   0.454 |            0.67  |
| misleading_text  |        900 |                 0.137 |           0.263 |                  0.23  |                   0.297 |            0.042 |
| misleading_joint |        900 |                 0.261 |           0.434 |                  0.392 |                   0.476 |            1     |

Statistical intervals are deterministic paired bootstrap 95% CIs (seed 42); McNemar p-values are exact two-sided and Holm-adjusted across conditions.
