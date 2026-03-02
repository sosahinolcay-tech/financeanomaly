"""Ensemble detector with weighted multi-model scoring."""

from __future__ import annotations

from typing import Dict, Iterable, Optional

import numpy as np

from .base import Detector


class WeightedEnsembleDetector(Detector):
    """Combine multiple detectors with directional weighted scoring."""

    def __init__(
        self,
        detectors: Iterable[Detector],
        directions: Optional[Iterable[str]] = None,
        weights: Optional[Iterable[float]] = None,
        threshold: float = 0.0,
    ) -> None:
        self.detectors = list(detectors)
        if not self.detectors:
            raise ValueError("At least one detector is required")

        self.directions = list(directions) if directions is not None else ["above"] * len(self.detectors)
        if len(self.directions) != len(self.detectors):
            raise ValueError("directions length must match detectors")

        raw_weights = np.asarray(list(weights) if weights is not None else [1.0] * len(self.detectors), dtype=float)
        if raw_weights.size != len(self.detectors):
            raise ValueError("weights length must match detectors")
        self.weights = raw_weights / np.sum(raw_weights)
        self.threshold = threshold

    def fit(self, feature_list: list[Dict[str, float]]) -> None:
        for detector in self.detectors:
            detector.fit(feature_list)

    def component_scores(self, features: Dict[str, float]) -> list[float]:
        return [float(detector.score(features)) for detector in self.detectors]

    def score(self, features: Dict[str, float]) -> float:
        scores = np.asarray(self.component_scores(features), dtype=float)
        transformed = []
        for score, direction in zip(scores, self.directions):
            transformed.append(-score if direction == "below" else score)
        return float(np.dot(np.asarray(transformed, dtype=float), self.weights))

    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        thresh = self.threshold if threshold is None else threshold
        return self.score(features) > thresh
