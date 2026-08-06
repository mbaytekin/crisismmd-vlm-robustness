# V2 report index

This directory contains the frozen-model identity, split and attack QA, pilot gate, inference metrics, paired statistical comparisons, plots, and blank manual-review templates.

- `model_identity.json`: served model, backend, smoke test, and prompt lock.
- `split_validation.md`: sample, SHA-256, and pHash disjointness checks.
- `attack_validation_<split>.md`: image/manifest validation; failures are hard stops, warnings remain reviewable.
- `pilot_results.md` and `pilot_quality_gate.md`: pilot metrics and the pre-main gate.
- `manual_review/`: HTML galleries and blank CSV review forms.
- `tables/` and `graphs/`: generated after main/style/size inference by `python -m src.v2_reporting`.

No human-review label is inferred automatically. A complete scientific conclusion requires the generated result tables plus the filled review templates.
