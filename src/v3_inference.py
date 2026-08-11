"""Frozen-prompt V3 pilot inference and clean-baseline gate."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from src.config import ROOT, load_yaml, resolve
from src.evaluation.metrics import classification_metrics
from src.inference.cache import InferenceCache
from src.inference.parsing import parse_response
from src.model_clients.autodetect import autodetect


MANIFEST=ROOT/"data"/"v3"/"manifests"/"all_conditions.csv"; RESULT=ROOT/"results"/"v3"; REPORT=ROOT/"reports"/"v3"


def file_hash(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()


def runtime_identity() -> dict:
    revision=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=False)
    packages={}
    for name in ("mlx-vlm","pandas","pyarrow","Pillow","PyYAML","requests"):
        try: packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name]="not-installed"
    return {"git_commit":revision.stdout.strip() if revision.returncode==0 else "unavailable","platform":platform.platform(),"machine":platform.machine(),"python":sys.version.split()[0],"packages":packages}


def prompt_cfg() -> dict:
    cfg=yaml.safe_load((ROOT/"configs"/"prompts"/"frozen_prompt.yaml").read_text(encoding="utf-8"))
    cfg["prompt_hash"]=hashlib.sha256((cfg["system_prompt"]+"\n"+cfg["user_prompt_template"]).encode()).hexdigest(); return cfg


def server() -> tuple:
    client,info=autodetect(load_yaml("configs/model.yaml"))
    if client is None: raise RuntimeError("No OpenAI-compatible local VLM endpoint detected")
    expected=os.environ.get("V3_EXPECTED_MODEL_ID")
    if expected and client.model_id!=expected: raise RuntimeError(f"Wrong model is served: expected {expected!r}, got {client.model_id!r}")
    return client,info


def smoke() -> dict:
    m=pd.read_csv(MANIFEST,dtype=str).fillna(""); row=m[(m.split_name=="pilot")&(m.condition=="clean")].iloc[0]; client,info=server(); p=prompt_cfg()
    started=time.perf_counter(); raw=client.complete(resolve(row.condition_image_path),p["system_prompt"],p["user_prompt_template"].replace("<<TWEET>>",row.condition_tweet),temperature=0.0,top_p=1.0,max_tokens=150,seed=42); parsed=parse_response(raw.raw_response)
    result={"status":"passed" if parsed["parse_status"]=="parsed" else "failed","timestamp":datetime.now(timezone.utc).isoformat(),"model_id":client.model_id,"backend":client.backend,"base_url":info.get("base_url"),"latency_seconds":time.perf_counter()-started,"sample_id":row.sample_id,"parse_status":parsed["parse_status"],"parsed_label":parsed.get("parsed_label"),"prompt_hash":p["prompt_hash"]}
    (REPORT/"model_smoke_test.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    if result["status"]!="passed": raise RuntimeError(result)
    return result


def inference(run_id: str,split: str,conditions: list[str],concurrency: int) -> Path:
    smoke_result=smoke(); m=pd.read_csv(MANIFEST,dtype=str).fillna(""); rows=m[(m.split_name==split)&m.condition.isin(conditions)].copy()
    if not len(rows): raise RuntimeError("No manifest rows for requested split/conditions")
    client,info=server(); p=prompt_cfg(); out_dir=RESULT/run_id; out_dir.mkdir(parents=True,exist_ok=True); cache=InferenceCache(out_dir/"inference_cache.sqlite")
    snapshot={"run_id":run_id,"manifest":"data/v3/manifests/all_conditions.csv","manifest_sha256":file_hash(MANIFEST),"split":split,"conditions":conditions,"model_id":client.model_id,"backend":client.backend,"base_url":info.get("base_url"),"prompt_hash":p["prompt_hash"],"temperature":0.0,"top_p":1.0,"seed":42,"thinking_enabled":False,"concurrency":concurrency,"runtime":runtime_identity(),"smoke_test":smoke_result}
    (out_dir/"resolved_config.yaml").write_text(yaml.safe_dump(snapshot,sort_keys=False),encoding="utf-8")
    def one(row):
        image=resolve(row.condition_image_path); request={"sample_id":row.sample_id,"condition":row.condition,"model_id":client.model_id,"prompt_hash":p["prompt_hash"],"image_path":str(image),"tweet":row.condition_tweet,"temperature":0.0,"top_p":1.0,"seed":42}
        cached=cache.get(request)
        if cached: cached["cache_hit"]=True; return cached
        started=time.perf_counter(); error=""; raw_text=""; parsed={"parse_status":"request_error","parsed_label":"","confidence":"","short_rationale":""}
        for attempt in range(2):
            try:
                user=p["user_prompt_template"].replace("<<TWEET>>",row.condition_tweet)+("\nReturn JSON only." if attempt else "")
                response=client.complete(image,p["system_prompt"],user,temperature=0.0,top_p=1.0,max_tokens=150,seed=42); raw_text=response.raw_response; parsed=parse_response(raw_text)
                if parsed["parse_status"]=="parsed": break
            except Exception as exc: error=f"{type(exc).__name__}: {exc}"
        result={"run_id":run_id,"sample_id":row.sample_id,"split_name":split,"condition":row.condition,"model_id":client.model_id,"backend":client.backend,"prompt_hash":p["prompt_hash"],"request_timestamp":datetime.now(timezone.utc).isoformat(),"latency_seconds":time.perf_counter()-started,"raw_response":raw_text,**parsed,"error":error,"cache_hit":False}
        cache.put(request,result); return result
    output=[]
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures=[pool.submit(one,row) for row in rows.itertuples()]
        for future in as_completed(futures): output.append(future.result())
    output.sort(key=lambda x:(x["sample_id"],conditions.index(x["condition"]))); path=out_dir/"predictions.jsonl"; path.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in output)+"\n",encoding="utf-8")
    parsed=pd.DataFrame(output); merged=parsed.merge(rows[["sample_id","condition","ground_truth"]],on=["sample_id","condition"]); valid=merged[merged.parse_status=="parsed"]
    metrics={"run_id":run_id,"model_id":client.model_id,"n":len(merged),"n_parsed":len(valid),"conditions":{}}
    for condition,q in valid.groupby("condition"): metrics["conditions"][condition]=classification_metrics(q.ground_truth,q.parsed_label)
    (out_dir/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8"); print(json.dumps({"output":str(path),**metrics},indent=2)); return path


def main() -> None:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True); sub.add_parser("smoke"); p=sub.add_parser("run"); p.add_argument("--run-id",required=True); p.add_argument("--split",default="pilot"); p.add_argument("--conditions",nargs="+",default=["clean"]); p.add_argument("--concurrency",type=int,default=1); args=ap.parse_args()
    if args.cmd=="smoke": print(json.dumps(smoke(),indent=2))
    else: inference(args.run_id,args.split,args.conditions,args.concurrency)


if __name__=="__main__": main()
