from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/gemini_v3_batch.py"
SPEC = importlib.util.spec_from_file_location("gemini_v3_batch", MODULE_PATH)
assert SPEC and SPEC.loader
gemini_v3_batch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gemini_v3_batch)


def test_batch_request_disables_thinking_and_enforces_json(tmp_path: Path) -> None:
    image = tmp_path / "sample.jpg"
    image.write_bytes(b"test-image")

    request = gemini_v3_batch.batch_request(
        "system",
        "user",
        image,
        max_output_tokens=512,
        thinking_budget=0,
    )

    config = request["generation_config"]
    assert config["max_output_tokens"] == 512
    assert config["thinking_config"] == {
        "thinking_budget": 0,
        "include_thoughts": False,
    }
    assert config["response_mime_type"] == "application/json"
    assert config["response_json_schema"]["required"] == [
        "damage_severity",
        "confidence",
        "short_rationale",
    ]
