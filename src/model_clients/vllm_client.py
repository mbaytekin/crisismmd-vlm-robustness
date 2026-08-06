from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
import requests

from .base import ModelResponse, VisionClient


class VLLMClient(VisionClient):
    backend = "vllm_openai_compatible"

    def __init__(self, base_url: str, model_id: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.timeout = timeout

    def describe(self):
        return {"backend": self.backend, "base_url": self.base_url, "server_reported_model_id": self.model_id, "request_format": "openai_chat_completions_vision"}

    def complete(self, image_path, system_prompt, user_prompt, **kwargs):
        mime = mimetypes.guess_type(str(image_path))[0] or "image/png"
        encoded = base64.b64encode(Path(image_path).read_bytes()).decode()
        payload = {"model": self.model_id, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": [{"type": "text", "text": user_prompt}, {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}]}], "temperature": kwargs.get("temperature", 0), "top_p": kwargs.get("top_p", 1), "max_tokens": kwargs.get("max_tokens", 150)}
        if kwargs.get("seed") is not None: payload["seed"] = kwargs["seed"]
        if self.model_id.startswith(("qwen3.5", "glm-4.6v")):
            payload["chat_template_kwargs"] = {"enable_thinking": False}
        response = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=self.timeout)
        body = response.text
        if response.ok:
            try: body = response.json()["choices"][0]["message"]["content"]
            except Exception: pass
        return ModelResponse(str(body), response.status_code, self.model_id, "openai_chat_completions_vision")
