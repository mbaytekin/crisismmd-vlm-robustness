from __future__ import annotations

from pathlib import Path
import os
import subprocess
import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str | Path) -> dict:
    with open(ROOT / path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def resolve(path: str | Path) -> Path:
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def run_id(prefix: str = "run") -> str:
    commit = "nogit"
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        pass
    return f"{prefix}_{commit}_{os.getpid()}"


def save_resolved_config(run_name: str, configs: dict[str, dict]) -> Path:
    rid = run_id(run_name)
    target = ROOT / "results" / rid / "resolved_config.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"run_id": rid, "git_commit": "nogit"}
    try:
        payload["git_commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        pass
    payload.update(configs)
    target.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return target
