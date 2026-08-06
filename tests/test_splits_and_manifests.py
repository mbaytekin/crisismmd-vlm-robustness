import pandas as pd


def test_pilot_test_do_not_overlap_if_outputs_exist():
    pilot, test = "data/splits/pilot.csv", "data/splits/test.csv"
    try:
        a, b = pd.read_csv(pilot, dtype=str), pd.read_csv(test, dtype=str)
    except FileNotFoundError:
        return
    assert set(a.sample_id).isdisjoint(set(b.sample_id))


def test_attack_manifest_integrity_if_outputs_exist():
    for path in ["data/attacks/pilot_attack_manifest.csv", "data/attacks/test_attack_manifest.csv"]:
        try: df = pd.read_csv(path, dtype=str)
        except FileNotFoundError: continue
        assert df.sample_id.notna().all()
        assert not df.duplicated(["sample_id", "condition"]).any()

