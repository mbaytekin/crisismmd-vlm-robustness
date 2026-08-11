from src.model_registry import registry, validate


def test_v3_model_registry_contains_only_large_clean_screen_candidates():
    result=validate(); assert result["status"]=="passed"; assert result["candidate_count"]==8; assert result["primary_count"]==0
    models=registry()["models"]
    assert len(models)==8
    assert min(m["parameters_billion"] for m in models)>=12
    assert all(m["priority"]=="clean_screen_candidate" for m in models)
    assert sorted(m["parameters_billion"] for m in models if m.get("tier")=="ultra_large")==[235,397]
    assert all(m["precision"]=="4bit" for m in models if m.get("tier")=="ultra_large")
    assert len({m["slug"] for m in models})==len(models)
