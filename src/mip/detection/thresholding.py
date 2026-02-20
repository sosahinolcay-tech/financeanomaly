"""Threshold strategies - separate from models."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ThresholdStrategy(Protocol):
    """Protocol for threshold decisions. Only depends on score, not features."""

    def is_anomaly(self, score: float) -> bool:
        """Return True if score indicates anomaly."""
        ...


class StaticThreshold:
    """Static threshold. direction: 'below' = anomaly when score < threshold, 'above' = when score > threshold."""

    def __init__(self, threshold: float, direction: str = "below"):
        self.threshold = threshold
        self.direction = direction

    def is_anomaly(self, score: float) -> bool:
        if self.direction == "below":
            return score < self.threshold
        return score > self.threshold


class RollingQuantileThreshold:
    """Dynamic percentile-based threshold - placeholder."""

    def __init__(self, quantile: float = 0.99, window_size: int = 1000):
        self.quantile = quantile
        self.window_size = window_size
        self._scores: list[float] = []

    def is_anomaly(self, score: float) -> bool:
        self._scores.append(score)
        if len(self._scores) > self.window_size:
            self._scores.pop(0)
        if len(self._scores) < 10:
            return False
        thresh = sorted(self._scores)[int(len(self._scores) * self.quantile)]
        return score < thresh  # For IF-style (lower = anomaly)


class EWMAAdaptiveThreshold:
    """EWMA baseline - placeholder."""

    def __init__(self, alpha: float = 0.1, n_std: float = 3.0):
        self.alpha = alpha
        self.n_std = n_std
        self._mean: float | None = None
        self._var: float | None = None

    def is_anomaly(self, score: float) -> bool:
        if self._mean is None:
            self._mean = score
            self._var = 0.0
            return False
        self._mean = self.alpha * score + (1 - self.alpha) * self._mean
        self._var = self.alpha * (score - self._mean) ** 2 + (1 - self.alpha) * (self._var or 0)
        std = (self._var ** 0.5) or 1e-9
        return abs(score - self._mean) > self.n_std * std
