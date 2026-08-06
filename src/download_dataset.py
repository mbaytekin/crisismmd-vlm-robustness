from __future__ import annotations

import argparse
import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

import requests

from src.config import resolve, load_yaml


def download(url: str, destination: Path) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"exists: {destination}")
    else:
        partial = destination.with_suffix(destination.suffix + ".part")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(partial, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
        partial.replace(destination)
    h = hashlib.sha256()
    with open(destination, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def safe_extract(archive: Path, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                target = (root / member.filename).resolve()
                if not str(target).startswith(str(root.resolve())):
                    raise RuntimeError(f"unsafe archive member: {member.filename}")
            z.extractall(root)
    else:
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                target = (root / member.name).resolve()
                if not str(target).startswith(str(root.resolve())):
                    raise RuntimeError(f"unsafe archive member: {member.name}")
            t.extractall(root)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/dataset.yaml")
    ap.add_argument("--no-extract", action="store_true")
    args = ap.parse_args()
    cfg = load_yaml(args.config)
    raw = resolve(cfg["raw_dir"])
    raw.mkdir(parents=True, exist_ok=True)
    files = [
        (cfg["official_archive_url"], raw / "CrisisMMD_v2.0.tar.gz"),
        (cfg["official_split_url"], raw / "crisismmd_datasplit_all.zip"),
    ]
    lines = []
    official_failed = False
    for url, path in files:
        try:
            digest = download(url, path)
            lines.append(f"{digest}  {path.name}")
            if not args.no_extract:
                out = raw / path.stem.replace(".tar", "")
                if not out.exists() or not any(out.iterdir()):
                    safe_extract(path, out)
        except Exception as exc:
            lines.append(f"ERROR  {path.name}  {type(exc).__name__}: {exc}")
            print(lines[-1])
            official_failed = True
    if official_failed:
        try:
            from huggingface_hub import snapshot_download
            hf_dir = snapshot_download(cfg["fallback_huggingface_dataset"], local_dir=str(raw / "huggingface_QCRI_CrisisMMD"), local_dir_use_symlinks=False)
            lines.append(f"FALLBACK_HUGGINGFACE  {hf_dir}")
        except Exception as exc:
            lines.append(f"ERROR  huggingface_fallback  {type(exc).__name__}: {exc}")
    (raw / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {raw / 'checksums.sha256'}")


if __name__ == "__main__":
    main()
