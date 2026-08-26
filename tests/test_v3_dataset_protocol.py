import pandas as pd

from src.v3_dataset_protocol import _largest_remainder


def test_largest_remainder_event_quotas_are_proportional_and_exact():
    counts = pd.Series({"event_a": 101, "event_b": 67, "event_c": 9, "event_d": 1})

    quotas = _largest_remainder(counts, 120)

    assert sum(quotas.values()) == 120
    assert set(quotas) == set(counts.index)
    assert quotas["event_a"] > quotas["event_b"] > quotas["event_c"] >= quotas["event_d"]
