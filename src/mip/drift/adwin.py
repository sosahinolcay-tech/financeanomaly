"""ADWIN-style drift monitoring with optional River backend."""

from __future__ import annotations

from collections import deque
import numpy as np

try:
    from river import drift as river_drift
except Exception:  # pragma: no cover - optional dependency
    river_drift = None


class ADWINMonitor:
    """Detect concept drift in a score stream."""

    def __init__(self, delta: float = 0.002, fallback_window: int = 100, z_threshold: float = 3.0):
        self.delta = delta
        self.fallback_window = fallback_window
        self.z_threshold = z_threshold
        self._drift_events = 0

        if river_drift is not None:
            self._detector = river_drift.ADWIN(delta=delta)
        else:
            self._detector = None
            self._values = deque(maxlen=fallback_window * 2)

    @property
    def drift_events(self) -> int:
        return self._drift_events

    def update(self, value: float) -> bool:
        """Return True when a drift event is detected."""
        if self._detector is not None:
            self._detector.update(value)
            detected = bool(getattr(self._detector, "drift_detected", False))
            if detected:
                self._drift_events += 1
            return detected

        # Statistical fallback if River is unavailable.
        self._values.append(float(value))
        if len(self._values) < self._values.maxlen:
            return False

        vals = np.asarray(self._values, dtype=float)
        mid = vals.size // 2
        old = vals[:mid]
        new = vals[mid:]
        old_mean = float(np.mean(old))
        new_mean = float(np.mean(new))
        old_std = float(np.std(old)) + 1e-9
        z = abs(new_mean - old_mean) / old_std
        detected = z > self.z_threshold
        if detected:
            self._drift_events += 1
        return detected
