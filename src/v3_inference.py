"""Frozen-prompt V3 clean screening and inference."""
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


MANIFEST=ROOT/"data"/"v3"/"manifests"/"all_conditions.csv"; SCREEN_MANIFEST=ROOT/"data"/"v3"/"manifests"/"prompt_validation_clean.csv"; RESULT=ROOT/"results"/"v3"; REPORT=ROOT/"reports"/"v3"
DEFAULT_PROMPT_CONFIG="configs/prompts/frozen_prompt_v4.yaml"


def file_hash(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()


def runtime_identity() -> dict:
    revision=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True,check=False)
    packages={}
    for name in ("mlx-vlm","vllm","torch","transformers","pandas","pyarrow","Pillow","PyYAML","requests"):
        try: packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name]="not-installed"
    return {
        "git_commit":revision.stdout.strip() if revision.returncode==0 else "unavailable",
        "platform":platform.platform(),
        "machine":platform.machine(),
        "python":sys.version.split()[0],
        "packages":packages,
        "execution_environment":os.environ.get("V3_EXECUTION_ENVIRONMENT", "local_unspecified"),
        "accelerator":os.environ.get("V3_ACCELERATOR", "unspecified"),
    }


def prompt_cfg(prompt_config: str=DEFAULT_PROMPT_CONFIG) -> dict:
    path=resolve(prompt_config)
    cfg=yaml.safe_load(path.read_text(encoding="utf-8"))
    cfg["prompt_hash"]=hashlib.sha256((cfg["system_prompt"]+"\n"+cfg["user_prompt_template"]).encode()).hexdigest()
    cfg["prompt_config"]=str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)
    return cfg


def server() -> tuple:
    client,info=autodetect(load_yaml("configs/model.yaml"))
    if client is None: raise RuntimeError("No OpenAI-compatible local VLM endpoint detected")
    expected=os.environ.get("V3_EXPECTED_MODEL_ID")
    if expected and client.model_id!=expected: raise RuntimeError(f"Wrong model is served: expected {expected!r}, got {client.model_id!r}")
    return client,info


def smoke(prompt_config: str=DEFAULT_PROMPT_CONFIG,manifest: str | Path=SCREEN_MANIFEST,split: str="prompt_validation",report_path: str | Path | None=None) -> dict:
    manifest_path=resolve(manifest); m=pd.read_csv(manifest_path,dtype=str).fillna(""); clean=m[(m.split_name==split)&(m.condition=="clean")]
    if clean.empty: raise RuntimeError(f"No clean smoke-test row for split {split!r} in {manifest_path}")
    row=clean.iloc[0]; client,info=server(); p=prompt_cfg(prompt_config)
    started=time.perf_counter(); raw=client.complete(resolve(row.condition_image_path),p["system_prompt"],p["user_prompt_template"].replace("<<TWEET>>",row.condition_tweet),temperature=0.0,top_p=1.0,max_tokens=150,seed=42); parsed=parse_response(raw.raw_response)
    result={"status":"passed" if parsed["parse_status"]=="parsed" else "failed","timestamp":datetime.now(timezone.utc).isoformat(),"model_id":client.model_id,"backend":client.backend,"base_url":info.get("base_url"),"latency_seconds":time.perf_counter()-started,"sample_id":row.sample_id,"split":split,"parse_status":parsed["parse_status"],"parsed_label":parsed.get("parsed_label"),"prompt_config":p["prompt_config"],"prompt_hash":p["prompt_hash"]}
    report=resolve(report_path) if report_path else REPORT/"model_smoke_test.json"
    report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(result,indent=2),encoding="utf-8")
    if result["status"]!="passed": raise RuntimeError(result)
    return result


def inference(run_id: str,split: str,conditions: list[str],concurrency: int,prompt_config: str=DEFAULT_PROMPT_CONFIG,manifest: str | Path=MANIFEST,output_dir: str | Path | None=None,smoke_report_path: str | Path | None=None) -> Path:
    manifest_path=resolve(manifest); out_dir=resolve(output_dir) if output_dir else RESULT/run_id; smoke_path=resolve(smoke_report_path) if smoke_report_path else out_dir/"smoke_test.json"; smoke_result=smoke(prompt_config,manifest_path,split,smoke_path); m=pd.read_csv(manifest_path,dtype=str).fillna(""); rows=m[(m.split_name==split)&m.condition.isin(conditions)].copy()
    if not len(rows): raise RuntimeError("No manifest rows for requested split/conditions")
    client,info=server(); p=prompt_cfg(prompt_config); out_dir.mkdir(parents=True,exist_ok=True); cache=InferenceCache(out_dir/"inference_cache.sqlite")
    manifest_name=str(manifest_path.relative_to(ROOT) if manifest_path.is_relative_to(ROOT) else manifest_path)
    snapshot={"run_id":run_id,"manifest":manifest_name,"manifest_sha256":file_hash(manifest_path),"split":split,"conditions":conditions,"model_id":client.model_id,"backend":client.backend,"base_url":info.get("base_url"),"prompt_config":p["prompt_config"],"prompt_version":p.get("version"),"prompt_hash":p["prompt_hash"],"temperature":0.0,"top_p":1.0,"seed":42,"thinking_enabled":False,"concurrency":concurrency,"runtime":runtime_identity(),"smoke_test":smoke_result}
    (out_dir/"resolved_config.yaml").write_text(yaml.safe_dump(snapshot,sort_keys=False),encoding="utf-8")
    def one(row):
        image=resolve(row.condition_image_path); request={"sample_id":row.sample_id,"condition":row.condition,"model_id":client.model_id,"prompt_hash":p["prompt_hash"],"image_path":str(image),"tweet":row.condition_tweet,"temperature":0.0,"top_p":1.0,"seed":42}
        cached=cache.get(request)
        if cached and cached.get("parse_status")=="parsed": cached["cache_hit"]=True; return cached
        started=time.perf_counter(); error=""; raw_text=""; parsed={"parse_status":"request_error","parsed_label":"","confidence":"","short_rationale":""}
        for attempt in range(2):
            try:
                user=p["user_prompt_template"].replace("<<TWEET>>",row.condition_tweet)+("\nReturn JSON only." if attempt else "")
                response=client.complete(image,p["system_prompt"],user,temperature=0.0,top_p=1.0,max_tokens=150,seed=42); raw_text=response.raw_response; parsed=parse_response(raw_text)
                if parsed["parse_status"]=="parsed": break
            except Exception as exc: error=f"{type(exc).__name__}: {exc}"
        result={"run_id":run_id,"sample_id":row.sample_id,"split_name":split,"condition":row.condition,"model_id":client.model_id,"backend":client.backend,"prompt_hash":p["prompt_hash"],"request_timestamp":datetime.now(timezone.utc).isoformat(),"latency_seconds":time.perf_counter()-started,"raw_response":raw_text,**parsed,"error":error,"cache_hit":False}
        cache.put(request,result); return result
    output=[]; batch_started=time.perf_counter(); total=len(rows)
    print(f"Starting {run_id}: split={split} records={total} concurrency={concurrency}",flush=True)
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures=[pool.submit(one,row) for row in rows.itertuples()]
        for completed,future in enumerate(as_completed(futures),start=1):
            result=future.result(); output.append(result)
            elapsed=time.perf_counter()-batch_started; average=elapsed/completed; eta=average*(total-completed)
            parsed_count=sum(item.get("parse_status")=="parsed" for item in output); cache_hits=sum(bool(item.get("cache_hit")) for item in output)
            print(
                f"[{run_id}] {completed}/{total} ({completed*100/total:5.1f}%) "
                f"parsed={parsed_count} errors={completed-parsed_count} cache={cache_hits} "
                f"avg={average:.1f}s eta={eta/60:.1f}m",
                flush=True,
            )
    output.sort(key=lambda x:(x["sample_id"],conditions.index(x["condition"]))); path=out_dir/"predictions.jsonl"; path.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in output)+"\n",encoding="utf-8")
    parsed=pd.DataFrame(output); merged=parsed.merge(rows[["sample_id","condition","ground_truth"]],on=["sample_id","condition"]); valid=merged[merged.parse_status=="parsed"]
    metrics={"run_id":run_id,"model_id":client.model_id,"n":len(merged),"n_parsed":len(valid),"conditions":{}}
    for condition,q in valid.groupby("condition"): metrics["conditions"][condition]=classification_metrics(q.ground_truth,q.parsed_label)
    (out_dir/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8"); print(json.dumps({"output":str(path),**metrics},indent=2)); return path


def main() -> None:
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    smoke_parser=sub.add_parser("smoke"); smoke_parser.add_argument("--prompt-config",default=DEFAULT_PROMPT_CONFIG); smoke_parser.add_argument("--manifest",default=str(SCREEN_MANIFEST)); smoke_parser.add_argument("--split",default="prompt_validation"); smoke_parser.add_argument("--report-path",default="")
    p=sub.add_parser("run"); p.add_argument("--run-id",required=True); p.add_argument("--split",default="prompt_validation"); p.add_argument("--conditions",nargs="+",default=["clean"]); p.add_argument("--concurrency",type=int,default=1); p.add_argument("--prompt-config",default=DEFAULT_PROMPT_CONFIG); p.add_argument("--manifest",default=str(SCREEN_MANIFEST)); p.add_argument("--output-dir",default=""); p.add_argument("--smoke-report-path",default=""); args=ap.parse_args()
    if args.cmd=="smoke": print(json.dumps(smoke(args.prompt_config,args.manifest,args.split,args.report_path or None),indent=2))
    else: inference(args.run_id,args.split,args.conditions,args.concurrency,args.prompt_config,args.manifest,args.output_dir or None,args.smoke_report_path or None)


if __name__=="__main__": main()
