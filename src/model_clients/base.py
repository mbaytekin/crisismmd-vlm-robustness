from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ModelResponse:
    raw_response: str
    http_status: int | None
    model_id: str
    request_format: str


class VisionClient:
    backend = "unknown"

    def describe(self) -> dict[str, Any]:
        raise NotImplementedError

    def complete(self, image_path, system_prompt: str, user_prompt: str, **kwargs) -> ModelResponse:
        raise NotImplementedError

