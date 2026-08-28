from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.model_clients.vllm_client import VLLMClient


@pytest.mark.parametrize("release", ("Qwen3.5", "Qwen3.6", "Qwen3.8"))
def test_qwen_release_disables_thinking(tmp_path: Path, release: str):
    image = tmp_path / "image.png"
    image.write_bytes(b"not-a-real-image")
    response = Mock(ok=True, status_code=200, text="ok")
    response.json.return_value = {"choices": [{"message": {"content": "{}"}}]}

    with patch("src.model_clients.vllm_client.requests.post", return_value=response) as post:
        VLLMClient("http://localhost:8000/v1", f"Qwen/{release}-27B").complete(
            image, "system", "user", temperature=0, top_p=1, max_tokens=150
        )

    assert post.call_args.kwargs["json"]["chat_template_kwargs"] == {
        "enable_thinking": False
    }
