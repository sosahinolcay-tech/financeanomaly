"""KS-statistic based feature distribution drift monitoring."""

from __future__ import annotations

from collections import deque
from typing import Iterable

import numpy as np


def ks_statistic(reference: Iterable[float], current: Iterable[float]) -> float:
    """Compute two-sample KS statistic without scipy."""
    ref = np.sort(np.asarray(list(reference), dtype=float))
    cur = np.sort(np.asarray(list(current), dtype=float))
    if ref.size == 0 or cur.size == 0:
        return 0.0

    grid = np.sort(np.concatenate([ref, cur]))
    cdf_ref = np.searchsorted(ref, grid, side="right") / ref.size
    cdf_cur = np.searchsorted(cur, grid, side="right") / cur.size
    return float(np.max(np.abs(cdf_ref - cdf_cur)))


class KSDriftMonitor:
    """Online monitor that compares reference/current windows with KS statistic."""

    def __init__(self, reference_window: int = 200, current_window: int = 200, threshold: float = 0.2):
        self.reference_window = reference_window
        self.current_window = current_window
        self.threshold = threshold
        self._reference = deque(maxlen=reference_window)
        self._current = deque(maxlen=current_window)

    def seed_reference(self, values: Iterable[float]) -> None:
        """Seed baseline distribution."""
        for v in values:
            self._reference.append(float(v))

    def update(self, value: float) -> tuple[bool, float]:
        """Push one observation and return (drift_detected, ks_stat)."""
        if len(self._reference) < self.reference_window:
            self._reference.append(float(value))
            return False, 0.0

        self._current.append(float(value))
        if len(self._current) < self.current_window:
            return False, 0.0

        stat = ks_statistic(self._reference, self._current)
        detected = stat > self.threshold
        if detected:
            # Refresh baseline to current after detected shift.
            self._reference.clear()
            self._reference.extend(self._current)
            self._current.clear()
        return detected, stat
