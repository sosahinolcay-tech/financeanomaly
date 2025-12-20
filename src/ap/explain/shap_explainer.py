"""SHAP-based explainability for anomaly detection."""

from typing import Dict, List, Optional
import numpy as np
import shap
from sklearn.ensemble import IsolationForest

from ..models.base import BaseDetector
from ..utils.config import settings


class SHAPExplainer:
    """SHAP explainer for anomaly detection models."""
    
    def __init__(self, detector: BaseDetector, feature_names: List[str]):
        """
        Initialize SHAP explainer.
        
        Args:
            detector: Trained anomaly detector
            feature_names: List of feature names in order
        """
        self.detector = detector
        self.feature_names = feature_names
        self.explainer: Optional[shap.TreeExplainer] = None
        
        # Initialize explainer if detector has sklearn model
        if hasattr(detector, 'model') and detector.model is not None:
            try:
                if hasattr(detector.model, 'estimators_'):
                    # Isolation Forest
                    self.explainer = shap.TreeExplainer(detector.model)
            except Exception:
                # If SHAP can't initialize, will use fallback
                pass
    
    def explain(
        self,
        features: Dict[str, float],
        background_data: Optional[List[Dict[str, float]]] = None,
        top_k: int = None
    ) -> Dict:
        """
        Explain anomaly score for given features.
        
        Args:
            features: Feature dictionary to explain
            background_data: Optional background data for SHAP (if not using TreeExplainer)
            top_k: Number of top features to return (default from config)
        
        Returns:
            Dictionary with 'shap_values', 'top_features', and 'reason'
        """
        top_k = top_k or settings.SHAP_TOP_K_FEATURES
        
        # Convert features to array
        feature_array = np.array([features.get(name, 0.0) for name in self.feature_names])
        
        if self.explainer is not None:
            # Use TreeExplainer for tree-based models
            shap_values = self.explainer.shap_values(feature_array.reshape(1, -1))
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # For binary outputs
            shap_values = shap_values.flatten()
        else:
            # Fallback: use simple feature importance based on absolute values
            # This is a simplified approach when SHAP can't be used directly
            shap_values = np.abs(feature_array)
            shap_values = shap_values / (np.sum(shap_values) + 1e-9)
        
        # Get top K features
        top_indices = np.argsort(np.abs(shap_values))[-top_k:][::-1]
        
        top_features = [
            {
                "feature": self.feature_names[idx],
                "value": float(feature_array[idx]),
                "shap_value": float(shap_values[idx]),
                "contribution": float(shap_values[idx])
            }
            for idx in top_indices
        ]
        
        # Generate human-readable reason
        reason = self._generate_reason(top_features, features)
        
        return {
            "shap_values": {name: float(val) for name, val in zip(self.feature_names, shap_values)},
            "top_features": top_features,
            "reason": reason
        }
    
    def _generate_reason(self, top_features: List[Dict], features: Dict[str, float]) -> str:
        """
        Generate human-readable explanation.
        
        Args:
            top_features: Top contributing features
            features: Original feature values
        
        Returns:
            Human-readable explanation string
        """
        reasons = []
        
        for feat in top_features:
            name = feat["feature"]
            value = feat["value"]
            contribution = feat["contribution"]
            
            if "vol_spike" in name:
                if value > 3.0:
                    reasons.append(f"Volume spike detected ({value:.2f}x baseline)")
            elif "imbalance" in name:
                if abs(value) > 0.5:
                    direction = "buy" if value > 0 else "sell"
                    reasons.append(f"Significant {direction} pressure (imbalance: {value:.2f})")
            elif "volatility" in name or "std_return" in name:
                if value > 0.1:
                    reasons.append(f"High volatility ({value:.4f})")
            elif "price_change" in name:
                if abs(value) > 0.05:
                    direction = "increase" if value > 0 else "decrease"
                    reasons.append(f"Large price {direction} ({abs(value)*100:.2f}%)")
            elif "return" in name:
                if abs(value) > 0.02:
                    reasons.append(f"Unusual return pattern ({value:.4f})")
        
        if not reasons:
            # Generic explanation
            reasons.append("Multiple features contributed to anomaly score")
        
        return "; ".join(reasons)

