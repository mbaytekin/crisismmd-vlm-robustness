from src.model_clients.autodetect import autodetect


class Response:
    ok = True

    def json(self):
        return {
            "data": [
                {"id": "mlx-community/Mistral-Small-3.1-24B-Instruct-2503-8bit"},
                {"id": "mlx-community/Qwen3.5-27B-8bit"},
            ]
        }


def test_autodetect_selects_expected_model(monkeypatch):
    monkeypatch.setenv("VLM_BASE_URL", "http://127.0.0.1:8080/v1")
    monkeypatch.setenv("V3_EXPECTED_MODEL_ID", "mlx-community/Qwen3.5-27B-8bit")
    monkeypatch.setattr("src.model_clients.autodetect.requests.get", lambda *_args, **_kwargs: Response())

    client, info = autodetect({"openai_timeout_seconds": 90})

    assert client.model_id == "mlx-community/Qwen3.5-27B-8bit"
    assert client.model_id in info["available_models"]
