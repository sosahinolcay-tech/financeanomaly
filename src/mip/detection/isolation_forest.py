"""Isolation Forest anomaly detector."""

from typing import Dict, Optional

import numpy as np
from sklearn.ensemble import IsolationForest

from ..config import settings
from .base import Detector
from .thresholding import StaticThreshold


class IsolationForestDetector(Detector):
    """Isolation Forest-based anomaly detector."""

    def __init__(self, n_estimators: int = None, contamination: float = None, threshold: float = None):
        self.n_estimators = n_estimators or settings.ISOLATION_FOREST_N_ESTIMATORS
        self.contamination = contamination or settings.ISOLATION_FOREST_CONTAMINATION
        self.threshold = threshold or settings.ANOMALY_THRESHOLD
        self.model: Optional[IsolationForest] = None
        self.feature_names: Optional[list] = None
        self.is_fitted = False

    def _features_to_array(self, features: Dict[str, float], names: list) -> np.ndarray:
        return np.array([features.get(n, 0.0) for n in names])

    def fit(self, feature_list: list) -> None:
        if not feature_list:
            raise ValueError("Cannot fit on empty feature list")
        self.feature_names = sorted(list(feature_list[0].keys()))
        X = np.array([self._features_to_array(f, self.feature_names) for f in feature_list])
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42,
        )
        self.model.fit(X)
        self.is_fitted = True

    def score(self, features: Dict[str, float]) -> float:
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted before scoring")
        X = self._features_to_array(features, self.feature_names).reshape(1, -1)
        return float(self.model.decision_function(X)[0])

    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        """Backward compat - use ThresholdStrategy in pipeline instead."""
        score = self.score(features)
        thresh = threshold if threshold is not None else self.threshold
        return StaticThreshold(thresh, "below").is_anomaly(score)
