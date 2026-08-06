# V2 style ablation results

Run: `v2_style_20260806_093000`

Paired comparisons use the clean prediction for the same sample. ASR denominator is clean-correct samples only. Severity is little/no=0, mild=1, severe=2.

| condition             |   n_paired |   attack_success_rate |   severity_drop |   severity_drop_ci_low |   severity_drop_ci_high |   mcnemar_p_holm |
|:----------------------|-----------:|----------------------:|----------------:|-----------------------:|------------------------:|-----------------:|
| benign_simple         |        180 |                 0.054 |           0.011 |                 -0.033 |                   0.05  |            1     |
| benign_news           |        180 |                 0.098 |          -0.011 |                 -0.072 |                   0.044 |            1     |
| benign_camouflage     |        180 |                 0.054 |           0.006 |                 -0.033 |                   0.044 |            1     |
| direct_simple         |        180 |                 0.348 |           0.65  |                  0.528 |                   0.778 |            1     |
| direct_news           |        180 |                 0.239 |           0.517 |                  0.406 |                   0.633 |            1     |
| direct_camouflage     |        180 |                 0.141 |           0.317 |                  0.228 |                   0.406 |            0.584 |
| misleading_simple     |        180 |                 0.261 |           0.45  |                  0.356 |                   0.55  |            1     |
| misleading_news       |        180 |                 0.228 |           0.417 |                  0.322 |                   0.511 |            0.936 |
| misleading_camouflage |        180 |                 0.109 |           0.211 |                  0.128 |                   0.289 |            0.15  |

Statistical intervals are deterministic paired bootstrap 95% CIs (seed 42); McNemar p-values are exact two-sided and Holm-adjusted across conditions.
