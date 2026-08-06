# CrisisMMD V2 typographic multimodal attack — technical report

## Technical summary

The main experiment is complete under the frozen prompt and locked local vLLM model. Image-only direct instruction was the strongest main-condition attack by paired ASR; joint attacks were also effective but were not uniformly stronger than image-only attacks. Benign controls produced substantially smaller effects. Style ablation shows a simple > news > camouflage ordering in the current evidence. Both style and size ablations are complete. In the current size results, medium overlays have the highest direct and misleading ASR; this is an observed ablation result, not a monotonic size law.

Main direct ASR range: 13.5%–32.5%; misleading ASR range: 13.7%–26.1%.

## Main findings

| condition    |   attack_success_rate |   severity_drop |   mcnemar_p_holm |
|:-------------|----------------------:|----------------:|-----------------:|
| direct_image |                 0.325 |           0.576 |                1 |
| direct_joint |                 0.305 |           0.422 |                1 |
| direct_text  |                 0.135 |           0.108 |                1 |

| condition        |   attack_success_rate |   severity_drop |   mcnemar_p_holm |
|:-----------------|----------------------:|----------------:|-----------------:|
| misleading_joint |                 0.261 |           0.434 |            1     |
| misleading_image |                 0.235 |           0.414 |            0.67  |
| misleading_text  |                 0.137 |           0.263 |            0.042 |

The ASR denominator is the same-sample clean-correct subset. Severity drop is ordinal clean prediction minus attacked prediction: little/no=0, mild=1, severe=2. These are paired descriptive/inferential comparisons, not causal proof of real-world misinformation impact.

## Ablation findings

| condition             |   attack_success_rate |   severity_drop |   mcnemar_p_holm |
|:----------------------|----------------------:|----------------:|-----------------:|
| direct_simple         |                 0.348 |           0.65  |            1     |
| misleading_simple     |                 0.261 |           0.45  |            1     |
| direct_news           |                 0.239 |           0.517 |            1     |
| misleading_news       |                 0.228 |           0.417 |            0.936 |
| direct_camouflage     |                 0.141 |           0.317 |            0.584 |
| misleading_camouflage |                 0.109 |           0.211 |            0.15  |

| condition         |   attack_success_rate |   severity_drop |   mcnemar_p_holm |
|:------------------|----------------------:|----------------:|-----------------:|
| direct_medium     |                 0.447 |           0.689 |            1     |
| direct_small      |                 0.421 |           0.6   |            1     |
| direct_large      |                 0.395 |           0.622 |            1     |
| misleading_small  |                 0.395 |           0.567 |            1     |
| misleading_medium |                 0.342 |           0.533 |            1     |
| misleading_large  |                 0.263 |           0.5   |            0.889 |

## Scope, data, and metric definitions

The unit of analysis is one CrisisMMD sample under one condition. Pilot, main, style-ablation, and size-ablation samples are disjoint by sample ID, exact SHA-256, and pHash at split boundaries. Main conditions contain clean, benign image/text/joint controls, direct image/text/joint attacks, and misleading image/text/joint attacks. Style and size ablations are image-only.

## Methodology and validation

All conditions use the unchanged frozen prompt, temperature 0, top-p 1, seed 42, thinking disabled, and the local `qwen3.5-9b-awq` vLLM server. Image validation checks decodability, exact source identity, bbox bounds, condition completeness, and manifest consistency. Paired bootstrap intervals use seed 42; McNemar tests are exact two-sided and Holm-adjusted across conditions.

## Limitations and uncertainty

Occupied-area warnings remain for very small source images because the renderer reduces font size to preserve the complete payload. Human readability, plausibility, and critical-region visibility are not inferred automatically; blank review templates remain in `manual_review/`. A small number of request/cache failures, if any, are reported in `error_analysis.md` rather than silently removed.

## Recommended next steps

1. Fill the manual review templates for readability, plausibility, critical-damage visibility, and image usability.

2. Treat attacks as supported only when the paired statistical result, benign-control comparison, image review, and error analysis agree.

## Further questions

Does increasing overlay size amplify ASR monotonically after controlling for style? Does camouflage reduce efficacy because it is less legible or because it is less salient? Are joint attacks complementary to image attacks or merely redundant? Manual-review labels are still needed to answer the perceptual part.

Runs: main `v2_main_20260805_202424`; style `v2_style_20260806_093000`; size `v2_size_20260806_110521`.

Detailed tables and plots: `tables/`, `graphs/`, `main_results.md`, `modality_comparison.md`, `style_ablation_results.md`, `size_ablation_results.md`, and `error_analysis.md`.
