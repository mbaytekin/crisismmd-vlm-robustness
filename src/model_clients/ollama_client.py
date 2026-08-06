from __future__ import annotations

import base64
from pathlib import Path
import requests

from .base import ModelResponse, VisionClient


class OllamaClient(VisionClient):
    backend = "ollama_native"

    def __init__(self, host: str, model_id: str, timeout: int = 120):
        self.host, self.model_id, self.timeout = host.rstrip("/"), model_id, timeout

    def describe(self):
        return {"backend": self.backend, "base_url": self.host, "server_reported_model_id": self.model_id, "model_tag": self.model_id, "request_format": "ollama_native_chat_vision"}

    def complete(self, image_path, system_prompt, user_prompt, **kwargs):
        payload = {"model": self.model_id, "stream": False, "think": False, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt, "images": [base64.b64encode(Path(image_path).read_bytes()).decode()]}], "options": {"temperature": kwargs.get("temperature", 0), "top_p": kwargs.get("top_p", 1), "num_predict": kwargs.get("max_tokens", 150)}}
        response = requests.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
        body = response.text
        if response.ok:
            try: body = response.json()["message"]["content"]
            except Exception: pass
        return ModelResponse(str(body), response.status_code, self.model_id, "ollama_native_chat_vision")
