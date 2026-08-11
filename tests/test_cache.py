from src.inference.cache import InferenceCache
from concurrent.futures import ThreadPoolExecutor


def test_cache_roundtrip(tmp_path):
    cache = InferenceCache(tmp_path / "cache.sqlite")
    request = {"sample_id": "x", "condition": "clean", "prompt_version": "v1"}
    assert cache.get(request) is None
    cache.put(request, {"parse_status": "parsed", "parsed_label": "mild_damage"})
    assert cache.get(request)["parsed_label"] == "mild_damage"


def test_cache_is_thread_safe(tmp_path):
    cache = InferenceCache(tmp_path / "concurrent.sqlite")
    def write(i):
        request = {"sample_id": str(i), "condition": "clean"}
        cache.put(request, {"value": i})
        return cache.get(request)["value"]
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(write, range(100))) == list(range(100))
