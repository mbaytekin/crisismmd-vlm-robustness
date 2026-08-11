# V2 corrected analysis methodology

The analysis unit is a sample-condition prediction. All attack outcomes are paired to the same sample's clean prediction. Untargeted ASR is the fraction of clean-correct samples made incorrect; targeted ASR additionally requires the attacked output to become `little_or_no_damage`. Wilson 95% intervals are reported for proportions. Severity drop uses the ordinal map little/no=0, mild=1, severe=2. Induced under-triage is restricted to severe examples correctly predicted severe when clean.

McNemar tests in `paired_modality_contrasts.csv` compare two attacked modalities directly; they are no longer described as attack-direction tests. P-values are exact, two-sided and Holm-adjusted within the six modality comparisons. Per-class precision/recall/F1 and condition confusion matrices are emitted separately.

The sensitivity analysis excludes 158 of 900 V2 main samples flagged for cross-split/repeated tweet identity, exact repeated pHash, or suspected mojibake. This does not repair V2; the corrected V3 split rebuild is the primary analysis for future model runs.
