# V3 split validation

Status: **passed**. Tweet, exact-image and near-image clusters are grouped before selection.

Near-duplicate threshold: dHash Hamming distance <= 4.

| split | n | independent clusters | little/no | mild | severe |
|---|---:|---:|---:|---:|---:|
| pilot | 90 | 90 | 30 | 30 | 30 |
| main | 720 | 720 | 240 | 240 | 240 |
| style_ablation | 120 | 120 | 40 | 40 | 40 |
| size_ablation | 60 | 60 | 20 | 20 | 20 |

## Exclusions

Old prompt-pilot cluster rows: 144; suspected mojibake rows: 207; short-side below 128 px: 28. No selected cluster crosses a split.
