"""Validate and resolve immutable Hugging Face revisions for the V3 model panel."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

from src.config import ROOT, load_yaml


REGISTRY_PATH="configs/v3/models.yaml"


def registry() -> dict: return load_yaml(REGISTRY_PATH)


def validate() -> dict:
    cfg=registry(); models=cfg.get("models",[]); required={"slug","family","parameters_billion","official_model_id","mac_model_id","nvidia_model_id","precision","source"}; errors=[]; minimum=cfg.get("minimum_parameters_billion",0)
    slugs=[m.get("slug") for m in models]
    if len(slugs)!=len(set(slugs)): errors.append("duplicate model slug")
    for index,model in enumerate(models):
        missing=sorted(required-set(model))
        if missing: errors.append(f"models[{index}] missing {missing}")
        if model.get("parameters_billion",0)<=0: errors.append(f"{model.get('slug')} has invalid parameter count")
        if model.get("parameters_billion",0)<minimum: errors.append(f"{model.get('slug')} is below the {minimum}B candidate floor")
    result={"status":"passed" if not errors else "failed","model_count":len(models),"candidate_count":sum(m.get("priority")=="clean_screen_candidate" for m in models),"primary_count":sum(m.get("priority")=="primary" for m in models),"errors":errors}
    if errors: raise RuntimeError(result)
    return result


def resolve_lock(slug: str, platform: str) -> dict:
    validate(); models={m["slug"]:m for m in registry()["models"]}
    if slug not in models: raise KeyError(f"Unknown model slug: {slug}")
    model=models[slug]; field="mac_model_id" if platform=="mac" else "nvidia_model_id"; model_id=model[field]
    from huggingface_hub import model_info
    info=model_info(model_id)
    payload={"schema_version":1,"resolved_at":datetime.now(timezone.utc).isoformat(),"slug":slug,"platform":platform,"model_id":model_id,"huggingface_commit_sha":info.sha,"precision":model["precision"],"parameters_billion":model["parameters_billion"],"license_declared":model.get("license"),"gated":bool(model.get("gated",False)),"registry_path":REGISTRY_PATH}
    private=ROOT/".model-lock"/f"{slug}__{platform}.json"; public=ROOT/"reports"/"v3"/"model_locks"/f"{slug}__{platform}.json"; private.parent.mkdir(exist_ok=True); public.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(payload,indent=2)+"\n"; private.write_text(text,encoding="utf-8"); public.write_text(text,encoding="utf-8"); return payload


def main() -> None:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True); sub.add_parser("validate"); p=sub.add_parser("lock"); p.add_argument("--slug",required=True); p.add_argument("--platform",choices=["mac","nvidia"],required=True); args=ap.parse_args()
    print(json.dumps(validate() if args.cmd=="validate" else resolve_lock(args.slug,args.platform),indent=2))


if __name__=="__main__": main()
