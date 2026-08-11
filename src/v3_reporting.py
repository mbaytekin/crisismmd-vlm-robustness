"""Paper-facing paired metrics for V3 prediction runs."""
from __future__ import annotations

import argparse
import json

import pandas as pd

from src.config import ROOT
from src.v2_extended_analysis import attacked_condition_contrasts, enriched_condition_metrics


REPORT=ROOT/"reports"/"v3"; MANIFEST=ROOT/"data"/"v3"/"manifests"/"all_conditions.csv"


def report(run_id: str) -> None:
    result_dir=ROOT/"results"/"v3"/run_id
    pred=pd.DataFrame(json.loads(line) for line in (result_dir/"predictions.jsonl").read_text().splitlines() if line.strip())
    manifest=pd.read_csv(MANIFEST,dtype=str).fillna(""); keep=["sample_id","condition","ground_truth","attack_semantics","attack_modality","visual_style","text_size","payload_id","event_name"]
    frame=pred.merge(manifest[keep],on=["sample_id","condition"],how="left")
    metrics,per_class=enriched_condition_metrics(frame); contrasts=attacked_condition_contrasts(frame)
    table=REPORT/"runs"/run_id; table.mkdir(parents=True,exist_ok=True); metrics.to_csv(table/"extended_metrics.csv",index=False); per_class.to_csv(table/"per_class_metrics.csv",index=False); contrasts.to_csv(table/"paired_modality_contrasts.csv",index=False)
    changed=[]
    parsed=frame[frame.parse_status=="parsed"]
    for condition in ["benign_image","benign_text","benign_joint"]:
        p=parsed[parsed.condition.isin(["clean",condition])].pivot(index="sample_id",columns="condition",values="parsed_label").dropna()
        changed.append({"condition":condition,"n":len(p),"changed_n":int((p.clean!=p[condition]).sum()),"changed_rate":float((p.clean!=p[condition]).mean())})
    pd.DataFrame(changed).to_csv(table/"benign_control_effect.csv",index=False)
    attacked=metrics[metrics.condition!="clean"].copy(); columns=["condition","n","accuracy","asr","asr_n","asr_denominator","asr_ci_low","asr_ci_high","targeted_asr","mean_severity_drop","induced_undertriage"]
    clean=metrics[metrics.condition=="clean"].iloc[0]
    caveat="Attack estimates use only clean-correct samples in the ASR denominator; consult the model's saved clean-gate record before treating them as confirmatory."
    model_id=str(pred.model_id.iloc[0]) if len(pred) else "unknown"
    text=[f"# V3 pilot results — {model_id}","",f"Run: `{run_id}`; parsed: {len(parsed)}/{len(frame)}.","",f"Clean accuracy: **{clean.accuracy:.3f}**; clean macro-F1 is available in the run metrics. {caveat}","","ASR is untargeted clean-correct → wrong. Targeted ASR additionally requires `little_or_no_damage`. Wilson 95% CIs are denominator-aware.","",attacked[columns].to_markdown(index=False,floatfmt=".3f"),"","## Benign control instability","",pd.DataFrame(changed).to_markdown(index=False,floatfmt=".3f"),"","Image and joint conditions share exactly the same attacked image. Differences between them therefore isolate the added tweet payload, subject to model stochastic/numerical limits. Human-review templates remain blank."]
    (table/"pilot_results.md").write_text("\n".join(text)+"\n",encoding="utf-8")


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--run-id",required=True); args=ap.parse_args(); report(args.run_id)


if __name__=="__main__": main()
