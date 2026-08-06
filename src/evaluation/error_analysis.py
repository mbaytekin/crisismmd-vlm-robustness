from __future__ import annotations

import argparse
import json
from pathlib import Path
import pandas as pd

from src.config import resolve


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--split", choices=["pilot", "test"], required=True); args = ap.parse_args()
    pred_path = resolve(f"results/{args.split}_predictions.jsonl")
    if not pred_path.exists(): raise FileNotFoundError(pred_path)
    rows = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    p = pd.DataFrame(rows)
    truth = pd.read_csv(resolve(f"data/splits/{args.split}.csv"), dtype=str)[["sample_id", "damage_label_normalized", "event_name"]].rename(columns={"damage_label_normalized": "ground_truth"})
    p = p.merge(truth, on="sample_id", how="left")
    clean = p[p.condition == "clean"][["sample_id", "parsed_label"]].rename(columns={"parsed_label": "clean_pred"})
    p = p.merge(clean, on="sample_id", how="left")
    attack_manifest = resolve(f"data/attacks/{args.split}_attack_manifest.csv")
    if attack_manifest.exists():
        texts = pd.read_csv(attack_manifest, dtype=str)[["sample_id", "condition", "text_content"]]
        p = p.merge(texts, on=["sample_id", "condition"], how="left")
    out = resolve("reports/error_analysis"); out.mkdir(parents=True, exist_ok=True)
    repeats = (p.condition != "clean") & p.text_content.fillna("").map(lambda x: bool(x)) & p.apply(lambda r: str(r.text_content).lower() in str(r.short_rationale).lower(), axis=1)
    groups = {"clean_correct_attack_wrong": (p.condition != "clean") & (p.clean_pred == p.ground_truth) & (p.parsed_label != p.ground_truth), "clean_wrong_attack_wrong": (p.condition != "clean") & (p.clean_pred != p.ground_truth) & (p.parsed_label != p.ground_truth), "severe_to_little_no_damage": (p.ground_truth == "severe_damage") & (p.parsed_label == "little_or_no_damage"), "benign_changed_clean": p.condition.str.startswith("benign") & (p.parsed_label != p.clean_pred), "attack_failed": p.condition.str.startswith(("direct", "indirect")) & (p.parsed_label == p.clean_pred), "parse_errors": p.parse_status != "parsed", "rationale_repeats_attack_text": repeats}
    for name, mask in groups.items(): p[mask].to_csv(out / f"{name}.csv", index=False)
    p[p.condition != "clean"].to_csv(out / "all_attack_cases.csv", index=False)
    print(f"wrote {len(groups)} error-analysis groups under {out}")


if __name__ == "__main__": main()
