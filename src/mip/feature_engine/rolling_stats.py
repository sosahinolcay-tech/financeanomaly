"""Rolling statistics utilities."""

import numpy as np
from typing import List


def compute_rolling_stats(values: np.ndarray, window: int) -> dict:
    """Compute rolling mean, std, etc."""
    if len(values) < window:
        return {}
    return {
        "rolling_mean": float(np.mean(values[-window:])),
        "rolling_std": float(np.std(values[-window:])),
    }
