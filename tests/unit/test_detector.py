"""Unit tests for anomaly detectors."""

import pytest
import numpy as np
from src.ap.models.isolation_forest import IsolationForestDetector

# Try to import online detector, skip tests if not available
try:
    from src.ap.models.online_detector import OnlineDetector
    HAS_RIVER = True
except ImportError:
    HAS_RIVER = False
    OnlineDetector = None


def test_isolation_forest_detector():
    """Test Isolation Forest detector."""
    detector = IsolationForestDetector()
    
    # Generate training data
    np.random.seed(42)
    training_features = []
    for _ in range(100):
        features = {
            "mean_return": np.random.normal(0, 0.01),
            "vol_spike": np.random.uniform(0.5, 2.0),
            "imbalance": np.random.uniform(-0.5, 0.5),
            "volatility": np.random.uniform(0.01, 0.1)
        }
        training_features.append(features)
    
    # Train
    detector.fit(training_features)
    assert detector.is_fitted
    
    # Test scoring
    test_features = {
        "mean_return": 0.01,
        "vol_spike": 1.0,
        "imbalance": 0.0,
        "volatility": 0.05
    }
    
    score = detector.score(test_features)
    assert isinstance(score, float)
    
    is_anomaly = detector.is_anomaly(test_features)
    assert isinstance(is_anomaly, bool)


@pytest.mark.skipif(not HAS_RIVER, reason="river library not available")
def test_online_detector():
    """Test online detector."""
    detector = OnlineDetector()
    
    # Generate training data
    training_features = []
    for _ in range(50):
        features = {
            "mean_return": np.random.normal(0, 0.01),
            "vol_spike": np.random.uniform(0.5, 2.0),
            "imbalance": np.random.uniform(-0.5, 0.5)
        }
        training_features.append(features)
    
    # Train
    detector.fit(training_features)
    assert detector.is_initialized
    
    # Test scoring
    test_features = {
        "mean_return": 0.01,
        "vol_spike": 1.0,
        "imbalance": 0.0
    }
    
    score = detector.score(test_features)
    assert 0 <= score <= 1  # Online detector returns 0-1
    
    is_anomaly = detector.is_anomaly(test_features)
    assert isinstance(is_anomaly, bool)

