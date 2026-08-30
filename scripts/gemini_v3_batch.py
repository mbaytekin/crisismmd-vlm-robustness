#!/usr/bin/env python3
"""Prepare, submit, monitor, and download Gemini Batch V3 evaluations."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROMPT = ROOT / "configs/prompts/frozen_prompt_v4.yaml"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_SHARD_SIZE = 500
DEFAULT_MAX_OUTPUT_TOKENS = 512
DEFAULT_THINKING_BUDGET = 0
COMPLETED_STATES = {
    "JOB_STATE_SUCCEEDED",
    "JOB_STATE_FAILED",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_EXPIRED",
}
LABELS = ["little_or_no_damage", "mild_damage", "severe_damage"]


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip("\"'")
        if name and name not in os.environ:
            os.environ[name] = value


def resolve(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    return candidate if candidate.is_absolute() else ROOT / candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prompt_config(path: Path) -> tuple[dict, str]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    material = config["system_prompt"] + "\n" + config["user_prompt_template"]
    return config, hashlib.sha256(material.encode()).hexdigest()


def default_manifest(split: str) -> Path:
    if split in {"main", "pilot"}:
        return ROOT / "data/v3/manifests/all_conditions.csv"
    names = {
        "style_ablation": "style_ablation_conditions.csv",
        "size_ablation": "size_ablation_conditions.csv",
        "natural_clean_all": "natural_clean_all.csv",
        "official_test": "official_test_clean.csv",
        "prompt_validation": "prompt_validation_clean.csv",
        "text_rhetoric_ablation": "text_rhetoric_ablation_conditions.csv",
        "size_response_pt": "size_response_pt_conditions.csv",
    }
    try:
        return ROOT / "data/v3/manifests" / names[split]
    except KeyError as exc:
        raise SystemExit(f"No default manifest for split {split!r}; pass --manifest") from exc


def default_conditions(split: str) -> list[str]:
    if split in {"main", "pilot"}:
        return [
            "clean", "benign_image", "benign_text", "benign_joint",
            "direct_image", "direct_text", "direct_joint",
            "misleading_image", "misleading_text", "misleading_joint",
        ]
    if split == "style_ablation":
        return [
            "clean", "benign_simple", "benign_news", "benign_camouflage",
            "direct_simple", "direct_news", "direct_camouflage",
            "misleading_simple", "misleading_news", "misleading_camouflage",
        ]
    if split == "size_ablation":
        return [
            "clean", "benign_small", "benign_medium", "benign_large",
            "direct_small", "direct_medium", "direct_large",
            "misleading_small", "misleading_medium", "misleading_large",
        ]
    if split == "text_rhetoric_ablation":
        return [
            "clean",
            "benign_direct_label", "direct_label",
            "benign_direct_natural", "direct_natural",
            "benign_misleading_plain", "misleading_plain",
            "benign_misleading_authority", "misleading_authority",
        ]
    if split == "size_response_pt":
        return [
            "clean",
            *[
                f"{semantics}_pt{point:02d}"
                for semantics in ("benign", "direct", "misleading")
                for point in (3, 6, 9, 12, 15)
            ],
        ]
    return ["clean"]


def image_mime(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "image/webp"


def response_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "damage_severity": {"type": "string", "enum": LABELS},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "short_rationale": {"type": "string"},
        },
        "required": ["damage_severity", "confidence", "short_rationale"],
    }


def batch_request(
    system_prompt: str,
    user_prompt: str,
    image: Path,
    max_output_tokens: int,
    thinking_budget: int,
) -> dict:
    encoded = base64.b64encode(image.read_bytes()).decode("ascii")
    return {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": user_prompt},
                {"inlineData": {"mimeType": image_mime(image), "data": encoded}},
            ],
        }],
        # File-based Batch JSONL uses the GenerateContentRequest wire field
        # name here. The Python SDK uses `config` for inline requests, but the
        # uploaded JSONL parser expects `generation_config`.
        "generation_config": {
            "temperature": 0.0,
            "top_p": 1.0,
            "max_output_tokens": max_output_tokens,
            "thinking_config": {
                "thinking_budget": thinking_budget,
                "include_thoughts": False,
            },
            "response_mime_type": "application/json",
            "response_json_schema": response_schema(),
        },
        "systemInstruction": {"parts": [{"text": system_prompt}]},
    }


def parse_conditions(values: list[str] | None, split: str) -> list[str]:
    if not values:
        return default_conditions(split)
    output: list[str] = []
    for value in values:
        output.extend(part.strip() for part in value.split(",") if part.strip())
    return list(dict.fromkeys(output))


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def prepare(args: argparse.Namespace) -> None:
    prompt_path = resolve(args.prompt_config)
    manifest_path = resolve(args.manifest) if args.manifest else default_manifest(args.split)
    prompt, prompt_hash = prompt_config(prompt_path)
    conditions = parse_conditions(args.conditions, args.split)
    manifest = pd.read_csv(manifest_path, dtype=str).fillna("")
    rows = manifest[(manifest["split_name"] == args.split) & manifest.condition.isin(conditions)].copy()
    if rows.empty:
        raise SystemExit(f"No rows for split={args.split!r}, conditions={conditions}")
    missing_columns = {"sample_id", "condition", "condition_image_path", "condition_tweet"} - set(rows.columns)
    if missing_columns:
        raise SystemExit(f"Manifest lacks columns: {sorted(missing_columns)}")
    if args.max_output_tokens < 256:
        raise SystemExit("--max-output-tokens must be at least 256 for structured VLM output")
    if args.thinking_budget < -1:
        raise SystemExit("--thinking-budget must be -1 (dynamic) or non-negative")
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit("--limit must be positive")
        rows = rows.iloc[:args.limit].copy()

    output_dir = resolve(args.output_dir) if args.output_dir else ROOT / "results/v3/gemini_batch" / safe_slug(args.model) / args.split
    input_dir = output_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    for old in input_dir.glob("shard-*.jsonl"):
        old.unlink()
    for old in input_dir.glob("shard-*.metadata.jsonl"):
        old.unlink()

    shard_size = args.shard_size
    if shard_size <= 0:
        raise SystemExit("--shard-size must be positive")
    rows = rows.reset_index(drop=True)
    shard_records = []
    for shard_number, start in enumerate(range(0, len(rows), shard_size)):
        shard_rows = rows.iloc[start:start + shard_size]
        request_path = input_dir / f"shard-{shard_number:03d}.jsonl"
        metadata_path = input_dir / f"shard-{shard_number:03d}.metadata.jsonl"
        with request_path.open("w", encoding="utf-8") as request_file, metadata_path.open("w", encoding="utf-8") as metadata_file:
            for order, (_, row) in enumerate(shard_rows.iterrows(), start=start):
                image = resolve(row.condition_image_path)
                if not image.is_file():
                    raise SystemExit(f"Missing image: {image}")
                key = f"{args.split}:{int(order):06d}:{row.sample_id}:{row.condition}"
                user_prompt = prompt["user_prompt_template"].replace("<<TWEET>>", row.condition_tweet)
                request = {
                    "key": key,
                    "request": batch_request(
                        prompt["system_prompt"],
                        user_prompt,
                        image,
                        args.max_output_tokens,
                        args.thinking_budget,
                    ),
                }
                request_file.write(json.dumps(request, ensure_ascii=False) + "\n")
                metadata_file.write(json.dumps({
                    "key": key,
                    "order": int(order),
                    "sample_id": row.sample_id,
                    "condition": row.condition,
                    "split_name": args.split,
                    "image_path": str(image),
                    "prompt_hash": prompt_hash,
                }, ensure_ascii=False) + "\n")
        shard_records.append({
            "shard": shard_number,
            "requests": len(shard_rows),
            "request_path": str(request_path),
            "metadata_path": str(metadata_path),
            "bytes": request_path.stat().st_size,
        })

    spec = {
        "schema_version": 2,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "split": args.split,
        "conditions": conditions,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "manifest_sha256": sha256(manifest_path),
        "prompt_config": str(prompt_path.relative_to(ROOT)),
        "prompt_hash": prompt_hash,
        "shard_size": shard_size,
        "generation_config": {
            "temperature": 0.0,
            "top_p": 1.0,
            "max_output_tokens": args.max_output_tokens,
            "thinking_budget": args.thinking_budget,
            "response_mime_type": "application/json",
            "response_json_schema": response_schema(),
        },
        "limit": args.limit,
        "n_requests": len(rows),
        "shards": shard_records,
    }
    (output_dir / "batch_spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "n_requests": len(rows), "shards": len(shard_records), "bytes": sum(item["bytes"] for item in shard_records)}, indent=2))


def gemini_client(env_file: str | Path):
    load_env(resolve(env_file))
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is missing. Copy .env.example to .env and fill it locally.")
    try:
        from google import genai
    except ImportError as exc:
        raise SystemExit("Install Gemini dependencies: python -m pip install -r requirements-gemini.txt") from exc
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def read_spec(input_dir: Path) -> dict:
    spec_path = input_dir.parent / "batch_spec.json"
    if not spec_path.is_file():
        raise SystemExit(f"Missing batch spec: {spec_path}")
    return json.loads(spec_path.read_text(encoding="utf-8"))


def submit(args: argparse.Namespace) -> None:
    input_dir = resolve(args.input_dir)
    spec = read_spec(input_dir)
    jobs_path = input_dir.parent / "jobs.json"
    jobs = json.loads(jobs_path.read_text(encoding="utf-8")) if jobs_path.is_file() else {"schema_version": 1, "model": args.model or spec["model"], "jobs": []}
    existing = {item["shard"] for item in jobs["jobs"]}
    client = gemini_client(args.env_file)
    model = args.model or spec["model"]
    from google.genai import types
    for shard in spec["shards"]:
        if shard["shard"] in existing and not args.force:
            print(f"Resume: shard {shard['shard']} already submitted")
            continue
        path = Path(shard["request_path"])
        print(f"Uploading shard {shard['shard']} ({shard['requests']} requests, {shard['bytes']} bytes)", flush=True)
        uploaded = client.files.upload(
            file=str(path),
            config=types.UploadFileConfig(display_name=path.name, mime_type="jsonl"),
        )
        batch_job = client.batches.create(model=model, src=uploaded.name, config={"display_name": f"crisismmd-v3-{safe_slug(model)}-{spec['split']}-{shard['shard']:03d}"})
        jobs["jobs"] = [item for item in jobs["jobs"] if item["shard"] != shard["shard"]]
        jobs["jobs"].append({"shard": shard["shard"], "requests": shard["requests"], "input_file": uploaded.name, "job_name": batch_job.name})
        jobs_path.write_text(json.dumps(jobs, indent=2) + "\n", encoding="utf-8")
        print(f"Submitted shard {shard['shard']}: {batch_job.name}", flush=True)
    print(f"Jobs manifest: {jobs_path}")


def job_state(client, name: str):
    return client.batches.get(name=name)


def status(args: argparse.Namespace) -> None:
    input_dir = resolve(args.input_dir)
    jobs_path = input_dir.parent / "jobs.json"
    if not jobs_path.is_file():
        raise SystemExit(f"Missing jobs manifest: {jobs_path}")
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    client = gemini_client(args.env_file)
    counts = {}
    for item in sorted(jobs["jobs"], key=lambda value: value["shard"]):
        job = job_state(client, item["job_name"])
        state = getattr(job.state, "name", str(job.state))
        counts[state] = counts.get(state, 0) + 1
        print(f"shard={item['shard']:03d} state={state} job={item['job_name']}")
    print(json.dumps(counts, indent=2))


def response_text(result: dict) -> tuple[str, str]:
    if result.get("error"):
        return "", json.dumps(result["error"], ensure_ascii=False)
    response = result.get("response") or {}
    candidates = response.get("candidates") or []
    if not candidates:
        return "", "missing_candidates"
    parts = ((candidates[0].get("content") or {}).get("parts") or [])
    text = "".join(str(part.get("text", "")) for part in parts if part.get("text") is not None)
    return text, "" if text else "empty_response"


def download(args: argparse.Namespace) -> None:
    input_dir = resolve(args.input_dir)
    spec = read_spec(input_dir)
    jobs_path = input_dir.parent / "jobs.json"
    if not jobs_path.is_file():
        raise SystemExit(f"Missing jobs manifest: {jobs_path}")
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    client = gemini_client(args.env_file)
    metadata = {}
    for shard in spec["shards"]:
        path = Path(shard["metadata_path"])
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                item = json.loads(line)
                metadata[item["key"]] = item
    try:
        from src.inference.parsing import parse_response
    except ImportError as exc:
        raise SystemExit(f"Run from the repository root: {exc}") from exc
    records = []
    for item in jobs["jobs"]:
        job = job_state(client, item["job_name"])
        state = getattr(job.state, "name", str(job.state))
        if state != "JOB_STATE_SUCCEEDED":
            raise SystemExit(f"Shard {item['shard']} is not complete: {state}")
        if not job.dest or not job.dest.file_name:
            raise SystemExit(f"Shard {item['shard']} has no result file")
        raw_bytes = client.files.download(file=job.dest.file_name)
        for line in raw_bytes.decode("utf-8").splitlines():
            if not line.strip():
                continue
            result = json.loads(line)
            key = result.get("key") or (result.get("metadata") or {}).get("key")
            meta = metadata.get(key)
            if not meta:
                raise SystemExit(f"Result key not found in metadata: {key}")
            raw_text, error = response_text(result)
            parsed = parse_response(raw_text)
            if error and parsed["parse_status"] != "parsed":
                parsed["parse_status"] = "request_error"
            records.append({
                "run_id": f"gemini_{safe_slug(spec['model'])}_{spec['split']}",
                "sample_id": meta["sample_id"],
                "split_name": meta["split_name"],
                "condition": meta["condition"],
                "model_id": spec["model"],
                "backend": "gemini_batch_api",
                "prompt_hash": meta["prompt_hash"],
                "raw_response": raw_text,
                **parsed,
                "error": error,
                "cache_hit": False,
                "_order": meta["order"],
            })
    records.sort(key=lambda item: (item["_order"], item["condition"]))
    for item in records:
        item.pop("_order", None)
    output = resolve(args.output) if args.output else input_dir.parent / "predictions.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in records) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "records": len(records), "parsed": sum(item["parse_status"] == "parsed" for item in records)}, indent=2))


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--split", required=True)
    prep.add_argument("--conditions", nargs="+")
    prep.add_argument("--manifest")
    prep.add_argument("--prompt-config", default=str(DEFAULT_PROMPT))
    prep.add_argument("--model", default=os.environ.get("GEMINI_MODEL", DEFAULT_MODEL))
    prep.add_argument("--shard-size", type=int, default=int(os.environ.get("GEMINI_BATCH_SHARD_SIZE", DEFAULT_SHARD_SIZE)))
    prep.add_argument("--max-output-tokens", type=int, default=int(os.environ.get("GEMINI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS)))
    prep.add_argument("--thinking-budget", type=int, default=int(os.environ.get("GEMINI_THINKING_BUDGET", DEFAULT_THINKING_BUDGET)))
    prep.add_argument("--limit", type=int, help="Prepare only the first N records (smoke testing only)")
    prep.add_argument("--output-dir")
    prep.set_defaults(func=prepare)

    for name in ("submit", "status", "download"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--input-dir", required=True)
        cmd.add_argument("--env-file", default=".env")
        if name == "submit":
            cmd.add_argument("--model")
            cmd.add_argument("--force", action="store_true")
        if name == "download":
            cmd.add_argument("--output")
        cmd.set_defaults(func=globals()[name])
    return ap


if __name__ == "__main__":
    args = parser().parse_args()
    args.func(args)
