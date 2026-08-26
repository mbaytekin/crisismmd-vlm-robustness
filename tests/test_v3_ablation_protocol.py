from src.v3_ablation_protocol import audit, wilson_half_width


def test_wilson_precision_improves_with_sample_size():
    assert wilson_half_width(120) < wilson_half_width(60)
    assert 0.08 < wilson_half_width(120) < 0.10
    assert 0.11 < wilson_half_width(60) < 0.13


def test_frozen_ablation_dataset_passes_protocol_audit():
    report = audit(write_outputs=False)

    assert report["status"] == "passed_with_documented_caveats"
    assert report["failures"] == []
    assert report["details"]["style"]["source_samples"] == 120
    assert report["details"]["size"]["source_samples"] == 60
    assert report["details"]["style"]["news_placement_metadata_mismatches"] == 171
    assert not any(report["details"]["size"]["within_sample_semantics_invariance_failures"].values())
