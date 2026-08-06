from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.config import resolve, load_yaml
from src.dataset_utils import (LABELS, canonical_column, find_column, image_candidates,
                               image_info, normalize_label, perceptual_hash, read_annotation,
                               sha256_file)


ALIASES = {
    "event": ["event_name", "event", "crisis_event", "disaster_type"],
    "tweet_id": ["tweet_id", "tweetid", "id"],
    "image_id": ["image_id", "imageid", "image", "filename", "image_filename", "image_path"],
    "tweet_text": ["tweet_text", "text", "tweet", "description", "content"],
    "damage": ["damage_severity", "damage", "damage_label", "severity", "label"],
}


def choose_column(df: pd.DataFrame, key: str) -> str | None:
    return find_column(df.columns, [canonical_column(x) for x in ALIASES[key]])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/dataset.yaml")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    raw = resolve(cfg["raw_dir"])
    images = image_candidates(raw)
    by_name = {p.name.lower(): p for p in images}
    by_stem = {p.stem.lower(): p for p in images}
    annotations = [p for p in raw.rglob("*") if p.is_file() and p.suffix.lower() in {".tsv", ".csv", ".txt", ".json", ".jsonl"}]
    records, issues = [], []
    seen_sha = set()
    for ann in annotations:
        df = read_annotation(ann)
        if df.empty:
            continue
        cols = {key: choose_column(df, key) for key in ALIASES}
        if not cols["damage"] or not cols["image_id"]:
            continue
        for idx, row in df.iterrows():
            original_label = row.get(cols["damage"])
            label = normalize_label(original_label)
            image_ref = str(row.get(cols["image_id"], ""))
            image = by_name.get(Path(image_ref).name.lower()) or by_stem.get(Path(image_ref).stem.lower())
            if image is None and image_ref:
                matches = [p for p in images if image_ref.lower() in str(p).lower()]
                image = matches[0] if matches else None
            tweet = "" if not cols["tweet_text"] else str(row.get(cols["tweet_text"], "") or "").strip()
            if label is None:
                issues.append({"annotation": str(ann), "row": int(idx), "reason": "unsupported_or_missing_damage_label", "value": str(original_label)})
                continue
            if image is None:
                issues.append({"annotation": str(ann), "row": int(idx), "reason": "missing_image", "image_ref": image_ref})
                continue
            if not tweet:
                issues.append({"annotation": str(ann), "row": int(idx), "reason": "empty_tweet_text", "image_ref": image_ref})
                continue
            try:
                info = image_info(image)
                digest = sha256_file(image)
                phash = perceptual_hash(image)
            except Exception as exc:
                issues.append({"annotation": str(ann), "row": int(idx), "reason": "unreadable_image", "error": str(exc)})
                continue
            if digest in seen_sha:
                issues.append({"annotation": str(ann), "row": int(idx), "reason": "duplicate_image_sha256", "image_ref": image_ref})
                continue
            seen_sha.add(digest)
            event = "unknown_event" if not cols["event"] else str(row.get(cols["event"], "unknown_event") or "unknown_event").strip()
            if event in {"", "nan", "None", "unknown_event"}:
                parts = image.parts
                if "data_image" in parts:
                    pos = parts.index("data_image")
                    if pos + 1 < len(parts): event = parts[pos + 1]
            tweet_id = "" if not cols["tweet_id"] else str(row.get(cols["tweet_id"], "") or "")
            image_id = image_ref or image.stem
            sample_id = f"{event}__{tweet_id or image_id}__{image.stem}".replace("/", "_")
            records.append({
                "sample_id": sample_id, "event_name": event, "tweet_id": tweet_id,
                "image_id": image_id, "image_path": str(image.relative_to(resolve("."))),
                "tweet_text": tweet, "damage_label_original": str(original_label),
                "damage_label_normalized": label, "image_width": info["width"],
                "image_height": info["height"], "image_format": info["format"],
                "sha256": digest, "perceptual_hash": phash, "source_annotation_file": str(ann.relative_to(resolve("."))),
            })
    out = pd.DataFrame(records)
    if not out.empty:
        out = out.drop_duplicates("sample_id").sort_values(["damage_label_normalized", "sample_id"]).reset_index(drop=True)
    csv_path, parquet_path = resolve(cfg["processed_manifest_csv"]), resolve(cfg["processed_manifest_parquet"])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    out.to_parquet(parquet_path, index=False)
    reports = resolve("reports")
    reports.mkdir(exist_ok=True)
    (reports / "dataset_issues.json").write_text(json.dumps(issues, indent=2, ensure_ascii=False), encoding="utf-8")
    counts = out["damage_label_normalized"].value_counts().to_dict() if not out.empty else {}
    if not out.empty:
        out.groupby(["damage_label_normalized", "event_name"], dropna=False).size().reset_index(name="n").to_csv(reports / "dataset_distribution.csv", index=False)
    else:
        pd.DataFrame(columns=["damage_label_normalized", "event_name", "n"]).to_csv(reports / "dataset_distribution.csv", index=False)
    summary = ["# Dataset summary", "", f"Valid unique samples: {len(out)}", "", "## Class counts", ""]
    summary += [f"- `{k}`: {counts.get(k, 0)}" for k in LABELS]
    summary += ["", "Raw data is never modified. Exclusions are recorded in `reports/dataset_issues.json`."]
    (reports / "dataset_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    print(f"annotations={len(annotations)} images={len(images)} valid={len(out)} issues={len(issues)}")


if __name__ == "__main__":
    main()
