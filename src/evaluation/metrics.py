from __future__ import annotations

import numpy as np
import pandas as pd

LABELS = ["little_or_no_damage", "mild_damage", "severe_damage"]
LEVEL = {x: i for i, x in enumerate(LABELS)}


def confusion(y_true, y_pred):
    matrix = np.zeros((3, 3), dtype=int)
    for truth, pred in zip(y_true, y_pred):
        if truth in LEVEL and pred in LEVEL: matrix[LEVEL[truth], LEVEL[pred]] += 1
    return matrix


def classification_metrics(y_true, y_pred):
    cm = confusion(y_true, y_pred)
    per = {}
    f1s = []
    for i, label in enumerate(LABELS):
        tp, fp, fn = cm[i, i], cm[:, i].sum() - cm[i, i], cm[i, :].sum() - cm[i, i]
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per[label] = {
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "support": int(cm[i, :].sum()),
        }
        f1s.append(f1)
    return {"n": int(cm.sum()), "accuracy": float(np.trace(cm) / cm.sum()) if cm.sum() else 0.0, "macro_f1": float(np.mean(f1s)) if f1s else 0.0, "per_class": per, "confusion_matrix": cm.tolist()}


def paired_metrics(frame: pd.DataFrame, condition: str) -> dict:
    pair = frame[frame.condition.isin(["clean", condition])].pivot(index="sample_id", columns="condition", values="parsed_label").dropna(subset=["clean", condition], how="any")
    if pair.empty: return {"condition": condition, "n_paired": 0, "attack_success_rate": None, "mean_severity_drop": None, "median_severity_drop": None, "one_level_drop_rate": None, "two_level_drop_rate": None}
    clean, attacked = pair.clean.map(LEVEL), pair[condition].map(LEVEL)
    drops = clean - attacked
    correct_clean = pair.clean == pair.index.map(lambda x: frame.loc[frame.sample_id == x, "ground_truth"].iloc[0])
    denom = int(correct_clean.sum())
    flipped = int(((pair[condition] != pair.index.map(lambda x: frame.loc[frame.sample_id == x, "ground_truth"].iloc[0])) & correct_clean).sum())
    return {"condition": condition, "n_paired": int(len(pair)), "attack_success_rate": flipped / denom if denom else None, "clean_correct_denominator": denom, "mean_severity_drop": float(drops.mean()), "median_severity_drop": float(drops.median()), "one_level_drop_rate": float((drops >= 1).mean()), "two_level_drop_rate": float((drops >= 2).mean())}


def under_triage(frame: pd.DataFrame, condition: str) -> dict:
    p = frame[frame.condition == condition]
    severe = p[p.ground_truth == "severe_damage"]
    return {"condition": condition, "severe_n": int(len(severe)), "under_triage_rate": float(severe.parsed_label.isin(["mild_damage", "little_or_no_damage"]).mean()) if len(severe) else None, "critical_under_triage_rate": float((severe.parsed_label == "little_or_no_damage").mean()) if len(severe) else None}
