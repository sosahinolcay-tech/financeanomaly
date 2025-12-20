"""Base classes for anomaly detectors."""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import numpy as np


class BaseDetector(ABC):
    """Abstract base class for anomaly detectors."""
    
    @abstractmethod
    def score(self, features: Dict[str, float]) -> float:
        """
        Compute anomaly score for given features.
        
        Args:
            features: Dictionary of feature names to values
        
        Returns:
            Anomaly score (lower = more anomalous for isolation forest)
        """
        pass
    
    @abstractmethod
    def is_anomaly(self, features: Dict[str, float], threshold: Optional[float] = None) -> bool:
        """
        Determine if features represent an anomaly.
        
        Args:
            features: Dictionary of feature names to values
            threshold: Optional threshold override
        
        Returns:
            True if anomaly detected
        """
        pass
    
    def fit(self, feature_list: list[Dict[str, float]]):
        """
        Train the detector on historical data.
        
        Args:
            feature_list: List of feature dictionaries
        """
        # Default: no-op (for online detectors that don't need training)
        pass

