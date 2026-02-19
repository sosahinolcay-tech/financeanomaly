"""Online adaptive detector using River."""

from typing import Dict, Optional

try:
    from river import anomaly, compose, preprocessing
    HAS_RIVER = True
except ImportError:
    HAS_RIVER = False
    anomaly = compose = preprocessing = None

from ..config import settings
from .base import BaseDetector


class RiverDetector(BaseDetector):
    """Online adaptive anomaly detector using HalfSpaceTrees."""

    def __init__(self, threshold: float = None, n_trees: int = None):
        self.threshold = threshold or settings.ONLINE_DETECTOR_THRESHOLD
        self.n_trees = n_trees or settings.ONLINE_DETECTOR_N_TREES
        self.model = None
        self.feature_names: Optional[list] = None
        self.is_initialized = False

    def _to_dict(self, features: Dict[str, float], names: list) -> dict:
        return {n: features.get(n, 0.0) for n in names}

    def _initialize(self, feature_names: list) -> None:
        if not HAS_RIVER:
            raise ImportError("river is required. pip install river")
        self.feature_names = sorted(feature_names)
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            anomaly.HalfSpaceTrees(
                n_trees=self.n_trees,
                height=15,
                window_size=250,
                seed=42,
            ),
        )
        self.is_initialized = True

    def fit(self, feature_list: list) -> None:
        if not feature_list:
            raise ValueError("Cannot fit on empty feature list")
        if self.feature_names is None:
            self.feature_names = sorted(list(feature_list[0].keys()))
            self._initialize(self.feature_names)
        for f in feature_list:
            self.model.learn_one(self._to_dict(f, self.feature_names))

    def score(self, features: Dict[str, float]) -> float:
        if not self.is_initialized:
            self.feature_names = sorted(list(features.keys()))
            self._initialize(self.feature_names)
        x = self._to_dict(features, self.feature_names)
        s = float(self.model.score_one(x))
        self.model.learn_one(x)  # Online learning
        return s

    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        score = self.score(features)
        thresh = threshold if threshold is not None else self.threshold
        return score > thresh
