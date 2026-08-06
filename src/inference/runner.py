from __future__ import annotations

import argparse
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.config import load_yaml, resolve, save_resolved_config
from src.inference.cache import InferenceCache
from src.inference.parsing import parse_response
from src.inference.prompts import SYSTEM_PROMPT, retry_prompt, user_prompt
from src.model_clients.autodetect import autodetect


def load_prompt_config(path: str | None) -> dict:
    if not path:
        return {"version": "crisis_damage_v1", "system_prompt": SYSTEM_PROMPT, "user_prompt_template": "__legacy__", "sha256": hashlib.sha256((SYSTEM_PROMPT + "\nlegacy").encode()).hexdigest()}
    import yaml
    cfg = load_yaml(path)
    cfg["sha256"] = hashlib.sha256((cfg["system_prompt"] + "\n" + cfg["user_prompt_template"]).encode()).hexdigest()
    return cfg


def make_prompt(prompt_cfg: dict, tweet_text: str, retry: bool = False) -> tuple[str, str]:
    if prompt_cfg["user_prompt_template"] == "__legacy__":
        prompt = user_prompt(tweet_text)
    else:
        prompt = prompt_cfg["user_prompt_template"].replace("<<TWEET>>", tweet_text)
    if retry:
        prompt += "\nReturn JSON only, with no Markdown fences or additional text."
    return prompt_cfg["system_prompt"], prompt


def run_one(client, row, condition, attack_lookup, infer_cfg, cache, prompt_cfg):
    if condition == "clean": image_path = resolve(row.image_path)
    else:
        image_path = resolve(attack_lookup[(row.sample_id, condition)].attacked_image_path)
    request = {"sample_id": row.sample_id, "condition": condition, "model_id": client.model_id, "prompt_version": prompt_cfg["version"], "prompt_sha256": prompt_cfg["sha256"], "image_path": str(image_path), "tweet_text": row.tweet_text, "temperature": infer_cfg["temperature"], "top_p": infer_cfg["top_p"], "max_tokens": infer_cfg["max_tokens"]}
    cached = cache.get(request)
    if cached:
        cached["cache_hit"] = True
        return cached
    started = time.perf_counter(); attempts = 0; last = None
    while attempts <= int(infer_cfg["max_retries"]):
        try:
            system_prompt, prompt = make_prompt(prompt_cfg, row.tweet_text, retry=attempts > 0)
            response = client.complete(image_path, system_prompt, prompt, temperature=infer_cfg["temperature"], top_p=infer_cfg["top_p"], max_tokens=infer_cfg["max_tokens"], seed=infer_cfg["seed"])
            parsed = parse_response(response.raw_response)
            result = {"sample_id": row.sample_id, "condition": condition, "model_id": response.model_id, "backend": client.backend, "prompt_version": prompt_cfg["version"], "prompt_sha256": prompt_cfg["sha256"], "request_timestamp": datetime.now(timezone.utc).isoformat(), "latency_seconds": time.perf_counter() - started, "http_status": response.http_status, "raw_response": response.raw_response, **parsed, "retry_count": attempts, "error": "" if parsed["parse_status"] == "parsed" else "parse_error", "cache_hit": False}
            if parsed["parse_status"] == "parsed" or attempts >= int(infer_cfg["max_retries"]):
                cache.put(request, result); return result
        except Exception as exc:
            last = f"{type(exc).__name__}: {exc}"
        attempts += 1
    result = {"sample_id": row.sample_id, "condition": condition, "model_id": client.model_id, "backend": client.backend, "prompt_version": prompt_cfg["version"], "prompt_sha256": prompt_cfg["sha256"], "request_timestamp": datetime.now(timezone.utc).isoformat(), "latency_seconds": time.perf_counter() - started, "http_status": None, "raw_response": "", "parsed_label": "", "confidence": "", "short_rationale": "", "parse_status": "request_error", "retry_count": attempts, "error": last or "unknown"}
    cache.put(request, result); return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["pilot", "test"], required=True)
    ap.add_argument("--conditions", nargs="*", default=None)
    ap.add_argument("--allow-unverified-vision", action="store_true")
    ap.add_argument("--config", default="configs/inference.yaml")
    ap.add_argument("--prompt-config", default="")
    ap.add_argument("--output", default="")
    ap.add_argument("--cache", default="")
    ap.add_argument("--attack-manifest", default="")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    prompt_cfg = load_prompt_config(args.prompt_config or None)
    snapshot = save_resolved_config(f"inference_{args.split}", {"inference": cfg, "model": load_yaml("configs/model.yaml")})
    client, info = autodetect(load_yaml("configs/model.yaml"))
    if not client: raise RuntimeError("No local vision model server detected; text-only fallback is disabled.")
    smoke = resolve("reports/model_server_info.json")
    if not args.allow_unverified_vision and smoke.exists():
        state = json.loads(smoke.read_text()).get("vision_smoke_test_result", {}).get("status")
        if state != "passed": raise RuntimeError(f"Vision smoke test is not passed ({state}); inference refused.")
    elif not args.allow_unverified_vision and not smoke.exists():
        raise RuntimeError("Run 05_detect_model_server.sh with a smoke image before inference.")
    split = pd.read_csv(resolve(f"data/splits/{args.split}.csv"), dtype=str)
    conditions = args.conditions or ["clean", "benign_simple", "benign_realistic", "direct_simple", "direct_realistic", "indirect_simple", "indirect_realistic"]
    attack_path = resolve(args.attack_manifest) if args.attack_manifest else resolve(f"data/attacks/{args.split}_attack_manifest.csv")
    attack = pd.read_csv(attack_path, dtype=str) if any(c != "clean" for c in conditions) else pd.DataFrame()
    lookup = {(r.sample_id, r.condition): r for r in attack.itertuples()} if not attack.empty else {}
    cache = InferenceCache(resolve(args.cache) if args.cache else resolve(f"results/{args.split}_inference_cache.sqlite"))
    futures, results = [], []
    with ThreadPoolExecutor(max_workers=max(1, int(cfg["concurrency"]))) as pool:
        for row in split.itertuples():
            for condition in conditions: futures.append(pool.submit(run_one, client, row, condition, lookup, cfg, cache, prompt_cfg))
        for future in as_completed(futures): results.append(future.result())
    results.sort(key=lambda r: (r["sample_id"], conditions.index(r["condition"])))
    out = resolve(args.output) if args.output else resolve(f"results/{args.split}_predictions.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for row in results: f.write(json.dumps(row, ensure_ascii=False) + "\n")
    pd.DataFrame([r for r in results if r["parse_status"] != "parsed"]).to_csv(resolve("results/inference_failures.csv"), index=False)
    print(f"wrote {out} records={len(results)} config={snapshot}")


if __name__ == "__main__":
    main()
