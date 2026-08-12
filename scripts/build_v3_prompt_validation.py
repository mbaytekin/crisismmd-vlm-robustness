#!/usr/bin/env python3
"""Build a clean-only prompt-validation split outside all V3 experiment splits."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import ROOT, resolve
from src.evaluation.metrics import LABELS
from src.v3_pipeline import CONFIG, build_duplicate_clusters, stable_int


SPLIT_NAME = "prompt_validation"
SPLIT_PATH = ROOT / "data" / "v3" / "splits" / f"{SPLIT_NAME}.csv"
MANIFEST_PATH = ROOT / "data" / "v3" / "manifests" / f"{SPLIT_NAME}_clean.csv"
REPORT_PATH = ROOT / "reports" / "v3" / "prompt_validation_split.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def eligible_unused_pool() -> tuple[pd.DataFrame, set[str]]:
    raw = pd.read_csv(resolve("data/processed/all_valid_damage_samples.csv"), dtype=str).fillna("")
    clustered = build_duplicate_clusters(raw)
    old = pd.read_csv(resolve("data/splits/pilot.csv"), dtype=str).fillna("")
    old_clusters = set(clustered.loc[clustered.sample_id.isin(set(old.sample_id)), "duplicate_cluster_id"])
    used_clusters: set[str] = set()
    for name in ("pilot", "main", "style_ablation", "size_ablation"):
        split = pd.read_csv(ROOT / "data" / "v3" / "splits" / f"{name}.csv", dtype=str).fillna("")
        used_clusters.update(split.duplicate_cluster_id)
    width = pd.to_numeric(clustered.image_width, errors="coerce")
    height = pd.to_numeric(clustered.image_height, errors="coerce")
    too_small = (width < int(CONFIG["minimum_image_side_px"])) | (height < int(CONFIG["minimum_image_side_px"]))
    eligible = clustered[
        ~clustered.duplicate_cluster_id.isin(old_clusters | used_clusters)
        & ~clustered.suspected_mojibake.astype(bool)
        & ~too_small
    ].copy()
    return eligible, used_clusters


def choose(pool: pd.DataFrame, per_class: int) -> pd.DataFrame:
    selected: list[pd.Series] = []
    used: set[str] = set()
    event_counts: dict[tuple[str, str], int] = defaultdict(int)
    label_order = sorted(LABELS, key=lambda label: int((pool.damage_label_normalized == label).sum()))
    for label in label_order:
        candidates = pool[pool.damage_label_normalized == label].copy()
        candidates["_rank"] = candidates.sample_id.map(
            lambda sample_id: stable_int(f"{SPLIT_NAME}:candidate:{sample_id}")
        )
        candidates = candidates.sort_values(["duplicate_cluster_id", "_rank"]).drop_duplicates("duplicate_cluster_id")
        for _ in range(per_class):
            available = candidates[~candidates.duplicate_cluster_id.isin(used)]
            if available.empty:
                raise RuntimeError(f"Insufficient unused clusters for {label}")
            row = min(
                available.itertuples(),
                key=lambda item: (
                    event_counts[(label, str(item.event_name))],
                    stable_int(f"{SPLIT_NAME}:{label}:{item.event_name}:{item.sample_id}"),
                ),
            )
            chosen = candidates[candidates.sample_id == row.sample_id].iloc[0]
            selected.append(chosen)
            used.add(str(chosen.duplicate_cluster_id))
            event_counts[(label, str(chosen.event_name))] += 1
    frame = pd.DataFrame(selected).drop(columns=["_rank"], errors="ignore")
    frame = frame.sort_values("sample_id").reset_index(drop=True)
    frame["v3_split"] = SPLIT_NAME
    return frame


def clean_manifest(split: pd.DataFrame) -> pd.DataFrame:
    columns = pd.read_csv(ROOT / "data" / "v3" / "manifests" / "all_conditions.csv", nrows=0).columns
    rows = []
    for source in split.itertuples():
        row = {column: "" for column in columns}
        row.update({
            "sample_id": source.sample_id,
            "duplicate_cluster_id": source.duplicate_cluster_id,
            "tweet_id": source.tweet_id,
            "split_name": SPLIT_NAME,
            "condition": "clean",
            "attack_modality": "none",
            "attack_semantics": "none",
            "visual_style": "none",
            "text_size": "none",
            "original_image_path": source.image_path,
            "condition_image_path": source.image_path,
            "original_tweet": source.tweet_text,
            "condition_tweet": source.tweet_text,
            "ground_truth": source.damage_label_normalized,
            "event_name": source.event_name,
            "perceptual_hash": source.perceptual_hash,
            "sha256": source.sha256,
            "template_version": "v3_prompt_validation",
            "generation_seed": str(CONFIG["seed"]),
            "generation_status": "not_applicable",
        })
        rows.append(row)
    return pd.DataFrame(rows, columns=columns)


def build(per_class: int) -> dict:
    pool, experiment_clusters = eligible_unused_pool()
    split = choose(pool, per_class)
    if split.duplicate_cluster_id.duplicated().any():
        raise RuntimeError("Duplicate cluster inside prompt-validation split")
    if set(split.duplicate_cluster_id) & experiment_clusters:
        raise RuntimeError("Prompt-validation cluster overlaps a V3 experiment split")
    SPLIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    split.to_csv(SPLIT_PATH, index=False)
    manifest = clean_manifest(split)
    manifest.to_csv(MANIFEST_PATH, index=False)
    report = {
        "schema_version": 1,
        "split_name": SPLIT_NAME,
        "purpose": "exploratory_prompt_validation_only",
        "seed": int(CONFIG["seed"]),
        "n": len(split),
        "per_class": split.damage_label_normalized.value_counts().sort_index().to_dict(),
        "per_event": split.event_name.value_counts().sort_index().to_dict(),
        "per_class_event": {
            label: group.event_name.value_counts().sort_index().to_dict()
            for label, group in split.groupby("damage_label_normalized")
        },
        "eligible_unused_rows": len(pool),
        "duplicate_clusters": int(split.duplicate_cluster_id.nunique()),
        "overlap_with_v3_experiment_clusters": 0,
        "limitation": "All remaining independent little_or_no_damage clusters are from hurricane_irma; use this split for paired prompt comparison, not event-general performance estimation.",
        "split_sha256": sha256(SPLIT_PATH),
        "manifest_sha256": sha256(MANIFEST_PATH),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-class", type=int, default=60)
    args = parser.parse_args()
    if args.per_class < 1:
        raise SystemExit("--per-class must be positive")
    print(json.dumps(build(args.per_class), indent=2))


if __name__ == "__main__":
    main()
