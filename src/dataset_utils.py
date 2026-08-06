from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd
from PIL import Image

LABELS = {"little_or_no_damage": 0, "mild_damage": 1, "severe_damage": 2}
LABEL_ALIASES = {
    "little or no damage": "little_or_no_damage",
    "little/no damage": "little_or_no_damage",
    "little_or_no_damage": "little_or_no_damage",
    "no damage": "little_or_no_damage",
    "mild damage": "mild_damage",
    "mild_damage": "mild_damage",
    "severe damage": "severe_damage",
    "severe_damage": "severe_damage",
}


def normalize_label(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    key = re.sub(r"\s+", " ", str(value).strip().lower().replace("’", "'")).strip()
    if key in {"don't know", "dont know", "can't judge", "cant judge", "unknown", "nan", "none", ""}:
        return None
    key = key.replace("-", " ")
    return LABEL_ALIASES.get(key)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def perceptual_hash(path: Path) -> str:
    """Small deterministic dHash; avoids a non-standard imagehash dependency."""
    with Image.open(path) as im:
        gray = im.convert("L").resize((9, 8))
        bits = []
        for y in range(8):
            for x in range(8):
                bits.append("1" if gray.getpixel((x, y)) > gray.getpixel((x + 1, y)) else "0")
    return f"{int(''.join(bits), 2):016x}"


def image_info(path: Path) -> dict:
    with Image.open(path) as im:
        return {"width": im.width, "height": im.height, "format": im.format or path.suffix.lstrip(".").upper()}


def canonical_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")


def find_column(columns, candidates) -> str | None:
    normalized = {canonical_column(c): c for c in columns}
    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]
    for norm, original in normalized.items():
        if any(candidate in norm for candidate in candidates):
            return original
    return None


def read_annotation(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".json", ".jsonl"}:
        try:
            data = json.loads(path.read_text(encoding="utf-8")) if suffix == ".json" else [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
            if isinstance(data, dict):
                for key in ("data", "annotations", "records", "examples"):
                    if isinstance(data.get(key), list):
                        data = data[key]
                        break
            return pd.json_normalize(data if isinstance(data, list) else [data])
        except Exception:
            return pd.DataFrame()
    for sep in ("\t", ",", None):
        try:
            df = pd.read_csv(path, sep=sep, engine="python", dtype=str, on_bad_lines="skip")
            if len(df.columns) > 1:
                return df
        except Exception:
            continue
    return pd.DataFrame()


def image_candidates(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}]

