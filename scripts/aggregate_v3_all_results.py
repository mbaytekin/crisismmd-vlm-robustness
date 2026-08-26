#!/usr/bin/env python3
"""Build paper-facing tables from completed V3 reports only.

This script performs no inference and does not download or modify model data.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/v3/all_results"

MODELS = [
    ("qwen35_27b_bf16", "Qwen3.5 27B", "BF16", "local MLX (main/ablation); GCP A100 (clean)",
     ROOT / "reports/v3/final_analysis/models/qwen35_27b_bf16",
     ROOT / "reports/v3/gcp_a100/models/qwen35_27b_bf16"),
    ("qwen36_27b_bf16", "Qwen3.6 27B", "BF16", "local MLX (main); GCP A100 (clean/ablation)",
     ROOT / "reports/v3/final_analysis/models/qwen36_27b_bf16",
     ROOT / "reports/v3/gcp_a100/models/qwen36_27b_bf16"),
    ("qwen3vl_32b_bf16", "Qwen3-VL 32B", "BF16", "GCP A100 / CUDA-vLLM",
     ROOT / "reports/v3/gcp_a100/models/qwen3vl_32b_bf16",
     ROOT / "reports/v3/gcp_a100/models/qwen3vl_32b_bf16"),
    ("mistral31_24b_bf16", "Mistral Small 3.1 24B", "BF16", "GCP A100 / CUDA-vLLM",
     ROOT / "reports/v3/gcp_a100/models/mistral31_24b_bf16",
     ROOT / "reports/v3/gcp_a100/models/mistral31_24b_bf16"),
    ("mistral31_24b_8bit", "Mistral Small 3.1 24B", "8-bit", "local MLX",
     ROOT / "reports/v3/final_analysis/models/mistral31_24b_8bit",
     ROOT / "reports/v3/final_analysis/models/mistral31_24b_8bit"),
    ("qwen3vl_32b_8bit", "Qwen3-VL 32B", "8-bit", "local MLX",
     ROOT / "reports/v3/final_analysis/models/qwen3vl_32b_8bit",
     ROOT / "reports/v3/final_analysis/models/qwen3vl_32b_8bit"),
    ("gemini_2_5_flash", "Gemini 2.5 Flash", "hosted", "Gemini Batch API",
     ROOT / "reports/v3/final_analysis/models/gemini_2_5_flash",
     ROOT / "reports/v3/final_analysis/models/gemini_2_5_flash"),
]

MAIN_CONDITIONS = ["direct_image", "direct_text", "direct_joint", "misleading_image", "misleading_text", "misleading_joint"]


def read_csv(path):
    return pd.read_csv(path) if path.is_file() else pd.DataFrame()


def pct(value):
    return "" if pd.isna(value) else f"{100 * float(value):.2f}%"


def md(df):
    if df.empty:
        return "_No completed result was found._"
    try:
        return df.to_markdown(index=False)
    except ImportError:
        columns = [str(c) for c in df.columns]
        lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        for values in df.fillna("").astype(str).itertuples(index=False, name=None):
            lines.append("| " + " | ".join(values) + " |")
        return "\n".join(lines)


def first_clean(path):
    df = read_csv(path / "clean_metrics.csv")
    if df.empty:
        return {}
    row = df.iloc[0]
    return {"n": row.get("n", ""), "parsed": row.get("n_parsed", ""),
            "accuracy": pct(row.get("accuracy")), "macro_f1": pct(row.get("macro_f1")),
            "mae": f"{float(row['mean_absolute_severity_error']):.4f}" if "mean_absolute_severity_error" in row else ""}


def main_rows():
    rows = []
    for slug, name, precision, backend, local, report_root in MODELS:
        path = local / "attack_metrics.csv"
        if not path.is_file():
            path = report_root / "main" / "attack_metrics.csv"
        df = read_csv(path)
        if df.empty:
            continue
        clean = first_clean(local)
        if not clean:
            clean = first_clean(report_root / "main")
        for condition in MAIN_CONDITIONS:
            row = df[df["condition"] == condition]
            if row.empty:
                continue
            r = row.iloc[0]
            rows.append({"model": name, "slug": slug, "precision": precision, "backend": backend,
                         "clean_n": clean.get("n", ""), "clean_accuracy": clean.get("accuracy", ""),
                         "condition": condition, "n": int(r["n_paired_parsed"]),
                         "accuracy": pct(r["accuracy_under_attack"]),
                         "downward_asr": pct(r["downward_asr"]),
                         "downward_n/den": f"{int(r['downward_asr_n'])}/{int(r['downward_asr_denominator'])}",
                         "induced_severe": pct(r["induced_severe_undertriage"]),
                         "induced_critical": pct(r["induced_critical_undertriage"])})
    return pd.DataFrame(rows)


def main_summary(df):
    if df.empty:
        return pd.DataFrame()
    value_columns = {
        "direct_image": "direct_image_asr", "direct_text": "direct_text_asr", "direct_joint": "direct_joint_asr",
        "misleading_image": "misleading_image_asr", "misleading_text": "misleading_text_asr",
        "misleading_joint": "misleading_joint_asr",
    }
    rows = []
    for keys, group in df.groupby(["model", "slug", "precision", "backend", "clean_accuracy"], sort=False, dropna=False):
        model, slug, precision, backend, clean_accuracy = keys
        row = {"model": model, "slug": slug, "precision": precision, "backend": backend,
               "main_clean_accuracy": clean_accuracy}
        for condition, column in value_columns.items():
            value = group.loc[group["condition"] == condition, "downward_asr"]
            row[column] = value.iloc[0] if len(value) else ""
        rows.append(row)
    return pd.DataFrame(rows)


def ablation_rows(kind):
    rows = []
    conditions = (["direct_simple", "direct_news", "direct_camouflage", "misleading_simple", "misleading_news", "misleading_camouflage"]
                  if kind == "style" else
                  ["direct_small", "direct_medium", "direct_large", "misleading_small", "misleading_medium", "misleading_large"])
    for slug, name, precision, backend, local, report_root in MODELS:
        path = local / "secondary" / kind / "ablation_metrics.csv"
        if not path.is_file():
            path = report_root / "secondary" / kind / "ablation_metrics.csv"
        df = read_csv(path)
        if df.empty:
            continue
        for condition in conditions:
            row = df[df["condition"] == condition]
            if row.empty:
                continue
            r = row.iloc[0]
            rows.append({"model": name, "slug": slug, "precision": precision, "backend": backend,
                         "condition": condition, "n": int(r["n_paired_parsed"]),
                         "downward_asr": pct(r["downward_asr"]),
                         "downward_n/den": f"{int(r['downward_asr_n'])}/{int(r['downward_asr_denominator'])}",
                         "malicious_minus_benign": pct(r.get("malicious_minus_benign_downward", float("nan"))),
                         "bootstrap_ci": (f"[{pct(r.get('paired_bootstrap_ci_low', float('nan')))}, "
                                          f"{pct(r.get('paired_bootstrap_ci_high', float('nan')))}]")})
    return pd.DataFrame(rows)


def clean_benchmark_rows():
    rows = []
    for slug, name, precision, backend, local, report_root in MODELS:
        candidates = [(report_root / "clean_benchmarks/natural/overall_metrics.csv", "natural_clean_3474"),
                      (report_root / "clean_benchmarks/official/overall_metrics.csv", "official_test_529")]
        if slug == "gemini_2_5_flash":
            candidates = [(ROOT / "reports/v3/clean_benchmarks/gemini_2_5_flash/natural_clean_all/overall_metrics.csv", "natural_clean_3474"),
                          (ROOT / "reports/v3/clean_benchmarks/gemini_2_5_flash/official_test/overall_metrics.csv", "official_test_529")]
        for path, cohort in candidates:
            df = read_csv(path)
            if df.empty:
                continue
            row = df.iloc[0]
            rows.append({"model": name, "slug": slug, "precision": precision, "backend": backend,
                         "cohort": cohort, "n": int(row["n"]), "parsed": int(row["n_parsed"]),
                         "accuracy": pct(row["accuracy"]), "macro_f1": pct(row["macro_f1_all_labels"]),
                         "mae": f"{float(row['mean_absolute_severity_error']):.4f}"})
    return pd.DataFrame(rows)


def inventory():
    rows = []
    roots = ["results/v3/gcp_a100", "results/v3/final_bf16", "results/v3/final_optional", "results/v3/final_ablation",
             "results/v3/gemini_batch/gemini-2.5-flash/thinking0-json-v2"]
    for rel in roots:
        path = ROOT / rel
        files = sorted(path.rglob("predictions.jsonl")) if path.is_dir() else []
        for file in files:
            with file.open(encoding="utf-8") as handle:
                count = sum(1 for line in handle if line.strip())
            rows.append({"result_group": rel, "records": count, "local_path": str(file)})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    main_df = main_rows()
    main_summary_df = main_summary(main_df)
    style_df = ablation_rows("style")
    size_df = ablation_rows("size")
    clean_df = clean_benchmark_rows()
    inventory_df = inventory()
    for filename, frame in [("main_attack_results.csv", main_df), ("style_ablation_results.csv", style_df),
                            ("size_ablation_results.csv", size_df), ("clean_benchmark_results.csv", clean_df),
                            ("main_summary.csv", main_summary_df),
                            ("prediction_inventory.csv", inventory_df)]:
        frame.to_csv(OUT / filename, index=False)

    model_df = pd.DataFrame([{"model": x[1], "slug": x[0], "precision": x[2], "backend": x[3]} for x in MODELS])
    report = ["# V3 All Results", "", "Generated from existing report CSVs and prediction files; no inference was run.", "",
              "## Model panel", "", md(model_df), "",
              "## Main V3 summary", "", "Clean is main-split accuracy; attack columns are downward ASR among clean-correct, target-eligible mild/severe cases.", "", md(main_summary_df), "",
              "## Main V3 attack matrix", "", "Primary attack outcome is downward ASR among clean-correct, target-eligible mild/severe cases. `n/den` is the exact numerator/denominator.", "", md(main_df), "",
              "## Style ablation", "", md(style_df), "",
              "## Size ablation", "", md(size_df), "",
              "## Clean benchmarks", "", "Natural clean uses 3,474 independent valid images; official test uses the dataset-provided 529-image test split.", "", md(clean_df), "",
              "## Local result locations", "",
              "All pulled GCP result files are under `results/v3/gcp_a100/`; the corresponding analysis reports are under `reports/v3/gcp_a100/`.", "",
              "Local MLX result roots: `results/v3/final_bf16/`, `results/v3/final_optional/`, and `results/v3/final_ablation/`.", "",
              "Gemini Batch prediction files are under `results/v3/gemini_batch/gemini-2.5-flash/thinking0-json-v2/`; Gemini reports are under `reports/v3/final_analysis/models/gemini_2_5_flash/` and `reports/v3/clean_benchmarks/gemini_2_5_flash/`.", "",
              "## Prediction inventory", "", md(inventory_df), "",
              "## Interpretation notes", "",
              "- BF16 GCP and local MLX rows are kept separate in the backend column; this is an environment annotation, not a claim that the backends are scientifically equivalent.",
              "- The 9B AWQ pilot is exploratory and is intentionally excluded from the canonical model table.",
              "- Missing rows mean that a completed prediction/report file was not present for that model/cohort; no missing experiment was silently substituted with another split.",
              "",
              "## Gemini follow-up candidates",
              "",
              "Gemini 2.5 Flash was retained as a completed baseline. Candidate follow-ups, subject to API availability, are `gemini-2.5-pro` (quality-first stable control), `gemini-3.5-flash` or `gemini-3.6-flash` (current stable multimodal models), and `gemini-3.5-flash-lite` (throughput/cost reference, not the primary quality replacement). Run the same frozen prompt and decoding settings first on the 180-example prompt-validation split, then decide whether to submit the full batch.",
              "Official model reference: https://ai.google.dev/gemini-api/docs/models",
              "Batch-limit reference: https://ai.google.dev/gemini-api/docs/rate-limits"]
    report_text = "\n".join(report) + "\n"
    (OUT / "README.md").write_text(report_text, encoding="utf-8")
    print(f"Wrote {OUT / 'README.md'}")
    print(f"Main rows: {len(main_df)}; style rows: {len(style_df)}; size rows: {len(size_df)}; clean rows: {len(clean_df)}")


if __name__ == "__main__":
    main()
