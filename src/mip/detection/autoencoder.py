"""Lightweight online autoencoder-style detector using IncrementalPCA."""

from __future__ import annotations

from collections import deque
from typing import Dict, Optional

import numpy as np
from sklearn.decomposition import IncrementalPCA

from .base import Detector


class AutoencoderDetector(Detector):
    """Approximate online autoencoder via reconstruction error."""

    def __init__(
        self,
        n_components: int = 4,
        warmup_samples: int = 100,
        z_threshold: float = 3.0,
    ) -> None:
        self.n_components = n_components
        self.warmup_samples = warmup_samples
        self.z_threshold = z_threshold

        self.feature_names: Optional[list[str]] = None
        self.model: Optional[IncrementalPCA] = None
        self._warmup = deque(maxlen=warmup_samples)
        self._errors = deque(maxlen=2000)
        self.is_initialized = False

    def _to_array(self, features: Dict[str, float]) -> np.ndarray:
        if self.feature_names is None:
            self.feature_names = sorted(list(features.keys()))
        return np.asarray([features.get(name, 0.0) for name in self.feature_names], dtype=float)

    def fit(self, feature_list: list[Dict[str, float]]) -> None:
        if not feature_list:
            raise ValueError("Cannot fit on empty feature list")

        self.feature_names = sorted(list(feature_list[0].keys()))
        X = np.asarray([self._to_array(f) for f in feature_list], dtype=float)
        n_components = max(1, min(self.n_components, X.shape[1], X.shape[0]))

        self.model = IncrementalPCA(n_components=n_components)
        self.model.fit(X)
        self.is_initialized = True

    def score(self, features: Dict[str, float]) -> float:
        x = self._to_array(features)

        if not self.is_initialized:
            self._warmup.append(x)
            if len(self._warmup) >= self.warmup_samples:
                X = np.asarray(self._warmup, dtype=float)
                n_components = max(1, min(self.n_components, X.shape[1], X.shape[0]))
                self.model = IncrementalPCA(n_components=n_components)
                self.model.fit(X)
                self.is_initialized = True
            return 0.0

        assert self.model is not None
        x2 = x.reshape(1, -1)
        z = self.model.transform(x2)
        x_hat = self.model.inverse_transform(z)
        err = float(np.mean((x2 - x_hat) ** 2))
        self._errors.append(err)

        # Incremental update for online adaptation.
        self.model.partial_fit(x2)
        return err

    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        err = self.score(features)
        if len(self._errors) < 30:
            return False
        mean = float(np.mean(self._errors))
        std = float(np.std(self._errors)) + 1e-9
        z = (err - mean) / std
        thresh = threshold if threshold is not None else self.z_threshold
        return z > thresh
