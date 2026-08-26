import json

import numpy as np

from src.evaluation.metrics import classification_metrics
from src.v3_clean_gate import evaluate


def metrics(accuracy=0.75, macro_f1=0.70, recalls=(0.6,0.7,0.8), parsed=90):
    labels=("little_or_no_damage","mild_damage","severe_damage")
    return {"run_id":"test","model_id":"model","n":90,"n_parsed":parsed,"conditions":{"clean":{"accuracy":accuracy,"macro_f1":macro_f1,"per_class":{label:{"recall":recall} for label,recall in zip(labels,recalls)}}}}


THRESHOLDS={"parse_rate_min":0.995,"accuracy_min":0.70,"macro_f1_min":0.65,"every_class_recall_min":0.50}


def test_clean_gate_passes_only_when_every_threshold_passes():
    result=evaluate(metrics(),"main",THRESHOLDS)
    assert result["qualified"] is True
    assert all(result["checks"].values())


def test_clean_gate_rejects_class_collapse_despite_high_accuracy():
    result=evaluate(metrics(accuracy=0.85,recalls=(0.2,0.9,0.9)),"main",THRESHOLDS)
    assert result["qualified"] is False
    assert result["checks"]["accuracy"] is True
    assert result["checks"]["every_class_recall"] is False


def test_clean_gate_rejects_parse_failures():
    result=evaluate(metrics(parsed=89),"main",THRESHOLDS)
    assert result["qualified"] is False
    assert result["checks"]["parse_rate"] is False


def test_prompt_validation_gate_requires_180_balanced_samples():
    candidate=metrics(accuracy=0.64,macro_f1=0.63,recalls=(0.67,0.43,0.82),parsed=180)
    candidate["n"]=180
    candidate["conditions"]["clean"]["per_class"]={
        label:{**values,"support":60}
        for label,values in candidate["conditions"]["clean"]["per_class"].items()
    }
    thresholds={**THRESHOLDS,"accuracy_min":0.60,"macro_f1_min":0.55,"every_class_recall_min":0.40,"n":180,"per_class":60}
    result=evaluate(candidate,"prompt_validation",thresholds)
    assert result["qualified"] is True
    assert result["checks"]["sample_count"] is True
    assert result["checks"]["class_balance"] is True

    candidate["n"]=90
    rejected=evaluate(candidate,"prompt_validation",thresholds)
    assert rejected["qualified"] is False
    assert rejected["checks"]["sample_count"] is False


def test_classification_metrics_are_json_serializable():
    result = classification_metrics(
        np.array(["little_or_no_damage", "mild_damage", "severe_damage"]),
        np.array(["little_or_no_damage", "severe_damage", "severe_damage"]),
    )

    assert json.dumps(result)
    for values in result["per_class"].values():
        assert type(values["precision"]) is float
        assert type(values["recall"]) is float
        assert type(values["f1"]) is float
