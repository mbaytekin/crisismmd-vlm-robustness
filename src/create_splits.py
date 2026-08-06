from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import load_yaml, resolve, save_resolved_config


def stratified_take(df: pd.DataFrame, n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    parts = []
    grouped = list(df.groupby("event_name", sort=True))
    if not grouped:
        return df.iloc[0:0]
    quotas = {event: n // len(grouped) for event, _ in grouped}
    for event, group in sorted(grouped, key=lambda x: len(x[1]), reverse=True)[: n % len(grouped)]:
        quotas[event] += 1
    # Reallocate unmet quotas to events with available capacity.
    remaining = n
    chosen = []
    for event, group in grouped:
        take = min(quotas[event], len(group))
        idx = rng.permutation(len(group))[:take]
        chosen.append(group.iloc[idx])
        remaining -= take
    if remaining > 0:
        used = set(pd.concat(chosen)["sample_id"]) if chosen else set()
        extra = df[~df.sample_id.isin(used)].iloc[rng.permutation(len(df[~df.sample_id.isin(used)]))[:remaining]]
        chosen.append(extra)
    return pd.concat(chosen, ignore_index=True).head(n)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/dataset.yaml")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    snapshot = save_resolved_config("splits", {"dataset": cfg})
    manifest = pd.read_csv(resolve(cfg["processed_manifest_csv"]), dtype=str)
    classes = list(cfg["classes"])
    pilot_parts, test_parts = [], []
    for i, label in enumerate(classes):
        pool = manifest[manifest.damage_label_normalized == label].copy()
        pilot = stratified_take(pool, int(cfg["pilot_per_class"]), int(cfg["seed"]) + i)
        remaining = pool[~pool.sample_id.isin(pilot.sample_id)]
        test = stratified_take(remaining, int(cfg["test_per_class"]), int(cfg["seed"]) + 100 + i)
        if len(pilot) < int(cfg["pilot_per_class"]) or len(test) < int(cfg["test_per_class"]):
            raise RuntimeError(f"Not enough unique samples for {label}: pilot={len(pilot)} test={len(test)}")
        pilot_parts.append(pilot.assign(split="pilot"))
        test_parts.append(test.assign(split="test"))
    pilot, test = pd.concat(pilot_parts).sample(frac=1, random_state=cfg["seed"]).reset_index(drop=True), pd.concat(test_parts).sample(frac=1, random_state=cfg["seed"] + 1).reset_index(drop=True)
    overlap = set(pilot.sample_id) & set(test.sample_id)
    if overlap:
        raise AssertionError(f"pilot/test overlap: {len(overlap)}")
    out = resolve("data/splits")
    out.mkdir(parents=True, exist_ok=True)
    pilot.to_csv(out / "pilot.csv", index=False)
    test.to_csv(out / "test.csv", index=False)
    combined = pd.concat([pilot, test], ignore_index=True)
    distribution = combined.groupby(["split", "damage_label_normalized", "event_name"], dropna=False).size().reset_index(name="n")
    distribution.to_csv(out / "split_distribution.csv", index=False)
    event_counts = {f"{split_name}::{event}": int(n) for (split_name, event), n in combined.groupby(["split", "event_name"]).size().items()}
    summary = {"seed": cfg["seed"], "pilot_n": len(pilot), "test_n": len(test), "overlap_n": len(overlap), "pilot_class_counts": pilot.damage_label_normalized.value_counts().to_dict(), "test_class_counts": test.damage_label_normalized.value_counts().to_dict(), "event_counts": event_counts}
    (out / "split_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    display = {k: summary[k] for k in ("pilot_n", "test_n", "overlap_n")}
    display["config"] = str(snapshot)
    print(json.dumps(display, indent=2))


if __name__ == "__main__":
    main()
