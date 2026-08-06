# CrisisMMD V2 independent dataset audit

## Overall decision

**Audit status: PASS_WITH_WARNINGS.** Read-only audit. Critical/high rows: **0**; medium rows: **859**. Existing data, manifests, predictions and source code were not changed.

## Project structure

| Experiment | Content | Actual path | Format |
|---|---|---|---|
| Dataset manifest | Samples x conditions | data/v2/manifests/all_conditions.csv and .parquet | CSV/Parquet |
| Pilot | 99 x 10 | data/v2/attacks/pilot/ | PNG/CSV |
| Main | 900 x 10 | data/v2/attacks/main/, results/v2/v2_main_20260805_202424/ | PNG/JSONL/SQLite/JSON |
| Style ablation | 180 x 10 | data/v2/attacks/style_ablation/, results/v2/v2_style_20260806_093000/ | PNG/JSONL/SQLite/JSON |
| Size ablation | 90 x 10 | data/v2/attacks/size_ablation/, results/v2/v2_size_20260806_110521/ | PNG/JSONL/SQLite/JSON |
| Text-only/joint tweets | Payload + original | data/v2/manifests/text_conditions.csv | CSV |
| Payload assignments | Deterministic assignments | data/v2/manifests/payload_assignments.csv | CSV |
| Predictions | Model outputs | results/v2/*/predictions.jsonl | JSONL |
| Metrics/reports | Metrics and narratives | results/v2/*/metrics.json, reports/v2/ | JSON/CSV/Markdown/HTML |

## Expected versus found

| Split | Expected samples | Found samples | Found rows | Expected conditions | Distinct conditions |
|---|---:|---:|---:|---:|---:|
| pilot | 99 | 99 | 990 | 10 | 10 |
| main | 900 | 900 | 9000 | 10 | 10 |
| style_ablation | 180 | 180 | 1800 | 10 | 10 |
| size_ablation | 90 | 90 | 900 | 10 | 10 |

Grain checked: one sample_id x condition.

## Findings

- Modality violations=0; text preservation failures=0; clean-identical attack images=0.
- Payload assignment/category failures=0; benign forbidden-term issues=0.
- Missing/unreadable attack images=0; bbox failures=0; occupied warnings=347; below-min-font warnings=71.
- Cross-split sample/SHA/pHash intersections are listed as critical if nonzero.

## Payload diversity

- benign: B1=274, B2=267, B3=255, B4=241, B5=232
- direct_instruction: D1=274, D2=267, D3=255, D4=241, D5=232
- misleading_claim: M1=241, M2=223, M3=216, M4=210, M5=199, M6=180

Same-sample payload identity across modality/style/size families was checked.

## News and camouflage

- News rows=540; expected fictional logo=CRISIS24; logo violations=0.
- Camouflage metadata contrast=min=1.127, median=1.388, max=1.457; independent low=216, high=18, complex review=29.
- Critical-region occlusion and human readability are not inferable from metadata alone; both are marked manual review.

## Size ablation

- Font-order violations=0; non-size invariant violations=209, all attributable to placement_region changing across sizes for 89 sample groups. Therefore this ablation is not a pure size-only comparison and should be interpreted as size plus placement.

## Data diversity

- Damage classes: main: little_or_no_damage=300, mild_damage=300, severe_damage=300; pilot: little_or_no_damage=33, mild_damage=33, severe_damage=33; size_ablation: little_or_no_damage=30, mild_damage=30, severe_damage=30; style_ablation: little_or_no_damage=60, mild_damage=60, severe_damage=60
- Events: main: california_wildfires=96, hurricane_harvey=189, hurricane_irma=251, hurricane_maria=183, iraq_iran_earthquake=50, mexico_earthquake=63, srilanka_floods=68; pilot: california_wildfires=15, hurricane_harvey=15, hurricane_irma=15, hurricane_maria=15, iraq_iran_earthquake=13, mexico_earthquake=13, srilanka_floods=13; size_ablation: california_wildfires=11, hurricane_harvey=19, hurricane_irma=38, hurricane_maria=19, iraq_iran_earthquake=1, mexico_earthquake=2, srilanka_floods=0; style_ablation: california_wildfires=11, hurricane_harvey=57, hurricane_irma=70, hurricane_maria=37, iraq_iran_earthquake=2, mexico_earthquake=2, srilanka_floods=1
- Unique clean image paths=1269; placement/style/size/resolution fields were profiled.

## Critical issues and recommendation

- Issue types: occupied_area_warning=347, font_below_config_minimum=71, payload_imbalance=12, camouflage_possibly_invisible=216, camouflage_metadata_pixel_contrast_mismatch=75, camouflage_not_camouflaged=18, camouflage_complex_background_review=29, size_ablation_invariant_changed=89, critical_region_manual_review_required=1, readability_manual_review_required=1.
- Exact rows: reports/v2/audit/audit_issues.csv; review cards: reports/v2/audit/audit_gallery.html.
- Main-inference recommendation: **SAFE_WITH_CAVEATS**. Medium items require manual review; high/critical items would block use.

## Direct answers

1. Plan compliance and all issues are summarized above and enumerated in CSV.
2. Image-only/text-only/joint rules were checked by paths, SHA-256, tweet suffix and payload identity.
3. Payload diversity and balance are shown above.
4. News uses fictional-logo checks.
5. Camouflage uses independent local-background contrast plus metadata.
6. Size checks include target metadata, monotonic order and invariants.
7. Class, event, payload, placement, style, size and resolution diversity were profiled.
8. Critical/high and medium counts are above.
9. Experiment locations are in the project table.
10. Safe to use for main inference is the recommendation above; outputs were not modified.

Deterministic seed: 42. Only the three requested audit outputs were generated.
