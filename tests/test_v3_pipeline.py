from pathlib import Path

import pandas as pd
import pytest

from src.v3_pipeline import CONFIG, V3_ROOT, build_duplicate_clusters, contrast_ratio, payloads


def test_payload_families_are_length_matched():
    means = {family: sum(map(len, values.values())) / len(values) for family, values in payloads().items()}
    assert max(means.values()) / min(means.values()) <= 1.10


def test_v3_splits_are_cluster_tweet_and_image_disjoint():
    paths = {name: V3_ROOT / "splits" / f"{name}.csv" for name in CONFIG["split_sizes_per_class"]}
    if not all(path.exists() for path in paths.values()): pytest.skip("run V3 prepare first")
    frames = {name: pd.read_csv(path, dtype=str) for name, path in paths.items()}
    for name, frame in frames.items():
        assert len(frame) == int(CONFIG["split_sizes_per_class"][name]) * 3
        assert frame.duplicate_cluster_id.is_unique
        assert set(frame.damage_label_normalized.value_counts()) == {int(CONFIG["split_sizes_per_class"][name])}
        assert not frame.suspected_mojibake.astype(str).str.lower().eq("true").any()
    for i, (a, left) in enumerate(frames.items()):
        for b, right in list(frames.items())[i + 1:]:
            for column in ["sample_id", "tweet_id", "sha256", "duplicate_cluster_id"]:
                assert set(left[column]).isdisjoint(set(right[column])), (a, b, column)


def test_v3_main_image_and_joint_share_visual_and_preserve_tweet():
    path = V3_ROOT / "manifests" / "all_conditions.csv"
    if not path.exists(): pytest.skip("run V3 prepare first")
    m = pd.read_csv(path, dtype=str).fillna(""); main = m[m.split_name == "main"]
    for (sample_id, semantics), group in main[main.visual_key != ""].groupby(["sample_id", "attack_semantics"]):
        assert group.condition_image_path.nunique() == 1, (sample_id, semantics)
    modified = main[main.attack_modality.isin(["text", "joint"])]
    assert all(r.condition_tweet == f"{r.payload_text}\n\n{r.original_tweet}" for r in modified.itertuples())


def test_size_ablation_placement_is_frozen_before_rendering():
    path = V3_ROOT / "manifests" / "all_conditions.csv"
    if not path.exists(): pytest.skip("run V3 prepare first")
    m = pd.read_csv(path, dtype=str).fillna(""); size = m[(m.split_name == "size_ablation") & (m.visual_key != "")]
    assert all(group.placement_region.nunique() == 1 for _, group in size.groupby("sample_id"))


def test_contrast_ratio_reference_values():
    assert contrast_ratio((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0)
    assert contrast_ratio((128, 128, 128), (128, 128, 128)) == pytest.approx(1.0)
