from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import requests

from src.config import load_yaml, resolve
from .ollama_client import OllamaClient
from .vllm_client import VLLMClient


def autodetect(cfg: dict | None = None):
    cfg = cfg or load_yaml("configs/model.yaml")
    env_vllm = os.getenv("VLM_BASE_URL") or cfg.get("vlm_base_url")
    candidates = []
    if env_vllm:
        candidates.append(("vllm", env_vllm.rstrip("/")))
    candidates += [("vllm", "http://127.0.0.1:8000/v1"), ("vllm", "http://127.0.0.1:8000")]
    for _, base in candidates:
        for endpoint in (f"{base}/models", f"{base}/v1/models"):
            try:
                r = requests.get(endpoint, timeout=5)
                if r.ok:
                    data = r.json().get("data", [])
                    if data:
                        available_ids = [item.get("id") for item in data if item.get("id")]
                        expected_id = os.getenv("V3_EXPECTED_MODEL_ID")
                        model_id = expected_id if expected_id in available_ids else available_ids[0]
                        client_base = base if endpoint == f"{base}/models" else f"{base.rstrip('/')}/v1"
                        client = VLLMClient(client_base, model_id, int(cfg.get("openai_timeout_seconds", 90)))
                        return client, {**client.describe(), "discovery_endpoint": endpoint, "available_models": available_ids, "model_capabilities": "unknown_until_smoke_test"}
            except Exception:
                continue
    host = os.getenv("OLLAMA_HOST") or cfg.get("ollama_host") or "http://127.0.0.1:11434"
    try:
        r = requests.get(f"{host.rstrip('/')}/api/tags", timeout=5)
        r.raise_for_status()
        models = r.json().get("models", [])
        if models:
            model_id = models[0].get("name") or models[0].get("model")
            client = OllamaClient(host, model_id, int(cfg.get("ollama_timeout_seconds", 120)))
            return client, {**client.describe(), "discovery_endpoint": f"{host.rstrip('/')}/api/tags", "available_models": [m.get("name") or m.get("model") for m in models], "model_capabilities": "unknown_until_smoke_test"}
    except Exception as exc:
        return None, {"status": "not_found", "error": f"{type(exc).__name__}: {exc}"}
    return None, {"status": "not_found", "error": "No vLLM/OpenAI-compatible or Ollama model endpoint found"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-image", default="")
    args = ap.parse_args()
    client, info = autodetect()
    info["vision_smoke_test_result"] = {"status": "not_run"}
    if client and args.smoke_image:
        from src.inference.prompts import SYSTEM_PROMPT, user_prompt
        try:
            response = client.complete(resolve(args.smoke_image), SYSTEM_PROMPT, user_prompt("Smoke-test social post."), temperature=0, top_p=1, max_tokens=150, seed=42)
            nonempty = bool(response.raw_response.strip())
            info["vision_smoke_test_result"] = {"status": "passed" if response.http_status and response.http_status < 300 and nonempty else "failed", "http_status": response.http_status, "nonempty_final_response": nonempty, "raw_response": response.raw_response[:4000]}
            info["model_capabilities"] = "vision_payload_accepted" if info["vision_smoke_test_result"]["status"] == "passed" else "vision_unverified"
        except Exception as exc:
            info["vision_smoke_test_result"] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
    path = resolve("reports/model_server_info.json")
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(info, indent=2, ensure_ascii=False))
    if not client: raise SystemExit(1)


if __name__ == "__main__":
    main()
