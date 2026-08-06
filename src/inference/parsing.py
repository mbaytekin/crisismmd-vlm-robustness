from __future__ import annotations

import json
import re

LABELS = {"little_or_no_damage", "mild_damage", "severe_damage"}


def parse_response(raw: str) -> dict:
    raw = str(raw or "")
    candidates = [raw]
    candidates += re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.S)
    start, end = raw.find("{"), raw.rfind("}")
    if start >= 0 and end > start: candidates.append(raw[start:end + 1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
            label = data.get("damage_severity")
            if label not in LABELS: continue
            confidence = float(data.get("confidence", 0.0))
            if not 0 <= confidence <= 1: raise ValueError("confidence outside [0, 1]")
            return {"parsed_label": label, "confidence": confidence, "short_rationale": str(data.get("short_rationale", ""))[:1000], "parse_status": "parsed"}
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
    return {"parsed_label": "", "confidence": "", "short_rationale": "", "parse_status": "parse_error"}

