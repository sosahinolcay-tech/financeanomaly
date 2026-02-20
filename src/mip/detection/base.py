"""Base detector interface - Protocol for dependency inversion."""

from typing import Dict, Protocol, runtime_checkable


@runtime_checkable
class Detector(Protocol):
    """Protocol for anomaly detectors. Depends only on domain (FeatureVector)."""

    def score(self, features: Dict[str, float]) -> float:
        """Compute anomaly score. Lower = more anomalous (IF) or higher (River)."""
        ...

    def fit(self, feature_list: list[Dict[str, float]]) -> None:
        """Train on historical data. No-op for online detectors."""
        ...
