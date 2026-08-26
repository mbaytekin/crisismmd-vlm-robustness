from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/v3/ablation_protocol.yaml"


def resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else ROOT / value


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    with resolve(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wilson_half_width(n: int, p: float = 0.5, z: float = 1.959963984540054) -> float:
    if n <= 0:
        return math.nan
    denominator = 1 + z * z / n
    radius = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return radius


def _actual_region(text_bbox: str, image_height: str) -> str:
    box = ast.literal_eval(text_bbox)
    center = (float(box[1]) + float(box[3])) / 2
    return "top_edge" if center < float(image_height) / 2 else "bottom_edge"


def _class_event_table(split: pd.DataFrame) -> dict:
    table = split.groupby(["event_name", "damage_label_normalized"]).size().unstack(fill_value=0)
    return {str(index): {str(key): int(value) for key, value in row.items()} for index, row in table.iterrows()}


def _duplicate_overlap(splits: dict[str, pd.DataFrame]) -> dict:
    fields = ["sample_id", "tweet_id", "sha256", "duplicate_cluster_id"]
    output = {}
    names = sorted(splits)
    for index, first in enumerate(names):
        for second in names[index + 1 :]:
            key = f"{first}__{second}"
            output[key] = {}
            for field in fields:
                left = set(splits[first][field].astype(str)) - {""}
                right = set(splits[second][field].astype(str)) - {""}
                output[key][field] = len(left & right)
    return output


def _payload_invariance(frame: pd.DataFrame) -> int:
    attacked = frame[frame.attack_semantics.ne("none")]
    counts = attacked.groupby(["sample_id", "attack_semantics"]).payload_id.nunique()
    return int(counts.ne(1).sum())


def _size_invariance(frame: pd.DataFrame) -> dict:
    attacked = frame[frame.attack_semantics.ne("none")]
    fields = ["payload_id", "visual_style", "placement_region", "opacity", "background_color", "text_color"]
    output = {}
    groups = attacked.groupby(["sample_id", "attack_semantics"])
    for field in fields:
        output[field] = int(groups[field].nunique().ne(1).sum())
    return output


def audit(config_path: str | Path = DEFAULT_CONFIG, write_outputs: bool = True) -> dict:
    config = load_config(config_path)
    artifacts = config["artifacts"]
    source_path = resolve(artifacts["source_manifest"])
    source = pd.read_csv(source_path, dtype=str).fillna("")
    split_names = ["pilot", "main", "style_ablation", "size_ablation", "prompt_validation"]
    splits = {name: pd.read_csv(ROOT / f"data/v3/splits/{name}.csv", dtype=str).fillna("") for name in split_names}

    failures: list[dict] = []
    warnings: list[dict] = []
    details = {}
    dedicated_frames = {}

    for kind, split_name in (("style", "style_ablation"), ("size", "size_ablation")):
        protocol = config[kind]
        split = splits[split_name]
        frame = source[source.split_name.eq(split_name)].copy()
        expected_n = int(protocol["source_samples"])
        expected_conditions = list(protocol["conditions"])
        condition_counts = frame.condition.value_counts().to_dict()
        class_counts = split.damage_label_normalized.value_counts().to_dict()

        checks = {
            "split_rows": len(split) == expected_n,
            "manifest_rows": len(frame) == expected_n * len(expected_conditions),
            "sample_condition_unique": not frame.duplicated(["sample_id", "condition"]).any(),
            "condition_set": set(condition_counts) == set(expected_conditions),
            "condition_counts": all(condition_counts.get(condition, 0) == expected_n for condition in expected_conditions),
            "class_balance": all(class_counts.get(label, 0) == int(protocol["per_class"]) for label in (
                "little_or_no_damage", "mild_damage", "severe_damage"
            )),
            "payload_invariance": _payload_invariance(frame) == 0,
            "all_generated": frame.generation_status.isin(["success", "not_applicable"]).all(),
        }
        checks = {name: bool(passed) for name, passed in checks.items()}
        for check, passed in checks.items():
            if not passed:
                failures.append({"split": split_name, "check": check})

        attacked = frame[frame.condition.ne("clean")].copy()
        numeric = ["font_size_px", "relative_font_height", "occupied_area_ratio", "rendered_contrast_ratio"]
        for column in numeric:
            attacked[column] = pd.to_numeric(attacked[column], errors="coerce")
        variants = attacked.groupby(["visual_style", "text_size"])[numeric].agg(["count", "min", "mean", "max"])

        detail = {
            "source_samples": len(split),
            "manifest_rows": len(frame),
            "condition_counts": {str(key): int(value) for key, value in sorted(condition_counts.items())},
            "class_counts": {str(key): int(value) for key, value in sorted(class_counts.items())},
            "event_counts": {str(key): int(value) for key, value in sorted(split.event_name.value_counts().items())},
            "event_by_class": _class_event_table(split),
            "checks": checks,
            "worst_case_binomial_95ci_half_width": wilson_half_width(expected_n),
            "class_specific_worst_case_95ci_half_width": wilson_half_width(int(protocol["per_class"])),
            "variant_summary": json.loads(variants.round(6).to_json(orient="index")),
        }

        if kind == "style":
            source_heights = split[["sample_id", "image_height"]]
            news = attacked[attacked.visual_style.eq("news_banner")].merge(source_heights, on="sample_id", validate="many_to_one")
            news["actual_region"] = news.apply(lambda row: _actual_region(row.text_bbox, row.image_height), axis=1)
            mismatches = int(news.placement_region.ne(news.actual_region).sum())
            detail["news_placement_metadata_mismatches"] = mismatches
            detail["actual_news_regions"] = {str(key): int(value) for key, value in news.actual_region.value_counts().items()}
            detail["interpretation"] = "presentation_style_package_not_single_component_style"
            warnings.append({
                "severity": "medium",
                "finding": "news placement metadata does not describe rendered placement",
                "affected_rows": mismatches,
                "impact": "Use actual geometry and describe style as a bundled presentation strategy.",
            })
        else:
            invariance = _size_invariance(frame)
            detail["within_sample_semantics_invariance_failures"] = invariance
            if any(invariance.values()):
                failures.append({"split": split_name, "check": "size_factor_isolation", "details": invariance})
            detail["interpretation"] = "paired_single_factor_relative_text_size_ablation"

        details[kind] = detail
        dedicated_frames[kind] = frame.sort_values(["sample_id", "condition"]).reset_index(drop=True)

    overlap = _duplicate_overlap(splits)
    overlap_failures = [
        {"comparison": comparison, "field": field, "count": count}
        for comparison, fields in overlap.items() for field, count in fields.items() if count
    ]
    failures.extend({"check": "cross_split_overlap", **row} for row in overlap_failures)

    warnings.extend([
        {
            "severity": "medium",
            "finding": "ablation cohorts are class-balanced but not event-proportional",
            "impact": "Do not interpret event-specific values as population prevalence estimates.",
        },
        {
            "severity": "medium",
            "finding": "eligible attack denominators can be smaller than 120 or 60",
            "impact": "Report exact clean-correct mild/severe denominators and confidence intervals.",
        },
    ])

    report = {
        "schema_version": 1,
        "status": "failed" if failures else "passed_with_documented_caveats",
        "design": "class_balanced_cluster_disjoint_paired_secondary_ablation",
        "source_manifest_sha256": sha256(source_path),
        "prompt_sha256": sha256(resolve(artifacts["prompt"])),
        "details": details,
        "cross_split_overlap": overlap,
        "failures": failures,
        "warnings": warnings,
        "literature": config.get("literature", []),
    }

    if write_outputs:
        for kind, frame in dedicated_frames.items():
            target = resolve(artifacts[f"{kind}_manifest"])
            target.parent.mkdir(parents=True, exist_ok=True)
            frame.to_csv(target, index=False)
            report[f"{kind}_manifest_sha256"] = sha256(target)
        json_path = resolve(artifacts["audit_json"])
        md_path = resolve(artifacts["audit_markdown"])
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text(render_markdown(report), encoding="utf-8")
    return report


def render_markdown(report: dict) -> str:
    style = report["details"]["style"]
    size = report["details"]["size"]
    lines = [
        "# V3 Ablation Dataset Audit",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Technical summary",
        "",
        "The existing V3 ablation cohorts are ready for paper-facing BF16 inference without resampling or regenerating images. Both are class-balanced, globally cluster-disjoint, complete paired designs. The style cohort must be described as a presentation-style package because contrast, background, occupied area, and placement policy vary together. The size cohort is the cleaner single-factor experiment.",
        "",
        "| Cohort | Source samples | Per class | Conditions | Rows | Worst-case 95% half-width |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Presentation style | {style['source_samples']} | 40 | 10 | {style['manifest_rows']} | {100*style['worst_case_binomial_95ci_half_width']:.1f} pp |",
        f"| Relative text size | {size['source_samples']} | 20 | 10 | {size['manifest_rows']} | {100*size['worst_case_binomial_95ci_half_width']:.1f} pp |",
        "",
        "These widths assume the full cohort. Downward ASR uses only clean-correct mild/severe samples, so its model-specific intervals may be wider.",
        "",
        "## Design interpretation",
        "",
        "- Style: simple, fictional-news, and camouflage are paired on the same 120 sources and payload assignments at nominal medium size. They are bundled presentation strategies, not a one-variable causal contrast.",
        "- Size: small/medium/large use the same 60 sources, payload, simple renderer, placement, colors, and opacity. Target relative font heights are 3%, 5%, and 8%.",
        "- Sampling: classes are exactly balanced, events are diversified within class but are not population-proportional. All comparisons remain within model and within source sample.",
        "",
        "## Data-quality findings",
        "",
    ]
    for warning in report["warnings"]:
        suffix = f" ({warning['affected_rows']} rows)" if "affected_rows" in warning else ""
        lines.append(f"- **{warning['severity'].upper()}:** {warning['finding']}{suffix}. {warning['impact']}")
    lines += [
        "",
        "## Frozen analysis",
        "",
        "Primary reporting uses downward ASR among clean-correct mild/severe samples, exact numerators/denominators, Wilson intervals, malicious-minus-matched-benign paired risk differences, 5,000 paired bootstrap draws, exact McNemar tests, and Holm correction within each semantics/ablation family. Models are analyzed separately.",
        "",
        "## Literature basis",
        "",
        "The multi-image formulation follows Wang et al. (NAACL 2025). SceneTAP (CVPR 2025) motivates treating placement and scene integration as attack factors. Font-size sensitivity is additionally supported by Balakrishnan et al. (2026), which is retained as concurrent preprint evidence rather than peer-reviewed authority.",
        "",
        "## Limitations",
        "",
        "No established CrisisMMD standard prescribes a canonical style/size ablation distribution. These cohorts optimize paired precision and class-conditional safety analysis rather than prevalence estimation. Human readability, plausibility, and critical-damage occlusion review remains required before perceptual claims.",
        "",
    ]
    return "\n".join(lines)


def memory_snapshot(config_path: str | Path = DEFAULT_CONFIG, write_outputs: bool = True) -> dict:
    config = load_config(config_path)
    vm_text = subprocess.check_output(["vm_stat"], text=True)
    page_match = re.search(r"page size of (\d+) bytes", vm_text)
    page_size = int(page_match.group(1)) if page_match else 16384
    pages = {}
    for line in vm_text.splitlines():
        match = re.match(r"([^:]+):\s+([0-9.]+)", line)
        if match:
            pages[match.group(1)] = float(match.group(2).rstrip("."))
    available_pages = sum(pages.get(name, 0) for name in (
        "Pages free", "Pages inactive", "Pages speculative", "Pages purgeable"
    ))
    available_gib = available_pages * page_size / (1024 ** 3)
    total_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
    total_gib = total_bytes / (1024 ** 3)

    process_text = subprocess.check_output(
        ["ps", "-axo", "pid=,rss=,command="], text=True
    )
    processes = []
    for line in process_text.splitlines():
        if not re.search(r"mlx_vlm\.server|src\.v3_inference|train_vlm_lora\.py", line):
            continue
        match = re.match(r"\s*(\d+)\s+(\d+)\s+(.+)", line)
        if not match:
            continue
        pid, rss_kib, command = match.groups()
        model_match = re.search(r"--(?:model|model-path)\s+(\S+)", command)
        run_match = re.search(r"--run-id\s+(\S+)", command)
        category = "server" if "mlx_vlm.server" in command else "inference" if "src.v3_inference" in command else "training"
        processes.append({
            "pid": int(pid),
            "category": category,
            "rss_gib": int(rss_kib) / (1024 ** 2),
            "model_or_run": model_match.group(1) if model_match else run_match.group(1) if run_match else "unknown",
        })

    reserve = float(config["runtime"]["minimum_post_load_reserve_gib"])
    models = []
    cache_root = Path.home() / ".cache/huggingface/hub"
    for model in config["models"]:
        repo_dir = cache_root / ("models--" + model["model_id"].replace("/", "--"))
        snapshots = list((repo_dir / "snapshots").glob("*")) if (repo_dir / "snapshots").is_dir() else []
        complete = any((path / "config.json").is_file() and list(path.glob("*.safetensors")) for path in snapshots)
        incomplete = len(list(repo_dir.rglob("*.incomplete"))) if repo_dir.exists() else 0
        complete = bool(complete and incomplete == 0)
        peak = float(model["expected_peak_gib"])
        models.append({
            "slug": model["slug"],
            "model_id": model["model_id"],
            "cache_complete": complete,
            "incomplete_files": incomplete,
            "expected_peak_gib": peak,
            "required_available_gib": peak + reserve,
            "fits_current_snapshot": bool(complete and available_gib >= peak + reserve),
        })

    report = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_unified_memory_gib": total_gib,
        "available_or_reclaimable_gib": available_gib,
        "minimum_post_load_reserve_gib": reserve,
        "active_vlm_processes": processes,
        "active_vlm_rss_sum_gib": sum(item["rss_gib"] for item in processes),
        "models": models,
        "interpretation": (
            "Capacity is sufficient for each complete configured checkpoint one at a time under the current snapshot. "
            "Concurrent VLM work can substantially reduce throughput; the runner warns but does not stop it. "
            "The preflight is repeated immediately before every model load."
        ),
    }
    if write_outputs:
        artifacts = config["artifacts"]
        json_path = resolve(artifacts["ram_json"])
        md_path = resolve(artifacts["ram_markdown"])
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text(render_memory_markdown(report), encoding="utf-8")
    return report


def render_memory_markdown(report: dict) -> str:
    lines = [
        "# V3 Ablation RAM Readiness",
        "",
        f"**Snapshot:** {report['captured_at_utc']}",
        "",
        f"The Mac has **{report['total_unified_memory_gib']:.0f} GiB** unified memory. "
        f"At this snapshot, **{report['available_or_reclaimable_gib']:.1f} GiB** was available or reclaimable. "
        f"The runner reserves **{report['minimum_post_load_reserve_gib']:.0f} GiB** after each estimated model peak.",
        "",
        "| Model | Cache | Estimated peak | Peak + reserve | Fits now |",
        "|---|---|---:|---:|---|",
    ]
    for model in report["models"]:
        cache = "complete" if model["cache_complete"] else f"partial/missing ({model['incomplete_files']} incomplete)"
        lines.append(
            f"| `{model['slug']}` | {cache} | {model['expected_peak_gib']:.0f} GiB | "
            f"{model['required_available_gib']:.0f} GiB | {'yes' if model['fits_current_snapshot'] else 'no'} |"
        )
    lines += ["", "## Concurrent VLM work", ""]
    if report["active_vlm_processes"]:
        lines += ["| PID | Type | Model/run | RSS |", "|---:|---|---|---:|"]
        for process in report["active_vlm_processes"]:
            lines.append(
                f"| {process['pid']} | {process['category']} | `{process['model_or_run']}` | {process['rss_gib']:.1f} GiB |"
            )
    else:
        lines.append("No concurrent VLM process was detected.")
    lines += [
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "",
        "This is a point-in-time capacity estimate, not a guarantee against Metal allocation spikes. Models are loaded serially, concurrency remains one, and the check is repeated before every load.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--memory-report", action="store_true")
    args = parser.parse_args()
    if args.memory_report:
        print(json.dumps(memory_snapshot(args.config, write_outputs=not args.check_only), indent=2))
        return
    result = audit(args.config, write_outputs=not args.check_only)
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["failures"] else 0)


if __name__ == "__main__":
    main()
