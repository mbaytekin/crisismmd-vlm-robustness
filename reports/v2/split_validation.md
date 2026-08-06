# V2 split validation

Splits are checked at sample ID, exact image SHA-256, and deterministic perceptual-hash level. Diagonal perceptual-hash duplicates are expected to be profile information; off-diagonal intersections are leakage failures.

| split | n | little/no | mild | severe | duplicate sample | duplicate SHA | duplicate pHash |
|---|---:|---:|---:|---:|---:|---:|---:|
| pilot | 99 | 33 | 33 | 33 | 0 | 0 | 0 |
| main | 900 | 300 | 300 | 300 | 0 | 0 | 12 |
| style_ablation | 180 | 60 | 60 | 60 | 0 | 0 | 0 |
| size_ablation | 90 | 30 | 30 | 30 | 0 | 0 | 1 |

## Intersection matrix

| split A | split B | sample_id | SHA-256 | pHash |
|---|---|---:|---:|---:|
| pilot | pilot | 99 | 99 | 99 |
| pilot | main | 0 | 0 | 0 |
| pilot | style_ablation | 0 | 0 | 0 |
| pilot | size_ablation | 0 | 0 | 0 |
| main | pilot | 0 | 0 | 0 |
| main | main | 900 | 900 | 888 |
| main | style_ablation | 0 | 0 | 0 |
| main | size_ablation | 0 | 0 | 0 |
| style_ablation | pilot | 0 | 0 | 0 |
| style_ablation | main | 0 | 0 | 0 |
| style_ablation | style_ablation | 180 | 180 | 180 |
| style_ablation | size_ablation | 0 | 0 | 0 |
| size_ablation | pilot | 0 | 0 | 0 |
| size_ablation | main | 0 | 0 | 0 |
| size_ablation | style_ablation | 0 | 0 | 0 |
| size_ablation | size_ablation | 90 | 90 | 89 |
