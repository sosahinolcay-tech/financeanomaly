"""Isolation Forest anomaly detector."""

from typing import Dict, Optional
import numpy as np
from sklearn.ensemble import IsolationForest

from .base import BaseDetector
from ..utils.config import settings


class IsolationForestDetector(BaseDetector):
    """Isolation Forest-based anomaly detector."""
    
    def __init__(
        self,
        n_estimators: int = None,
        contamination: float = None,
        threshold: float = None
    ):
        """
        Initialize Isolation Forest detector.
        
        Args:
            n_estimators: Number of trees (default from config)
            contamination: Expected proportion of anomalies (default from config)
            threshold: Anomaly score threshold (default from config)
        """
        self.n_estimators = n_estimators or settings.ISOLATION_FOREST_N_ESTIMATORS
        self.contamination = contamination or settings.ISOLATION_FOREST_CONTAMINATION
        self.threshold = threshold or settings.ANOMALY_THRESHOLD
        
        self.model: Optional[IsolationForest] = None
        self.feature_names: Optional[list[str]] = None
        self.is_fitted = False
    
    def _features_to_array(self, features: Dict[str, float], feature_names: list[str]) -> np.ndarray:
        """Convert feature dict to numpy array."""
        return np.array([features.get(name, 0.0) for name in feature_names])
    
    def fit(self, feature_list: list[Dict[str, float]]):
        """
        Train the isolation forest on historical data.
        
        Args:
            feature_list: List of feature dictionaries
        """
        if not feature_list:
            raise ValueError("Cannot fit on empty feature list")
        
        # Extract feature names from first sample
        self.feature_names = sorted(list(feature_list[0].keys()))
        
        # Convert to numpy array
        X = np.array([
            self._features_to_array(f, self.feature_names)
            for f in feature_list
        ])
        
        # Train model
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42
        )
        self.model.fit(X)
        self.is_fitted = True
    
    def score(self, features: Dict[str, float]) -> float:
        """
        Compute anomaly score (decision function).
        
        Args:
            features: Dictionary of feature names to values
        
        Returns:
            Anomaly score (lower = more anomalous)
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted before scoring")
        
        if self.feature_names is None:
            raise ValueError("Feature names not set")
        
        X = self._features_to_array(features, self.feature_names).reshape(1, -1)
        score = self.model.decision_function(X)[0]
        return float(score)
    
    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        """
        Determine if features represent an anomaly.
        
        Args:
            features: Dictionary of feature names to values
            threshold: Optional threshold override
        
        Returns:
            True if anomaly detected
        """
        score = self.score(features)
        thresh = threshold if threshold is not None else self.threshold
        return score < thresh
    
    def predict(self, features: Dict[str, float]) -> int:
        """
        Predict anomaly label (-1 for anomaly, 1 for normal).
        
        Args:
            features: Dictionary of feature names to values
        
        Returns:
            -1 for anomaly, 1 for normal
        """
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted before prediction")
        
        if self.feature_names is None:
            raise ValueError("Feature names not set")
        
        X = self._features_to_array(features, self.feature_names).reshape(1, -1)
        return int(self.model.predict(X)[0])

