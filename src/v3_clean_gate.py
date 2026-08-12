"""Predeclared clean-only qualification gates for V3 candidate models."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import ROOT, load_yaml


def evaluate(metrics: dict, phase: str, thresholds: dict) -> dict:
    clean=metrics.get("conditions",{}).get("clean")
    if not clean: raise ValueError("Run does not contain clean-condition metrics")
    total=int(metrics.get("n",0)); parsed=int(metrics.get("n_parsed",0)); parse_rate=parsed/total if total else 0.0
    recalls={label:float(values["recall"]) for label,values in clean["per_class"].items()}
    supports={label:int(values.get("support",0)) for label,values in clean["per_class"].items()}
    observed={"sample_count":total,"per_class_support":supports,"parse_rate":parse_rate,"accuracy":float(clean["accuracy"]),"macro_f1":float(clean["macro_f1"]),"every_class_recall":min(recalls.values()),"per_class_recall":recalls}
    checks={"parse_rate":observed["parse_rate"]>=thresholds["parse_rate_min"],"accuracy":observed["accuracy"]>=thresholds["accuracy_min"],"macro_f1":observed["macro_f1"]>=thresholds["macro_f1_min"],"every_class_recall":observed["every_class_recall"]>=thresholds["every_class_recall_min"]}
    if "n" in thresholds: checks["sample_count"]=observed["sample_count"]==int(thresholds["n"])
    if "per_class" in thresholds: checks["class_balance"]=bool(supports) and all(value==int(thresholds["per_class"]) for value in supports.values())
    return {"schema_version":1,"phase":phase,"run_id":metrics.get("run_id"),"model_id":metrics.get("model_id"),"qualified":all(checks.values()),"observed":observed,"thresholds":thresholds,"checks":checks}


def run(run_id: str, phase: str) -> dict:
    result_dir=ROOT/"results"/"v3"/run_id
    metrics=json.loads((result_dir/"metrics.json").read_text(encoding="utf-8"))
    thresholds=load_yaml("configs/v3/models.yaml")["clean_gates"][phase]
    gate=evaluate(metrics,phase,thresholds)
    (result_dir/"clean_gate.json").write_text(json.dumps(gate,indent=2)+"\n",encoding="utf-8")
    report_dir=ROOT/"reports"/"v3"/"clean_gates"; report_dir.mkdir(parents=True,exist_ok=True)
    (report_dir/f"{run_id}.json").write_text(json.dumps(gate,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(gate,indent=2)); return gate


def main() -> None:
    phases=tuple(load_yaml("configs/v3/models.yaml")["clean_gates"])
    parser=argparse.ArgumentParser(); parser.add_argument("--run-id",required=True); parser.add_argument("--phase",choices=phases,required=True); args=parser.parse_args()
    if not run(args.run_id,args.phase)["qualified"]: raise SystemExit(4)


if __name__=="__main__": main()
