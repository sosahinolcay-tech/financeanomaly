"""Unit tests for anomaly detectors."""

import pytest
import numpy as np

from mip.detection.isolation_forest import IsolationForestDetector

try:
    from mip.detection import river_detector
    from mip.detection.river_detector import RiverDetector
    HAS_RIVER = river_detector.HAS_RIVER
except ImportError:
    HAS_RIVER = False


def test_isolation_forest():
    detector = IsolationForestDetector()
    np.random.seed(42)
    training = [
        {
            "mean_return": np.random.normal(0, 0.01),
            "vol_spike": np.random.uniform(0.5, 2.0),
            "imbalance": np.random.uniform(-0.5, 0.5),
            "volatility": np.random.uniform(0.01, 0.1),
        }
        for _ in range(100)
    ]
    detector.fit(training)
    assert detector.is_fitted
    test_f = {"mean_return": 0.01, "vol_spike": 1.0, "imbalance": 0.0, "volatility": 0.05}
    assert isinstance(detector.score(test_f), float)
    assert isinstance(detector.is_anomaly(test_f), bool)


@pytest.mark.skipif(not HAS_RIVER, reason="river not installed")
def test_river_detector():
    detector = RiverDetector()
    training = [
        {"mean_return": np.random.normal(0, 0.01), "vol_spike": np.random.uniform(0.5, 2.0), "imbalance": np.random.uniform(-0.5, 0.5)}
        for _ in range(50)
    ]
    detector.fit(training)
    test_f = {"mean_return": 0.01, "vol_spike": 1.0, "imbalance": 0.0}
    assert 0 <= detector.score(test_f) <= 1
    assert isinstance(detector.is_anomaly(test_f), bool)
