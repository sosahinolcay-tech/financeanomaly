"""Online adaptive anomaly detector using river library."""

from typing import Dict, Optional
import numpy as np
from river import anomaly, compose, preprocessing

from .base import BaseDetector
from ..utils.config import settings


class OnlineDetector(BaseDetector):
    """Online adaptive anomaly detector using HalfSpaceTrees."""
    
    def __init__(self, threshold: float = 0.5, n_trees: int = 10):
        """
        Initialize online detector.
        
        Args:
            threshold: Anomaly score threshold (0-1, higher = more sensitive)
            n_trees: Number of trees in ensemble
        """
        self.threshold = threshold
        self.n_trees = n_trees
        self.model = None
        self.feature_names: Optional[list[str]] = None
        self.is_initialized = False
    
    def _features_to_dict(self, features: Dict[str, float], feature_names: list[str]) -> dict:
        """Convert feature dict to river-compatible format."""
        return {name: features.get(name, 0.0) for name in feature_names}
    
    def initialize(self, feature_names: list[str]):
        """
        Initialize the model with feature names.
        
        Args:
            feature_names: List of feature names
        """
        self.feature_names = sorted(feature_names)
        
        # Create pipeline: normalize -> anomaly detector
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(),
            anomaly.HalfSpaceTrees(
                n_trees=self.n_trees,
                height=15,
                window_size=250,
                seed=42
            )
        )
        self.is_initialized = True
    
    def fit(self, feature_list: list[Dict[str, float]]):
        """
        Initialize and warm-up the model.
        
        Args:
            feature_list: List of feature dictionaries
        """
        if not feature_list:
            raise ValueError("Cannot fit on empty feature list")
        
        # Extract feature names
        if self.feature_names is None:
            self.feature_names = sorted(list(feature_list[0].keys()))
            self.initialize(self.feature_names)
        
        # Warm up the model
        for features in feature_list:
            x = self._features_to_dict(features, self.feature_names)
            self.model.learn_one(x)
    
    def score(self, features: Dict[str, float]) -> float:
        """
        Compute anomaly score.
        
        Args:
            features: Dictionary of feature names to values
        
        Returns:
            Anomaly score (0-1, higher = more anomalous)
        """
        if not self.is_initialized or self.model is None:
            # Auto-initialize if not done
            if self.feature_names is None:
                self.feature_names = sorted(list(features.keys()))
                self.initialize(self.feature_names)
            else:
                raise ValueError("Model not initialized")
        
        x = self._features_to_dict(features, self.feature_names)
        score = self.model.score_one(x)
        
        # Update model (online learning)
        self.model.learn_one(x)
        
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
        return score > thresh

