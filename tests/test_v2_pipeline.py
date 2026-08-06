from pathlib import Path

import pandas as pd
import pytest

from src.v2_pipeline import LABELS, V2_ROOT, contrast_ratio


def test_v2_splits_are_disjoint_when_prepared():
    paths = [V2_ROOT / "splits" / f"{x}.csv" for x in ["style_ablation", "size_ablation"]]
    if not all(p.exists() for p in paths):
        pytest.skip("v2 splits not prepared")
    frames = {"pilot": pd.read_csv("data/splits/pilot.csv", dtype=str), "main": pd.read_csv("data/splits/test.csv", dtype=str), "style": pd.read_csv(paths[0], dtype=str), "size": pd.read_csv(paths[1], dtype=str)}
    for a, left in frames.items():
        for b, right in frames.items():
            if a >= b: continue
            assert set(left.sample_id).isdisjoint(set(right.sample_id))
            assert set(left.sha256).isdisjoint(set(right.sha256))
            assert set(left.perceptual_hash).isdisjoint(set(right.perceptual_hash))


def test_v2_pilot_manifest_has_ten_conditions_and_payload_alignment():
    path = V2_ROOT / "manifests" / "all_conditions.csv"
    if not path.exists(): pytest.skip("v2 manifest not prepared")
    m = pd.read_csv(path, dtype=str); p = m[m.split_name == "pilot"]
    assert len(p) == 99 * 10
    assert not p.duplicated(["sample_id", "condition"]).any()
    assert set(p.groupby("sample_id").condition.nunique()) == {10}
    for _, row in p[p.attack_modality.isin(["text", "joint"])].iterrows():
        assert row.condition_tweet == f"{row.payload_text}\n\n{row.original_tweet}"
    for sid, group in p[p.attack_modality == "joint"].groupby("sample_id"):
        assert len(group) == 3
        assert group.payload_id.nunique() <= 3


def test_camouflage_contrast_target_is_valid():
    assert contrast_ratio((0, 0, 0), (24, 24, 24)) > 1.0
    assert contrast_ratio((255, 255, 255), (231, 231, 231)) > 1.0
