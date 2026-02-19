"""Base detector interface."""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseDetector(ABC):
    """Abstract base class for anomaly detectors."""

    @abstractmethod
    def score(self, features: Dict[str, float]) -> float:
        """Compute anomaly score."""
        pass

    @abstractmethod
    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        """Determine if features represent an anomaly."""
        pass

    def fit(self, feature_list: list) -> None:
        """Train on historical data (no-op for online detectors)."""
        pass
