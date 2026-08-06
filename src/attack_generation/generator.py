from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image

from src.config import load_yaml, resolve, save_resolved_config
from src.attack_generation.simple_overlay import draw_simple
from src.attack_generation.realistic_overlay import draw_realistic


def stable_index(sample_id: str, condition: str, n: int, seed: int) -> int:
    digest = hashlib.sha256(f"{seed}:{sample_id}:{condition}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % n


def assign_text(row, condition, texts, position):
    family = "direct" if condition.startswith("direct") else "indirect" if condition.startswith("indirect") else "benign"
    values = texts[family]
    return values[position % len(values)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["pilot", "test"], required=True)
    ap.add_argument("--config", default="configs/attacks.yaml")
    ap.add_argument("--texts", default="configs/attack_texts.yaml")
    ap.add_argument("--output-root", default="", help="Optional output directory for regenerated attack images")
    ap.add_argument("--manifest", default="", help="Optional manifest path")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    cfg, texts = load_yaml(args.config), load_yaml(args.texts)
    snapshot = save_resolved_config(f"attack_{args.split}", {"attacks": cfg, "attack_texts": texts})
    split = pd.read_csv(resolve(f"data/splits/{args.split}.csv"), dtype=str)
    conditions = args.only or cfg["conditions"]
    root = resolve(args.output_root) if args.output_root else resolve(f"data/attacks/{args.split}")
    rows = []
    for label, group in split.groupby("damage_label_normalized", sort=True):
        group = group.sort_values("sample_id").reset_index(drop=True)
        for condition in conditions:
            realistic = condition.endswith("realistic")
            family = "direct" if condition.startswith("direct") else "indirect" if condition.startswith("indirect") else "benign"
            for i, row in group.iterrows():
                if family == "benign":
                    template_text = texts["benign_templates"][i % len(texts["benign_templates"])]
                    event_name = str(row.get("event_name", "CrisisMMD")).replace("safe", "archive", 1).replace("damage", "scene", 1)
                    text = template_text.format(event_name=event_name[:48])
                else:
                    text = assign_text(row, condition, texts, i)
                if realistic:
                    templates = cfg["placement_templates"]["realistic"]
                    template = templates[stable_index(row.sample_id, condition, len(templates), cfg["seed"])]
                    placement_type = "realistic"
                else:
                    template = cfg["placement_templates"]["simple"][stable_index(row.sample_id, condition, 2, cfg["seed"])]
                    placement_type = "simple"
                original = resolve(row.image_path)
                try:
                    image = Image.open(original).convert("RGB")
                    if realistic:
                        result, meta = draw_realistic(image, text, cfg["font_size_ratio"], cfg["min_font_size_px"], cfg["padding_ratio"], cfg["default_opacity"], template, cfg["max_occupied_area_ratio"])
                    else:
                        result, meta = draw_simple(image, text, cfg["font_size_ratio"], cfg["min_font_size_px"], cfg["padding_ratio"], cfg["default_opacity"], template, cfg["max_occupied_area_ratio"])
                    out = root / condition / f"{row.sample_id}.png"
                    out.parent.mkdir(parents=True, exist_ok=True)
                    result.save(out, format="PNG", compress_level=int(cfg["png_compress_level"]))
                    status, error = "success", ""
                except Exception as exc:
                    out = root / condition / f"{row.sample_id}.png"
                    status, error, meta = "error", f"{type(exc).__name__}: {exc}", {"text_bbox": [], "font_size_px": 0, "relative_text_height": 0, "occupied_area_ratio": 0, "opacity": cfg["default_opacity"], "text_line_count": 0, "text_truncated": False}
                rows.append({"sample_id": row.sample_id, "condition": condition, "original_image_path": row.image_path, "attacked_image_path": str(out.relative_to(resolve("."))), "attack_family": family, "placement_type": placement_type, "placement_template": template, "text_content": text, "text_bbox": json.dumps(meta["text_bbox"]), "font_size_px": meta["font_size_px"], "relative_text_height": meta["relative_text_height"], "occupied_area_ratio": meta["occupied_area_ratio"], "opacity": meta["opacity"], "text_line_count": meta.get("text_line_count", 0), "text_truncated": meta.get("text_truncated", False), "generation_seed": cfg["seed"], "generation_status": status, "generation_error": error})
    manifest = pd.DataFrame(rows)
    path = resolve(args.manifest) if args.manifest else resolve(f"data/attacks/{args.split}_attack_manifest.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest.to_csv(path, index=False)
    print(f"generated={len(manifest)} errors={(manifest.generation_status != 'success').sum()} config={snapshot}")


if __name__ == "__main__":
    main()
