from src.inference.cache import InferenceCache


def test_cache_roundtrip(tmp_path):
    cache = InferenceCache(tmp_path / "cache.sqlite")
    request = {"sample_id": "x", "condition": "clean", "prompt_version": "v1"}
    assert cache.get(request) is None
    cache.put(request, {"parse_status": "parsed", "parsed_label": "mild_damage"})
    assert cache.get(request)["parsed_label"] == "mild_damage"

