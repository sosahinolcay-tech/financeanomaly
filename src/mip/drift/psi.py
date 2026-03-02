"""Population Stability Index utilities."""

from __future__ import annotations

from collections import deque
from typing import Iterable

import numpy as np


def population_stability_index(
    expected: Iterable[float],
    actual: Iterable[float],
    bins: int = 10,
    eps: float = 1e-6,
) -> float:
    """Compute PSI between baseline and current distributions."""
    exp = np.asarray(list(expected), dtype=float)
    act = np.asarray(list(actual), dtype=float)
    if exp.size == 0 or act.size == 0:
        return 0.0

    quantiles = np.linspace(0.0, 1.0, bins + 1)
    edges = np.unique(np.quantile(exp, quantiles))
    if edges.size < 2:
        return 0.0

    exp_hist, _ = np.histogram(exp, bins=edges)
    act_hist, _ = np.histogram(act, bins=edges)
    exp_pct = exp_hist / max(1, np.sum(exp_hist))
    act_pct = act_hist / max(1, np.sum(act_hist))

    exp_pct = np.clip(exp_pct, eps, None)
    act_pct = np.clip(act_pct, eps, None)
    return float(np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct)))


class PSIMonitor:
    """Online PSI monitor with rolling windows."""

    def __init__(self, reference_window: int = 500, current_window: int = 500, threshold: float = 0.2):
        self.reference_window = reference_window
        self.current_window = current_window
        self.threshold = threshold
        self._reference = deque(maxlen=reference_window)
        self._current = deque(maxlen=current_window)

    def seed_reference(self, values: Iterable[float]) -> None:
        for v in values:
            self._reference.append(float(v))

    def update(self, value: float) -> tuple[bool, float]:
        """Return (drift_detected, psi_value)."""
        if len(self._reference) < self.reference_window:
            self._reference.append(float(value))
            return False, 0.0

        self._current.append(float(value))
        if len(self._current) < self.current_window:
            return False, 0.0

        psi_val = population_stability_index(self._reference, self._current)
        detected = psi_val > self.threshold
        if detected:
            self._reference.clear()
            self._reference.extend(self._current)
            self._current.clear()
        return detected, psi_val
