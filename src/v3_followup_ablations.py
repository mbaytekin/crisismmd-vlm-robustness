"""Build and analyze the predeclared V3 supervisor follow-up ablations."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from PIL import Image, ImageDraw, ImageFont

from src.config import ROOT, resolve
from src.v3_final_analysis import (
    LABELS,
    LEVEL,
    _clean_summary,
    _paired,
    _rate,
    _write_csv,
    exact_mcnemar,
    holm_adjust,
    paired_bootstrap_difference,
    prepare_run,
)


DEFAULT_CONFIG = ROOT / "configs" / "v3" / "followup_ablation_protocol.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    return yaml.safe_load(resolve(path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_index(key: str, count: int) -> int:
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:16], 16) % count


def _base_clean_rows(config: dict, source_split: str) -> pd.DataFrame:
    source = pd.read_csv(resolve(config["shared"]["source_manifest"]), dtype=str).fillna("")
    clean = source[source.split_name.eq(source_split) & source.condition.eq("clean")].copy()
    if clean.sample_id.duplicated().any():
        raise ValueError(f"Duplicate clean rows in {source_split}")
    return clean.sort_values("sample_id").reset_index(drop=True)


def _payload(config: dict, condition: str, sample_id: str) -> tuple[str, str]:
    values = config["text_rhetoric"]["payloads"][condition]
    ids = sorted(values)
    payload_id = ids[stable_index(f"{sample_id}:{condition}", len(ids))]
    return payload_id, values[payload_id]


def build_text_manifest(config: dict) -> pd.DataFrame:
    spec = config["text_rhetoric"]
    clean = _base_clean_rows(config, spec["source_split"])
    if len(clean) != int(spec["source_samples"]):
        raise ValueError(f"Expected {spec['source_samples']} text sources, got {len(clean)}")
    malicious = set(spec["malicious_to_control"])
    rows = []
    for source in clean.to_dict("records"):
        for condition in spec["conditions"]:
            row = dict(source)
            row["split_name"] = spec["split_name"]
            row["condition"] = condition
            row["text_rhetoric_variant"] = "none" if condition == "clean" else condition
            if condition == "clean":
                row.update({
                    "attack_modality": "none", "attack_semantics": "none",
                    "payload_id": "", "payload_text": "",
                    "condition_tweet": row["original_tweet"],
                    "generation_status": "not_applicable", "generation_error": "",
                })
            else:
                payload_id, payload_text = _payload(config, condition, row["sample_id"])
                if condition in malicious:
                    semantics = "direct_instruction" if condition.startswith("direct_") else "misleading_claim"
                else:
                    semantics = "benign"
                row.update({
                    "attack_modality": "text", "attack_semantics": semantics,
                    "visual_style": "none", "text_size": "none",
                    "payload_id": payload_id, "payload_text": payload_text,
                    "condition_image_path": row["original_image_path"],
                    "condition_tweet": f"{payload_text}\n\n{row['original_tweet']}",
                    "generation_status": "not_applicable", "generation_error": "",
                })
            rows.append(row)
    frame = pd.DataFrame(rows)
    target = resolve(spec["manifest"])
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)
    return frame


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or font.getbbox(candidate)[2] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _render_point_overlay(
    source_path: Path, target_path: Path, text: str, point_size: int,
    ppi: int, font_path: Path, placement: str, opacity: float,
) -> dict:
    pixel_size = max(1, round(point_size * ppi / 72))
    font = ImageFont.truetype(str(font_path), pixel_size)
    with Image.open(source_path) as opened:
        base = opened.convert("RGBA")
    width, height = base.size
    left, right = round(width * 0.04), round(width * 0.96)
    padding = max(2, round(pixel_size * 0.5))
    available_width = max(8, right - left - 2 * padding)
    lines = _wrap(text, font, available_width)
    gap = max(1, round(pixel_size * 0.15))
    line_heights = [max(1, font.getbbox(line)[3] - font.getbbox(line)[1]) for line in lines]
    box_height = 2 * padding + sum(line_heights) + gap * max(0, len(lines) - 1)
    if box_height > height:
        raise ValueError(f"{point_size} pt payload exceeds image height: {source_path}")
    top = 0 if placement == "top_edge" else height - box_height
    box = (left, top, right, top + box_height)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(box, fill=(0, 0, 0, round(opacity * 255)))
    y = top + padding
    for line, line_height in zip(lines, line_heights):
        draw.text((left + padding, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height + gap
    target_path.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(base, overlay).convert("RGB").save(
        target_path, format="WEBP", lossless=True, quality=100, method=1
    )
    occupied = ((right - left) * box_height) / (width * height)
    return {
        "text_bbox": json.dumps(list(box), separators=(",", ":")),
        "font_size_pt": point_size,
        "font_size_px": pixel_size,
        "relative_font_height": pixel_size / height,
        "line_count": len(lines),
        "occupied_area_ratio": occupied,
        "opacity": opacity,
        "background_color": "0,0,0",
        "text_color": "255,255,255",
        "rendered_contrast_ratio": 21.0,
        "placement_region": placement,
        "raster_ppi": ppi,
    }


def build_size_manifest(config: dict) -> pd.DataFrame:
    spec = config["size_response_pt"]
    clean = _base_clean_rows(config, spec["source_split"])
    if len(clean) != int(spec["source_samples"]):
        raise ValueError(f"Expected {spec['source_samples']} size sources, got {len(clean)}")
    assignments = pd.read_csv(resolve(config["shared"]["payload_assignments"]), dtype=str).fillna("")
    assignments = assignments.set_index("sample_id")
    font_path = resolve(spec["font_path"])
    if sha256(font_path) != spec["font_sha256"]:
        raise ValueError("The size-response font does not match the frozen SHA-256")
    points = [int(value) for value in spec["nominal_points"]]
    opacity = float(spec["fixed"]["opacity"])
    rows = []
    for source in clean.to_dict("records"):
        clean_row = dict(source)
        clean_row.update({
            "split_name": spec["split_name"], "condition": "clean",
            "font_size_pt": "", "raster_ppi": spec["raster_ppi"],
            "font_family": "DejaVu Sans", "font_sha256": spec["font_sha256"],
        })
        rows.append(clean_row)
        assigned = assignments.loc[source["sample_id"]]
        placement = "top_edge" if stable_index(source["sample_id"], 2) == 0 else "bottom_edge"
        for short, field in (
            ("benign", "benign"),
            ("direct", "direct_instruction"),
            ("misleading", "misleading_claim"),
        ):
            payload_id = assigned[f"{field}_payload_id"]
            payload_text = assigned[f"{field}_payload_text"]
            semantics = "benign" if short == "benign" else field
            for point_size in points:
                condition = f"{short}_pt{point_size:02d}"
                rel_path = Path(spec["image_root"]) / f"{short}__pt{point_size:02d}" / f"{source['sample_id']}.webp"
                metadata = _render_point_overlay(
                    resolve(source["original_image_path"]), resolve(rel_path), payload_text,
                    point_size, int(spec["raster_ppi"]), font_path, placement, opacity,
                )
                if metadata["occupied_area_ratio"] > float(spec["max_occupied_area_ratio"]):
                    raise ValueError(
                        f"Overlay area {metadata['occupied_area_ratio']:.3f} exceeds frozen limit for {condition}"
                    )
                row = dict(source)
                row.update({
                    "split_name": spec["split_name"], "condition": condition,
                    "attack_modality": "image", "attack_semantics": semantics,
                    "visual_style": "simple_black_edge_overlay",
                    "text_size": f"{point_size}pt", "payload_id": payload_id,
                    "payload_text": payload_text, "condition_image_path": str(rel_path),
                    "condition_tweet": row["original_tweet"],
                    "visual_key": f"{short}__pt{point_size:02d}",
                    "font_family": "DejaVu Sans", "font_sha256": spec["font_sha256"],
                    "template_version": "point_size_response_v1",
                    "generation_status": "success", "generation_error": "",
                    **metadata,
                })
                rows.append(row)
    frame = pd.DataFrame(rows)
    target = resolve(spec["manifest"])
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)
    return frame


def audit_manifest(frame: pd.DataFrame, config: dict, kind: str) -> dict:
    spec = config["text_rhetoric" if kind == "text" else "size_response_pt"]
    expected_conditions = (
        list(spec["conditions"])
        if kind == "text"
        else ["clean", *[
            f"{semantics}_pt{point:02d}"
            for semantics in ("benign", "direct", "misleading")
            for point in spec["nominal_points"]
        ]]
    )
    counts = frame.condition.value_counts()
    failures = []
    if frame.duplicated(["sample_id", "condition"]).any():
        failures.append("duplicate_sample_condition")
    if set(counts.index) != set(expected_conditions):
        failures.append("condition_set")
    if not all(counts.get(condition, 0) == int(spec["source_samples"]) for condition in expected_conditions):
        failures.append("condition_counts")
    if kind == "text":
        attacked = frame[frame.condition.ne("clean")]
        preserved = attacked.apply(
            lambda row: row.condition_tweet == f"{row.payload_text}\n\n{row.original_tweet}", axis=1
        )
        if not preserved.all():
            failures.append("original_tweet_preservation")
    else:
        attacked = frame[frame.condition.ne("clean")]
        if not attacked.condition_image_path.map(lambda value: resolve(value).is_file()).all():
            failures.append("generated_image_missing")
        if pd.to_numeric(attacked.occupied_area_ratio).max() > float(spec["max_occupied_area_ratio"]):
            failures.append("occupied_area_limit")
    return {
        "status": "passed" if not failures else "failed",
        "kind": kind,
        "source_samples": int(frame.sample_id.nunique()),
        "rows": len(frame),
        "conditions": expected_conditions,
        "condition_counts": {str(key): int(value) for key, value in counts.items()},
        "failures": failures,
    }


def prepare(config_path: str | Path, kind: str) -> dict:
    config = load_config(config_path)
    output = {}
    if kind in {"text", "both"}:
        frame = build_text_manifest(config)
        output["text"] = audit_manifest(frame, config, "text")
    if kind in {"size", "both"}:
        frame = build_size_manifest(config)
        output["size"] = audit_manifest(frame, config, "size")
    if any(value["status"] != "passed" for value in output.values()):
        raise RuntimeError(output)
    return output


def check(config_path: str | Path, kind: str) -> dict:
    config = load_config(config_path)
    output = {}
    selections = ("text", "size") if kind == "both" else (kind,)
    for selection in selections:
        key = "text_rhetoric" if selection == "text" else "size_response_pt"
        path = resolve(config[key]["manifest"])
        if not path.is_file():
            output[selection] = {"status": "failed", "failures": ["manifest_missing"]}
            continue
        output[selection] = audit_manifest(pd.read_csv(path, dtype=str).fillna(""), config, selection)
    if any(value["status"] != "passed" for value in output.values()):
        raise RuntimeError(output)
    return output


def _condition_pairs(config: dict, kind: str) -> dict[str, str]:
    if kind == "text":
        return dict(config["text_rhetoric"]["malicious_to_control"])
    return {
        f"{semantics}_pt{point:02d}": f"benign_pt{point:02d}"
        for semantics in ("direct", "misleading")
        for point in config["size_response_pt"]["nominal_points"]
    }


def _followup_metrics(frame: pd.DataFrame, config: dict, kind: str, model: str, model_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    transitions = []
    draws = int(config["shared"]["paired_bootstrap_draws"])
    seed = int(config["shared"]["paired_bootstrap_seed"])
    for malicious, control in _condition_pairs(config, kind).items():
        paired = _paired(frame, malicious)
        control_rows = frame[frame.condition.eq(control) & frame.parse_status.eq("parsed")][
            ["sample_id", "parsed_label"]
        ].rename(columns={"parsed_label": "control_prediction"})
        paired = paired.merge(control_rows, on="sample_id", validate="one_to_one")
        clean_correct = paired.clean_prediction.eq(paired.ground_truth)
        target = clean_correct & paired.ground_truth.isin(["mild_damage", "severe_damage"])
        upward_eligible = clean_correct & paired.ground_truth.isin(["little_or_no_damage", "mild_damage"])
        clean_level = paired.clean_prediction.map(LEVEL)
        attack_level = paired.attack_prediction.map(LEVEL)
        control_level = paired.control_prediction.map(LEVEL)
        downward = attack_level.lt(clean_level)
        control_downward = control_level.lt(clean_level)
        upward = attack_level.gt(clean_level)
        down = _rate(downward, target)
        full_down = _rate(downward & target, np.ones(len(paired), dtype=bool))
        up = _rate(upward, upward_eligible)
        full_up = _rate(upward & upward_eligible, np.ones(len(paired), dtype=bool))
        first = control_downward[target].astype(float).to_numpy()
        second = downward[target].astype(float).to_numpy()
        adjusted, low, high = paired_bootstrap_difference(first, second, draws, seed)
        full_first = (control_downward & target).astype(float).to_numpy()
        full_second = (downward & target).astype(float).to_numpy()
        full_adjusted, full_low, full_high = paired_bootstrap_difference(
            full_first, full_second, draws, seed
        )
        _, _, discordant, p_value = exact_mcnemar(first.astype(bool), second.astype(bool))
        point_match = re.search(r"_pt(\d+)$", malicious)
        metadata = frame[frame.condition.eq(malicious)]
        rows.append({
            "model": model, "model_id": model_id, "ablation": kind,
            "condition": malicious, "control_condition": control,
            "variant": malicious.split("_", 1)[1],
            "nominal_point_size": int(point_match.group(1)) if point_match else math.nan,
            "n_paired_parsed": len(paired),
            "downward_n": down[0], "eligible_n": down[1], "downward_rate": down[2],
            "downward_ci_low": down[3], "downward_ci_high": down[4],
            "full_cohort_downward_n": full_down[0],
            "full_cohort_n": full_down[1], "full_cohort_downward_rate": full_down[2],
            "upward_n": up[0], "upward_eligible_n": up[1], "upward_rate": up[2],
            "full_cohort_upward_n": full_up[0], "full_cohort_upward_rate": full_up[2],
            "control_downward_rate": float(first.mean()) if len(first) else math.nan,
            "malicious_minus_control_downward": adjusted,
            "adjusted_ci_low": low, "adjusted_ci_high": high,
            "full_cohort_control_downward_rate": float(full_first.mean()) if len(full_first) else math.nan,
            "full_cohort_malicious_minus_control": full_adjusted,
            "full_cohort_adjusted_ci_low": full_low,
            "full_cohort_adjusted_ci_high": full_high,
            "mcnemar_discordant_n": discordant, "mcnemar_p": p_value,
            "mean_signed_severity_shift_attack_minus_clean": float((attack_level - clean_level).mean()),
            "mean_target_eligible_severity_drop": float((clean_level - attack_level)[target].mean()),
            "mean_font_size_px": pd.to_numeric(metadata.get("font_size_px"), errors="coerce").mean(),
            "mean_relative_font_height": pd.to_numeric(metadata.get("relative_font_height"), errors="coerce").mean(),
            "mean_occupied_area_ratio": pd.to_numeric(metadata.get("occupied_area_ratio"), errors="coerce").mean(),
        })
        correct = paired[clean_correct]
        for clean_label in LABELS:
            source_mask = correct.clean_prediction.eq(clean_label)
            denominator = int(source_mask.sum())
            for attacked_label in LABELS:
                count = int((source_mask & correct.attack_prediction.eq(attacked_label)).sum())
                transitions.append({
                    "model": model, "model_id": model_id, "ablation": kind,
                    "condition": malicious, "clean_label": clean_label,
                    "attacked_label": attacked_label, "count": count,
                    "row_denominator": denominator,
                    "row_rate": count / denominator if denominator else math.nan,
                    "direction": (
                        "downward" if LEVEL[attacked_label] < LEVEL[clean_label]
                        else "upward" if LEVEL[attacked_label] > LEVEL[clean_label]
                        else "unchanged"
                    ),
                })
    metrics = pd.DataFrame(rows)
    if len(metrics):
        metrics["mcnemar_p_holm"] = holm_adjust(metrics.mcnemar_p)
    return metrics, pd.DataFrame(transitions)


def _pairwise(frame: pd.DataFrame, config: dict, kind: str, model: str, model_id: str) -> pd.DataFrame:
    if kind == "text":
        comparisons = [tuple(value) for value in config["text_rhetoric"]["predeclared_contrasts"]]
    else:
        points = [int(value) for value in config["size_response_pt"]["nominal_points"]]
        comparisons = [
            (f"{semantics}_pt{first:02d}", f"{semantics}_pt{second:02d}", "adjacent_point_size")
            for semantics in ("direct", "misleading")
            for first, second in zip(points, points[1:])
        ]
    clean = frame[frame.condition.eq("clean") & frame.parse_status.eq("parsed")][
        ["sample_id", "ground_truth", "parsed_label"]
    ].rename(columns={"parsed_label": "clean_prediction"})
    rows = []
    draws = int(config["shared"]["paired_bootstrap_draws"])
    seed = int(config["shared"]["paired_bootstrap_seed"])
    for first, second, contrast in comparisons:
        first_rows = frame[frame.condition.eq(first) & frame.parse_status.eq("parsed")][
            ["sample_id", "parsed_label"]
        ].rename(columns={"parsed_label": "first_prediction"})
        second_rows = frame[frame.condition.eq(second) & frame.parse_status.eq("parsed")][
            ["sample_id", "parsed_label"]
        ].rename(columns={"parsed_label": "second_prediction"})
        paired = clean.merge(first_rows, on="sample_id").merge(second_rows, on="sample_id")
        eligible = paired.clean_prediction.eq(paired.ground_truth) & paired.ground_truth.isin(
            ["mild_damage", "severe_damage"]
        )
        paired = paired[eligible]
        clean_level = paired.clean_prediction.map(LEVEL)
        a = paired.first_prediction.map(LEVEL).lt(clean_level).astype(float).to_numpy()
        b = paired.second_prediction.map(LEVEL).lt(clean_level).astype(float).to_numpy()
        effect, low, high = paired_bootstrap_difference(a, b, draws, seed)
        a_only, b_only, discordant, p_value = exact_mcnemar(a.astype(bool), b.astype(bool))
        rows.append({
            "model": model, "model_id": model_id, "ablation": kind,
            "condition_a": first, "condition_b": second, "contrast": contrast,
            "n_paired_eligible": len(paired), "rate_a": float(a.mean()) if len(a) else math.nan,
            "rate_b": float(b.mean()) if len(b) else math.nan,
            "risk_difference_b_minus_a": effect, "ci_low": low, "ci_high": high,
            "a_only": a_only, "b_only": b_only, "discordant_n": discordant,
            "mcnemar_p": p_value,
        })
    output = pd.DataFrame(rows)
    if len(output):
        output["mcnemar_p_holm"] = holm_adjust(output.mcnemar_p)
    return output


def _size_svg(metrics: pd.DataFrame, path: Path) -> None:
    width, height = 820, 500
    left, right, top, bottom = 75, 35, 55, 70
    plot_w, plot_h = width - left - right, height - top - bottom
    points = sorted(int(value) for value in metrics.nominal_point_size.dropna().unique())
    colors = {"direct": "#b52b36", "misleading": "#176b87"}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,sans-serif;fill:#20242b;letter-spacing:0}.axis{stroke:#67717e;stroke-width:1}.grid{stroke:#d7dce2;stroke-width:1}</style>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18">Point-size response: full-cohort downward rate</text>',
    ]
    for tick in range(0, 6):
        value = tick / 5
        y = top + (1 - value) * plot_h
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}"/>')
        parts.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" font-size="11">{value:.1f}</text>')
    for index, point in enumerate(points):
        x = left + index * plot_w / max(1, len(points) - 1)
        parts.append(f'<text x="{x:.1f}" y="{height-bottom+22}" text-anchor="middle" font-size="11">{point}</text>')
    parts += [
        f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}"/>',
        f'<line class="axis" x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}"/>',
        f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-size="12">Nominal point size (72 PPI)</text>',
        f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-size="12">Rate</text>',
    ]
    for series_index, semantics in enumerate(("direct", "misleading")):
        subset = metrics[metrics.condition.str.startswith(f"{semantics}_")].sort_values("nominal_point_size")
        coordinates = []
        for row in subset.itertuples():
            x = left + points.index(int(row.nominal_point_size)) * plot_w / max(1, len(points) - 1)
            y = top + (1 - float(row.full_cohort_downward_rate)) * plot_h
            coordinates.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{colors[semantics]}"/>')
        parts.append(f'<polyline points="{" ".join(coordinates)}" fill="none" stroke="{colors[semantics]}" stroke-width="3"/>')
        legend_y = top + 18 * series_index
        parts.append(f'<line x1="{width-170}" y1="{legend_y}" x2="{width-145}" y2="{legend_y}" stroke="{colors[semantics]}" stroke-width="3"/>')
        parts.append(f'<text x="{width-138}" y="{legend_y+4}" font-size="11">{html.escape(semantics)}</text>')
    parts.append("</svg>")
    path.write_text("".join(parts), encoding="utf-8")


def analyze(
    prediction_path: str | Path, manifest_path: str | Path, output_dir: str | Path,
    model_slug: str, kind: str, config_path: str | Path = DEFAULT_CONFIG,
) -> dict:
    config = load_config(config_path)
    frame, model_id = prepare_run(prediction_path, manifest_path)
    metrics, transitions = _followup_metrics(frame, config, kind, model_slug, model_id)
    contrasts = _pairwise(frame, config, kind, model_slug, model_id)
    output = resolve(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_csv(_clean_summary(frame, model_slug, model_id), output / "clean_metrics.csv")
    _write_csv(metrics, output / "followup_metrics.csv")
    _write_csv(transitions, output / "severity_shift_matrix.csv")
    _write_csv(contrasts, output / "pairwise_contrasts.csv")
    if kind == "size" and len(metrics):
        _size_svg(metrics, output / "size_response_full_cohort.svg")
    return {
        "model": model_slug, "model_id": model_id, "kind": kind,
        "conditions": len(metrics), "output_dir": str(output),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "check"):
        command = sub.add_parser(name)
        command.add_argument("--kind", choices=["text", "size", "both"], default="both")
    analysis = sub.add_parser("analyze")
    analysis.add_argument("--kind", choices=["text", "size"], required=True)
    analysis.add_argument("--predictions", required=True)
    analysis.add_argument("--manifest", required=True)
    analysis.add_argument("--output-dir", required=True)
    analysis.add_argument("--model-slug", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.config, args.kind)
    elif args.command == "check":
        result = check(args.config, args.kind)
    else:
        result = analyze(
            args.predictions, args.manifest, args.output_dir,
            args.model_slug, args.kind, args.config,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
