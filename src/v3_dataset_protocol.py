"""Build and audit secondary clean cohorts for the V3 paper protocol.

The frozen 720-sample attack cohort is not rewritten here. This module creates
two clean-only views: all 3,474 locally valid severity records and the exact
published 529-row CrisisMMD test split. It also records selection, duplication,
and label-consistency evidence needed to describe the custom V3 cohort.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import pandas as pd

from src.config import ROOT, resolve
from src.evaluation.metrics import LABELS
from src.v3_pipeline import CONFIG, build_duplicate_clusters


SOURCE = ROOT / "data" / "processed" / "all_valid_damage_samples.csv"
OFFICIAL_SPLIT_ROOT = (
    ROOT / "data" / "raw" / "crisismmd_datasplit_all" / "crisismmd_datasplit_all"
)
OFFICIAL_IMAGE_ROOT = ROOT / "data" / "raw" / "CrisisMMD_v2.0" / "CrisisMMD_v2.0"
NATURAL_MANIFEST = ROOT / "data" / "v3" / "manifests" / "natural_clean_all.csv"
OFFICIAL_TEST_MANIFEST = ROOT / "data" / "v3" / "manifests" / "official_test_clean.csv"
REPORT = ROOT / "reports" / "v3" / "dataset_protocol_audit.json"
REPORT_MD = ROOT / "reports" / "v3" / "dataset_protocol_audit.md"
TABLE_ROOT = ROOT / "reports" / "v3" / "dataset_protocol"

OFFICIAL_FILES = {
    "train": "task_damage_text_img_train.tsv",
    "dev": "task_damage_text_img_dev.tsv",
    "test": "task_damage_text_img_test.tsv",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    return {
        str(key): int(value)
        for key, value in frame[column].value_counts().sort_index().items()
    }


def _official_rows(processed: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for split, filename in OFFICIAL_FILES.items():
        path = OFFICIAL_SPLIT_ROOT / filename
        frame = pd.read_csv(path, sep="\t", dtype=str).fillna("")
        frame["official_split"] = split
        frame["ground_truth"] = frame["label"]
        frame["resolved_image_path"] = frame["image"].map(
            lambda value: str((OFFICIAL_IMAGE_ROOT / value).relative_to(ROOT))
        )
        frames.append(frame)
    official = pd.concat(frames, ignore_index=True)

    known_hashes = processed.set_index("image_path")["sha256"].to_dict()
    hashes = []
    missing = []
    for row in official.itertuples():
        digest = known_hashes.get(row.resolved_image_path)
        if not digest:
            image_path = resolve(row.resolved_image_path)
            if not image_path.is_file():
                missing.append(row.resolved_image_path)
                digest = ""
            else:
                digest = _sha256(image_path)
        hashes.append(digest)
    if missing:
        raise FileNotFoundError(f"Missing official severity images: {missing[:5]}")
    official["sha256"] = hashes
    return official


def _exact_conflicts(official: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for digest, group in official.groupby("sha256", sort=True):
        labels = sorted(group.ground_truth.unique())
        if len(labels) <= 1:
            continue
        rows.append({
            "sha256": digest,
            "official_rows": len(group),
            "labels": "|".join(labels),
            "official_splits": "|".join(sorted(group.official_split.unique())),
            "image_ids": "|".join(sorted(group.image_id.unique())),
        })
    return pd.DataFrame(rows)


def _base_manifest_columns() -> list[str]:
    path = ROOT / "data" / "v3" / "manifests" / "all_conditions.csv"
    columns = list(pd.read_csv(path, nrows=0).columns)
    for extra in (
        "source_protocol", "official_split", "label_conflict_exact_sha",
        "v3_input_eligible", "v3_any_cohort_overlap", "v3_prompt_cohort_overlap",
    ):
        if extra not in columns:
            columns.append(extra)
    return columns


def _clean_row(columns: list[str], **values: str) -> dict[str, str]:
    row = {column: "" for column in columns}
    row.update({
        "condition": "clean",
        "attack_modality": "none",
        "attack_semantics": "none",
        "visual_style": "none",
        "text_size": "none",
        "generation_seed": str(CONFIG["seed"]),
        "generation_status": "not_applicable",
        **values,
    })
    return row


def build_clean_manifests(
    clustered: pd.DataFrame, official: pd.DataFrame, conflict_hashes: set[str],
    eligible_clusters: set[str], v3_clusters: set[str], prompt_clusters: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = _base_manifest_columns()
    natural_rows = []
    for source in clustered.itertuples():
        natural_rows.append(_clean_row(
            columns,
            sample_id=str(source.sample_id),
            duplicate_cluster_id=str(source.duplicate_cluster_id),
            tweet_id=str(source.tweet_id),
            split_name="natural_clean_all",
            original_image_path=str(source.image_path),
            condition_image_path=str(source.image_path),
            original_tweet=str(source.tweet_text),
            condition_tweet=str(source.tweet_text),
            ground_truth=str(source.damage_label_normalized),
            event_name=str(source.event_name),
            perceptual_hash=str(source.perceptual_hash),
            sha256=str(source.sha256),
            template_version="v3_natural_clean_all",
            source_protocol="processed_exact_sha_unique_natural_distribution",
            label_conflict_exact_sha=str(source.sha256 in conflict_hashes).lower(),
            v3_input_eligible=str(source.duplicate_cluster_id in eligible_clusters).lower(),
            v3_any_cohort_overlap=str(source.duplicate_cluster_id in v3_clusters).lower(),
            v3_prompt_cohort_overlap=str(source.duplicate_cluster_id in prompt_clusters).lower(),
        ))

    cluster_by_sha = clustered.drop_duplicates("sha256").set_index("sha256")[
        "duplicate_cluster_id"
    ].to_dict()
    official_rows = []
    test = official[official.official_split.eq("test")].reset_index(drop=True)
    for index, source in test.iterrows():
        digest = str(source.sha256)
        cluster = cluster_by_sha.get(digest, f"official_unmapped_{digest[:16]}")
        sample_id = f"official_test__{source.image_id}"
        if test.image_id.duplicated(keep=False).iloc[index]:
            sample_id = f"{sample_id}__{index:04d}"
        official_rows.append(_clean_row(
            columns,
            sample_id=sample_id,
            duplicate_cluster_id=str(cluster),
            tweet_id=str(source.tweet_id),
            split_name="official_test",
            original_image_path=str(source.resolved_image_path),
            condition_image_path=str(source.resolved_image_path),
            original_tweet=str(source.tweet_text),
            condition_tweet=str(source.tweet_text),
            ground_truth=str(source.ground_truth),
            event_name=str(source.event_name),
            sha256=digest,
            template_version="v3_official_test_clean",
            source_protocol="published_crisismmd_damage_test_split",
            official_split="test",
            label_conflict_exact_sha=str(digest in conflict_hashes).lower(),
            v3_input_eligible=str(cluster in eligible_clusters).lower(),
            v3_any_cohort_overlap=str(cluster in v3_clusters).lower(),
            v3_prompt_cohort_overlap=str(cluster in prompt_clusters).lower(),
        ))

    natural = pd.DataFrame(natural_rows, columns=columns)
    official_test = pd.DataFrame(official_rows, columns=columns)
    NATURAL_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    natural.to_csv(NATURAL_MANIFEST, index=False)
    official_test.to_csv(OFFICIAL_TEST_MANIFEST, index=False)
    return natural, official_test


def _eligible_pool(clustered: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], set[str]]:
    old = pd.read_csv(ROOT / "data" / "splits" / "pilot.csv", dtype=str).fillna("")
    old_clusters = set(
        clustered.loc[clustered.sample_id.isin(set(old.sample_id)), "duplicate_cluster_id"]
    )
    blocked = clustered.duplicate_cluster_id.isin(old_clusters)
    mojibake = clustered.suspected_mojibake.astype(bool)
    width = pd.to_numeric(clustered.image_width, errors="coerce")
    height = pd.to_numeric(clustered.image_height, errors="coerce")
    too_small = (width < int(CONFIG["minimum_image_side_px"])) | (
        height < int(CONFIG["minimum_image_side_px"])
    )
    eligible = clustered[~blocked & ~mojibake & ~too_small].copy()
    exclusions = {
        "source_rows": len(clustered),
        "old_pilot_cluster_rows": int(blocked.sum()),
        "mojibake_rows_after_prior_exclusions": int((~blocked & mojibake).sum()),
        "below_minimum_side_rows_after_prior_exclusions": int(
            (~blocked & ~mojibake & too_small).sum()
        ),
        "eligible_rows": len(eligible),
        "eligible_duplicate_clusters": int(eligible.duplicate_cluster_id.nunique()),
    }
    return eligible, exclusions, old_clusters


def _largest_remainder(counts: pd.Series, total: int) -> dict[str, int]:
    counts = counts[counts.gt(0)].astype(int).sort_index()
    exact = counts / counts.sum() * total
    quotas = exact.map(math.floor).astype(int)
    remainder = total - int(quotas.sum())
    order = sorted(counts.index, key=lambda key: (-(exact[key] - quotas[key]), str(key)))
    for key in order[:remainder]:
        quotas[key] += 1
    return {str(key): int(value) for key, value in quotas.items()}


def _event_class_table(frame: pd.DataFrame, label_column: str) -> pd.DataFrame:
    table = frame.pivot_table(
        index="event_name", columns=label_column, values="sample_id", aggfunc="count", fill_value=0
    ).reset_index()
    for label in LABELS:
        if label not in table:
            table[label] = 0
    table["total"] = table[LABELS].sum(axis=1)
    return table[["event_name", *LABELS, "total"]]


def _pair_overlap(frame: pd.DataFrame, first: str, second: str) -> dict[str, int]:
    a = frame[frame.official_split.eq(first)]
    b = frame[frame.official_split.eq(second)]
    return {
        "tweet_id": len(set(a.tweet_id) & set(b.tweet_id)),
        "sha256": len(set(a.sha256) & set(b.sha256)),
        "duplicate_cluster_id": len(set(a.duplicate_cluster_id) & set(b.duplicate_cluster_id)),
    }


def _wilson_half_width(n: int) -> float:
    z = 1.959963984540054
    denominator = 1 + z * z / n
    return z * math.sqrt(0.25 / n + z * z / (4 * n * n)) / denominator


def build_audit(
    clustered: pd.DataFrame, official: pd.DataFrame, conflicts: pd.DataFrame,
    natural: pd.DataFrame, official_manifest: pd.DataFrame,
) -> dict:
    TABLE_ROOT.mkdir(parents=True, exist_ok=True)
    eligible, exclusions, _ = _eligible_pool(clustered)
    conflict_hashes = set(conflicts.sha256) if len(conflicts) else set()

    official_cluster_map = clustered.drop_duplicates("sha256").set_index("sha256")[
        "duplicate_cluster_id"
    ].to_dict()
    official = official.copy()
    official["duplicate_cluster_id"] = official.sha256.map(official_cluster_map).fillna(
        official.sha256.map(lambda value: f"official_unmapped_{value[:16]}")
    )
    official_test = official[official.official_split.eq("test")].copy()

    split_frames = {}
    for split in ("pilot", "main", "style_ablation", "size_ablation", "prompt_validation"):
        split_frames[split] = pd.read_csv(
            ROOT / "data" / "v3" / "splits" / f"{split}.csv", dtype=str
        ).fillna("")
    all_v3_clusters = set().union(*(set(frame.duplicate_cluster_id) for frame in split_frames.values()))
    test_v3_overlap = {
        split: int(official_test.duplicate_cluster_id.isin(set(frame.duplicate_cluster_id)).sum())
        for split, frame in split_frames.items()
    }

    prompt_clusters = set(split_frames["prompt_validation"].duplicate_cluster_id)
    pilot_clusters = set(split_frames["pilot"].duplicate_cluster_id)
    eligible_clusters = set(eligible.duplicate_cluster_id)
    official_usable = official_test.duplicate_cluster_id.isin(eligible_clusters)
    official_after_prompt_validation = official_usable & ~official_test.duplicate_cluster_id.isin(
        prompt_clusters
    )
    official_strict_untouched = (
        official_after_prompt_validation
        & ~official_test.duplicate_cluster_id.isin(pilot_clusters)
        & ~official_test.sha256.isin(conflict_hashes)
    )

    main = split_frames["main"].copy()
    main_distribution = _event_class_table(main, "damage_label_normalized")
    main_distribution.to_csv(TABLE_ROOT / "main_event_class_distribution.csv", index=False)
    _event_class_table(clustered, "damage_label_normalized").to_csv(
        TABLE_ROOT / "source_event_class_distribution.csv", index=False
    )
    _event_class_table(eligible, "damage_label_normalized").to_csv(
        TABLE_ROOT / "eligible_event_class_distribution.csv", index=False
    )
    official_test_for_table = official_test.rename(columns={"image_id": "sample_id"})
    _event_class_table(official_test_for_table, "ground_truth").to_csv(
        TABLE_ROOT / "official_test_event_class_distribution.csv", index=False
    )

    candidate_rows = []
    candidate_pool = eligible[~eligible.sha256.isin(conflict_hashes)].copy()
    for label in LABELS:
        candidates = candidate_pool[candidate_pool.damage_label_normalized.eq(label)].drop_duplicates(
            "duplicate_cluster_id"
        )
        quotas = _largest_remainder(candidates.event_name.value_counts(), 240)
        for event, quota in quotas.items():
            candidate_rows.append({
                "damage_label": label,
                "event_name": event,
                "eligible_independent_clusters": int((candidates.event_name == event).sum()),
                "candidate_main_first_quota": quota,
                "current_main_n": int(((main.damage_label_normalized == label) & (main.event_name == event)).sum()),
            })
    candidate = pd.DataFrame(candidate_rows).sort_values(["damage_label", "event_name"])
    candidate.to_csv(TABLE_ROOT / "candidate_main_first_event_quotas.csv", index=False)

    official_split_distribution = (
        official.groupby(["official_split", "ground_truth"]).size().rename("n").reset_index()
    )
    official_split_distribution.to_csv(TABLE_ROOT / "official_split_distribution.csv", index=False)
    conflicts.to_csv(TABLE_ROOT / "exact_sha_label_conflicts.csv", index=False)
    main_conflicts = main[main.sha256.isin(conflict_hashes)][
        ["sample_id", "event_name", "damage_label_normalized", "sha256", "duplicate_cluster_id"]
    ].copy()
    main_conflicts.to_csv(TABLE_ROOT / "main_exact_sha_label_conflicts.csv", index=False)

    precision = pd.DataFrame([
        {"cohort": "v3_main_balanced", "n": 720, "worst_case_95pct_half_width": _wilson_half_width(720)},
        {"cohort": "v3_main_per_class", "n": 240, "worst_case_95pct_half_width": _wilson_half_width(240)},
        {"cohort": "official_test", "n": 529, "worst_case_95pct_half_width": _wilson_half_width(529)},
        {"cohort": "natural_clean_rows", "n": 3474, "worst_case_95pct_half_width": _wilson_half_width(3474)},
        {"cohort": "natural_clean_clusters", "n": int(clustered.duplicate_cluster_id.nunique()), "worst_case_95pct_half_width": _wilson_half_width(int(clustered.duplicate_cluster_id.nunique()))},
    ])
    precision.to_csv(TABLE_ROOT / "binomial_precision_reference.csv", index=False)

    real_images = [
        path for path in OFFICIAL_IMAGE_ROOT.joinpath("data_image").rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    ]
    apple_double = [path for path in real_images if path.name.startswith("._")]
    duplicate_groups = official.groupby("sha256").size()
    report = {
        "schema_version": 1,
        "generated_from_local_data": True,
        "official_dataset": {
            "published_real_images_all_tasks": 18082,
            "local_image_extension_files": len(real_images),
            "local_appledouble_metadata_files": len(apple_double),
            "published_damage_severity_rows": len(official),
            "damage_class_counts": _counts(official, "ground_truth"),
            "split_counts": _counts(official, "official_split"),
            "official_test_class_counts": _counts(official_test, "ground_truth"),
            "official_test_majority_baseline": float(official_test.ground_truth.value_counts(normalize=True).max()),
        },
        "local_processed_source": {
            "rows": len(clustered),
            "class_counts": _counts(clustered, "damage_label_normalized"),
            "exact_sha_unique": int(clustered.sha256.nunique()),
            "v3_duplicate_clusters": int(clustered.duplicate_cluster_id.nunique()),
            "rows_removed_from_official_severity_by_exact_sha_deduplication": len(official) - len(clustered),
            "official_duplicate_sha_groups": int((duplicate_groups > 1).sum()),
            "official_rows_in_duplicate_sha_groups": int(duplicate_groups[duplicate_groups > 1].sum()),
            "official_extra_rows_beyond_one_per_sha": int((duplicate_groups - 1).clip(lower=0).sum()),
            "exact_sha_conflicting_label_groups": len(conflicts),
            "official_rows_in_exact_sha_conflicting_label_groups": int(conflicts.official_rows.sum()) if len(conflicts) else 0,
        },
        "v3_selection": {
            **exclusions,
            "selected_source_rows": sum(len(split_frames[name]) for name in ("pilot", "main", "style_ablation", "size_ablation")),
            "main_rows": len(main),
            "main_per_class": _counts(main, "damage_label_normalized"),
            "main_events": _counts(main, "event_name"),
            "main_exact_sha_conflict_rows": len(main_conflicts),
            "allocation_rule": "rare_labels_first_then_small_splits_first_then_event_count_equalization",
            "selection_role": "custom_class_balanced_paired_robustness_cohort_not_official_test",
        },
        "official_split_audit": {
            "train_dev_overlap": _pair_overlap(official, "train", "dev"),
            "train_test_overlap": _pair_overlap(official, "train", "test"),
            "dev_test_overlap": _pair_overlap(official, "dev", "test"),
            "duplicate_clusters_spanning_multiple_official_splits": int(
                (official.groupby("duplicate_cluster_id").official_split.nunique() > 1).sum()
            ),
            "official_rows_in_cross_split_duplicate_clusters": int(
                official.duplicate_cluster_id.isin(
                    set(official.groupby("duplicate_cluster_id").official_split.nunique().loc[lambda value: value > 1].index)
                ).sum()
            ),
            "official_test_overlap_with_v3_by_cluster_rows": test_v3_overlap,
            "official_test_rows_independent_of_all_v3_cohorts": int(
                (~official_test.duplicate_cluster_id.isin(all_v3_clusters)).sum()
            ),
            "official_test_rows_passing_v3_input_and_old_pilot_filters": int(official_usable.sum()),
            "official_test_rows_after_prompt_validation_exclusion": int(official_after_prompt_validation.sum()),
            "official_test_rows_after_all_prompt_cohorts_and_exact_label_conflicts": int(official_strict_untouched.sum()),
        },
        "generated_clean_manifests": {
            "natural_clean_all": {"path": str(NATURAL_MANIFEST.relative_to(ROOT)), "rows": len(natural)},
            "official_test": {"path": str(OFFICIAL_TEST_MANIFEST.relative_to(ROOT)), "rows": len(official_manifest)},
        },
        "recommendation": {
            "primary_attack_cohort": "retain_frozen_v3_main_720",
            "secondary_clean_cohorts": ["natural_clean_all_3474", "official_test_529"],
            "do_not_claim": "The 720 rows are the published CrisisMMD test split or a natural-prevalence sample.",
            "versioning_rule": "Any replacement cohort must be V4 and requires regenerated attacks and rerun inference; never overwrite V3.",
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    _write_markdown(report)
    return report


def _write_markdown(report: dict) -> None:
    official = report["official_dataset"]
    processed = report["local_processed_source"]
    selection = report["v3_selection"]
    split_audit = report["official_split_audit"]
    overlap = split_audit["official_test_overlap_with_v3_by_cluster_rows"]
    lines = [
        "# CrisisMMD cohort and split audit",
        "",
        "**Technical summary.** The frozen 720-row V3 main set is a defensible custom, class-balanced paired robustness cohort, not the published CrisisMMD test split. Its strongest literature-aligned property is global exact/near-duplicate separation. Its principal sampling limitation is the small-splits-first, event-equalizing allocation, which depleted rare event/class cells before main selection. Keep V3 immutable, add natural-distribution and official-test clean evaluations, and version any future replacement as V4.",
        "",
        "## Three numbers refer to three different populations",
        "",
        "| Number | Meaning | Recommended use |",
        "|---:|---|---|",
        f"| 18,082 | Published CrisisMMD v2.0 real images across all annotation tasks | Dataset scale only; most images do not have a damage-severity label |",
        f"| 3,526 | Published damage-severity image rows | Severity-task source population before local exact-SHA deduplication |",
        f"| 3,474 | Locally valid, exact-SHA-unique severity image-text rows | Natural-prevalence clean-only evaluation |",
        f"| 529 | Published damage-severity test rows (71 little/no, 126 mild, 332 severe) | Secondary literature-comparability clean evaluation |",
        f"| 720 | Custom V3 main rows (240 per class) | Primary paired clean/attack experiment |",
        "",
        "The 18,082 figure is not the size of the severity task. The local directory contains 18,104 image-extension files because 22 are macOS AppleDouble `._*` metadata files; the real-image count remains 18,082.",
        "",
        "## Why 3,526 became 3,474",
        "",
        f"The local preprocessing keeps one row per exact image SHA-256. The official severity files contain {processed['official_duplicate_sha_groups']} duplicated SHA groups affecting {processed['official_rows_in_duplicate_sha_groups']} rows, so retaining one row per hash removes {processed['official_extra_rows_beyond_one_per_sha']} extra rows. This exactly explains 3,526 minus 52 equals 3,474.",
        "",
        f"A higher-risk label-quality issue remains: {processed['exact_sha_conflicting_label_groups']} exact-byte image groups ({processed['official_rows_in_exact_sha_conflicting_label_groups']} official rows) carry more than one severity label. The current main set contains {selection['main_exact_sha_conflict_rows']} retained rows from those groups. Primary tables should retain the frozen cohort, while a predeclared sensitivity excludes those rows.",
        "",
        "## How the 720-row V3 main cohort was selected",
        "",
        "1. Start from 3,474 exact-SHA-unique rows.",
        f"2. Build global duplicate clusters from exact tweet ID/text, exact SHA/perceptual hash, and dHash Hamming distance <= {CONFIG['near_duplicate_hamming']}.",
        f"3. Exclude old prompt-pilot clusters, suspected mojibake, and images below {CONFIG['minimum_image_side_px']} pixels on either side, leaving {selection['eligible_rows']:,} rows in {selection['eligible_duplicate_clusters']:,} independent clusters.",
        "4. Select rare labels first and allocate size (20/class), pilot (30/class), style (40/class), then main (240/class).",
        "5. Within each split/class, repeatedly choose from the currently least represented event; a seeded hash breaks ties.",
        "",
        "This produces a large, balanced, deterministic paired experiment with no V3 cross-split duplicate-cluster leakage. It is not a random sample, an event-proportional sample, or the official test split. Because auxiliary splits are filled first, all eligible California and Sri Lanka little/no clusters were consumed before main; main little/no examples consequently come only from the three hurricanes.",
        "",
        "Because main has event-by-class structural zeros, it cannot support honest event-by-class post-stratification to the source population. Only class-prior reweighting is supported; event-specific attack results must remain descriptive.",
        "",
        "## What the official 529-row test split contributes",
        "",
        f"The published test split preserves the natural class imbalance: its severe-class majority baseline is {official['official_test_majority_baseline']:.3f}. It is valuable for comparing clean zero-shot results with work that names the official split, but 60% raw accuracy would be below its majority baseline and cannot serve as a universal competence threshold.",
        "",
        "The released train/dev/test class counts are consistent with a 70/15/15 stratified partition. The severity split files do not record the exact randomization algorithm or seed, so this is a composition inference rather than a documented generation claim.",
        "",
        "Under the stricter V3 duplicate definition, the published files are not fully independent:",
        "",
        f"- train-test overlap: {split_audit['train_test_overlap']['tweet_id']} tweet IDs, {split_audit['train_test_overlap']['sha256']} exact SHA values, {split_audit['train_test_overlap']['duplicate_cluster_id']} duplicate clusters;",
        f"- dev-test overlap: {split_audit['dev_test_overlap']['tweet_id']} tweet IDs, {split_audit['dev_test_overlap']['sha256']} exact SHA values, {split_audit['dev_test_overlap']['duplicate_cluster_id']} duplicate clusters;",
        f"- {split_audit['duplicate_clusters_spanning_multiple_official_splits']} duplicate clusters span multiple official splits and affect {split_audit['official_rows_in_cross_split_duplicate_clusters']} official rows.",
        "",
        f"The official test also overlaps existing V3 cohorts by cluster (pilot {overlap['pilot']}, main {overlap['main']}, style {overlap['style_ablation']}, size {overlap['size_ablation']}, prompt-validation {overlap['prompt_validation']} rows). Only {split_audit['official_test_rows_independent_of_all_v3_cohorts']} of 529 rows are independent of every V3 cohort. Therefore the official test result is explicitly secondary/post-hoc, not a new untouched confirmatory test.",
        "",
        "## Literature alignment",
        "",
        "- [CrisisMMD](https://doi.org/10.1609/icwsm.v12i1.14983) defines the image damage-severity task; the [official dataset page](https://crisisnlp.qcri.org/crisismmd) reports 18,082 images overall and 3,526 severity rows.",
        "- [Alam et al. (ASONAM 2020)](https://doi.org/10.1109/ASONAM49781.2020.9381294) explicitly warns that random social-media splits can leak exact/near duplicates and constructs non-overlapping train/dev/test sets. V3 follows this principle more strictly across all experimental cohorts, although it does not reuse their consolidated benchmark split.",
        "- [Ofli et al. (ISCRAM 2020)](https://arxiv.org/abs/2004.11838) used a 70/15/15 split for informativeness and humanitarian tasks while grouping multi-image tweets, but explicitly excluded damage severity because that label is image-only. It does not validate a particular severity split for this study.",
        "- [Shetty et al. (Multimedia Tools and Applications)](https://doi.org/10.1007/s11042-024-19818-0) evaluates CrisisMMD multimodally and identifies class imbalance as a key reason severity assessment is harder. It supports reporting macro-F1/per-class behavior and a natural-distribution clean view, not replacing the paired attack design with majority-dominated accuracy.",
        "",
        "## Decision and next analyses",
        "",
        "- Retain V3 main-720 as the primary balanced paired robustness cohort; never describe it as official or natural-prevalence.",
        "- Run clean-only inference on all 3,474 locally valid rows and use duplicate-cluster bootstrap intervals, event metrics, event-by-class metrics, and leave-one-event-out sensitivity.",
        "- Run the exact official 529-row test as a secondary clean comparability analysis, preserving its natural class distribution.",
        "- Report class-balanced main estimates first, then class-prior post-stratification and the four-row exact-label-conflict sensitivity.",
        "- If a future cohort is rebuilt, create V4 side-by-side: exclude exact-SHA label conflicts, allocate main first, use class-balanced but within-class event-proportional quotas, predeclare precision/power, regenerate attacks, and rerun every model. Do not overwrite V3 after results exist.",
        "",
        "## Reproducible artifacts",
        "",
        "- `data/v3/manifests/natural_clean_all.csv` (ignored local derivative; 3,474 clean rows)",
        "- `data/v3/manifests/official_test_clean.csv` (ignored local derivative; 529 clean rows)",
        "- `reports/v3/dataset_protocol/` (aggregate, tweet-redacted audit tables)",
        "- `configs/v3/dataset_evaluation.yaml` (secondary cohort definitions)",
        "",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def validate() -> dict:
    checks = []
    specs = [
        (NATURAL_MANIFEST, "natural_clean_all", 3474, {"little_or_no_damage": 474, "mild_damage": 829, "severe_damage": 2171}),
        (OFFICIAL_TEST_MANIFEST, "official_test", 529, {"little_or_no_damage": 71, "mild_damage": 126, "severe_damage": 332}),
    ]
    for path, split, expected, classes in specs:
        if not path.is_file():
            checks.append({"manifest": str(path), "status": "missing"})
            continue
        frame = pd.read_csv(path, dtype=str).fillna("")
        failures = []
        if len(frame) != expected:
            failures.append(f"expected {expected} rows, found {len(frame)}")
        if set(frame.condition) != {"clean"} or set(frame.split_name) != {split}:
            failures.append("unexpected condition or split_name")
        if frame.duplicated(["sample_id", "condition"]).any():
            failures.append("duplicate sample-condition keys")
        required_metadata = {
            "duplicate_cluster_id", "label_conflict_exact_sha", "v3_input_eligible",
            "v3_any_cohort_overlap", "v3_prompt_cohort_overlap",
        }
        if not required_metadata.issubset(frame.columns):
            failures.append(
                f"missing audit metadata: {sorted(required_metadata - set(frame.columns))}"
            )
        if _counts(frame, "ground_truth") != classes:
            failures.append(f"class counts differ: {_counts(frame, 'ground_truth')}")
        missing_paths = sum(not resolve(path_value).is_file() for path_value in frame.condition_image_path)
        if missing_paths:
            failures.append(f"{missing_paths} image paths are missing")
        checks.append({
            "manifest": str(path.relative_to(ROOT)),
            "rows": len(frame),
            "status": "passed" if not failures else "failed",
            "failures": failures,
        })
    result = {"status": "passed" if all(x["status"] == "passed" for x in checks) else "failed", "checks": checks}
    if result["status"] != "passed":
        raise RuntimeError(json.dumps(result, indent=2))
    return result


def build() -> dict:
    processed = pd.read_csv(SOURCE, dtype=str).fillna("")
    clustered = build_duplicate_clusters(processed)
    official = _official_rows(processed)
    conflicts = _exact_conflicts(official)
    conflict_hashes = set(conflicts.sha256) if len(conflicts) else set()
    eligible, _, old_prompt_clusters = _eligible_pool(clustered)
    split_clusters = {}
    for split in ("pilot", "main", "style_ablation", "size_ablation", "prompt_validation"):
        frame = pd.read_csv(
            ROOT / "data" / "v3" / "splits" / f"{split}.csv", dtype=str
        ).fillna("")
        split_clusters[split] = set(frame.duplicate_cluster_id)
    all_v3_clusters = set().union(*split_clusters.values())
    prompt_clusters = (
        old_prompt_clusters | split_clusters["pilot"] | split_clusters["prompt_validation"]
    )
    natural, official_manifest = build_clean_manifests(
        clustered, official, conflict_hashes, set(eligible.duplicate_cluster_id),
        all_v3_clusters, prompt_clusters,
    )
    report = build_audit(clustered, official, conflicts, natural, official_manifest)
    report["manifest_validation"] = validate()
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "validate", "audit"])
    args = parser.parse_args()
    if args.command == "build":
        result = build()
    elif args.command == "validate":
        result = validate()
    else:
        if not REPORT.is_file():
            raise SystemExit("Audit does not exist; run the build command first")
        result = json.loads(REPORT.read_text(encoding="utf-8"))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
