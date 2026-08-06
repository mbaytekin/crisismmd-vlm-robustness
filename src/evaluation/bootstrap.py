from __future__ import annotations

import numpy as np


def bootstrap_ci(values, statistic=np.mean, n_boot=2000, seed=42):
    values = np.asarray(list(values), dtype=float)
    values = values[np.isfinite(values)]
    if not len(values): return {"estimate": None, "lower": None, "upper": None, "n": 0}
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, len(values), size=(n_boot, len(values)))
    estimates = np.array([statistic(values[idx]) for idx in samples])
    return {"estimate": float(statistic(values)), "lower": float(np.quantile(estimates, .025)), "upper": float(np.quantile(estimates, .975)), "n": int(len(values))}

