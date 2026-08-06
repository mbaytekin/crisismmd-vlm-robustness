from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from PIL import Image, ImageChops, ImageStat

from src.config import resolve, load_yaml


def validate(split: str, config_path: str, manifest_path: str = "") -> tuple[dict, pd.DataFrame]:
    cfg = load_yaml(config_path)
    path = resolve(manifest_path) if manifest_path else resolve(f"data/attacks/{split}_attack_manifest.csv")
    if not path.exists():
        return {"split": split, "status": "missing_manifest", "n_records": 0, "n_failures": 1}, pd.DataFrame([{"split": split, "reason": "missing_manifest"}])
    df = pd.read_csv(path, dtype=str)
    checks = []
    failures = []
    warnings = []
    for _, row in df.iterrows():
        reasons = []
        out = resolve(row.attacked_image_path)
        original = resolve(row.original_image_path)
        if not row.text_content or not str(row.text_content).strip(): reasons.append("empty_text")
        if str(row.get("text_truncated", "")).lower() == "true": reasons.append("text_truncated")
        try:
            if int(row.get("text_line_count", 0) or 0) > 2:
                warnings.append({"sample_id": row.sample_id, "condition": row.condition, "valid": True, "reasons": "warning:more_than_two_text_lines", "reason": "more_than_two_text_lines"})
        except (TypeError, ValueError):
            pass
        if row.generation_status != "success" or not out.exists(): reasons.append("generation_failed_or_missing")
        try:
            with Image.open(original) as a, Image.open(out) as b:
                if a.size != b.size: reasons.append("dimensions_changed")
                bbox = json.loads(row.text_bbox)
                if len(bbox) != 4 or not (0 <= int(bbox[0]) <= int(bbox[2]) <= a.width and 0 <= int(bbox[1]) <= int(bbox[3]) <= a.height): reasons.append("bbox_out_of_bounds")
                area = float(row.occupied_area_ratio)
                if area <= 0: reasons.append("area_limit")
                elif area > float(cfg["max_occupied_area_ratio"]):
                    # On very small images the configured minimum readable font
                    # can make the cap geometrically impossible. Keep the sample,
                    # but surface it as an explicit warning for human review.
                    if int(row.font_size_px) <= int(cfg["min_font_size_px"]): warnings.append({"sample_id": row.sample_id, "condition": row.condition, "valid": True, "reasons": "warning:area_limit_unavoidable_at_min_font", "reason": "area_limit_unavoidable_at_min_font"})
                    else: reasons.append("area_limit")
                if ImageStat.Stat(ImageChops.difference(a.convert("RGB"), b.convert("RGB"))).mean == [0.0, 0.0, 0.0]: reasons.append("identical_to_original")
        except Exception as exc:
            reasons.append(f"unreadable:{type(exc).__name__}")
        checks.append({"sample_id": row.sample_id, "condition": row.condition, "valid": not reasons, "reasons": ";".join(reasons)})
        failures.extend([{**checks[-1], "reason": reason} for reason in reasons])
    result = {"split": split, "status": "passed" if not failures else "failed", "n_records": len(df), "n_valid": len(df) - len(failures), "n_failures": len(failures), "n_warnings": len(warnings), "duplicate_sample_condition": int(df.duplicated(["sample_id", "condition"]).sum()), "conditions": sorted(df.condition.unique().tolist())}
    return result, pd.DataFrame(failures + warnings or [{"split": split, "reason": "none"}])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["pilot", "test"], default="pilot")
    ap.add_argument("--config", default="configs/attacks.yaml")
    ap.add_argument("--manifest", default="")
    args = ap.parse_args()
    results, failures = validate(args.split, args.config, args.manifest)
    report_dir = resolve("reports")
    report_dir.mkdir(exist_ok=True)
    (report_dir / "attack_generation_validation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    failures.to_csv(report_dir / "attack_generation_validation.csv", index=False)
    (report_dir / f"attack_generation_validation_{args.split}.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    failures.to_csv(report_dir / f"attack_generation_validation_{args.split}.csv", index=False)
    print(json.dumps(results, indent=2))
    if results["status"] != "passed": raise SystemExit(1)


if __name__ == "__main__":
    main()
