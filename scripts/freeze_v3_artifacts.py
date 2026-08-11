#!/usr/bin/env python3
"""Create or verify a content-addressed lock for V3 research inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "v3" / "artifact_lock.json"
INPUTS = [
    "configs/prompts/frozen_prompt.yaml",
    "configs/v3/attack_payloads.yaml",
    "configs/v3/models.yaml",
    "configs/v3/pipeline.yaml",
    "data/v3/splits/pilot.csv",
    "data/v3/splits/main.csv",
    "data/v3/splits/style_ablation.csv",
    "data/v3/splits/size_ablation.csv",
    "data/v3/manifests/all_conditions.csv",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def current_files() -> list[dict[str, object]]:
    missing = [item for item in INPUTS if not (ROOT / item).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing V3 lock inputs: {missing}")
    return [
        {"path": item, "bytes": (ROOT / item).stat().st_size, "sha256": sha256(ROOT / item)}
        for item in INPUTS
    ]


def freeze() -> None:
    payload = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "files": current_files(),
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "written", "output": str(OUTPUT), "file_count": len(INPUTS)}))


def check() -> None:
    if not OUTPUT.is_file():
        raise FileNotFoundError(f"Artifact lock not found: {OUTPUT}")
    expected = json.loads(OUTPUT.read_text(encoding="utf-8"))
    expected_by_path = {item["path"]: item for item in expected["files"]}
    current = current_files()
    mismatches = [
        item["path"]
        for item in current
        if expected_by_path.get(item["path"], {}).get("sha256") != item["sha256"]
    ]
    extras = sorted(set(expected_by_path) - {item["path"] for item in current})
    if mismatches or extras:
        raise RuntimeError({"changed_or_missing": mismatches, "unexpected_lock_entries": extras})
    print(json.dumps({"status": "passed", "file_count": len(current)}))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("freeze", "check"))
    args = parser.parse_args()
    freeze() if args.command == "freeze" else check()


if __name__ == "__main__":
    main()
