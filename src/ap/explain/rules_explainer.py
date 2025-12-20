"""Rule-based explainability for anomaly detection."""

from typing import Dict, List
from ..utils.config import settings


class RulesExplainer:
    """Simple rule-based explainer for anomaly alerts."""
    
    def __init__(self, top_k: int = None):
        """
        Initialize rules explainer.
        
        Args:
            top_k: Number of top features to explain (default from config)
        """
        self.top_k = top_k or settings.SHAP_TOP_K_FEATURES
    
    def explain(self, features: Dict[str, float], anomaly_score: float) -> Dict:
        """
        Explain anomaly using simple rules.
        
        Args:
            features: Feature dictionary
            anomaly_score: Anomaly score from detector
        
        Returns:
            Dictionary with 'top_features' and 'reason'
        """
        # Compute feature importance as absolute deviation from typical values
        # Typical values (can be learned from historical data, but using heuristics here)
        typical_values = {
            "vol_spike": 1.0,
            "imbalance": 0.0,
            "volatility": 0.05,
            "mean_return": 0.0,
            "std_return": 0.01,
            "price_change_pct": 0.0,
            "events_per_second": 1.0
        }
        
        # Compute deviations
        deviations = {}
        for name, value in features.items():
            typical = typical_values.get(name, 0.0)
            deviation = abs(value - typical)
            # Normalize by typical value if non-zero
            if typical != 0:
                deviation = deviation / abs(typical)
            deviations[name] = deviation
        
        # Get top K features by deviation
        sorted_features = sorted(
            deviations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_k]
        
        top_features = [
            {
                "feature": name,
                "value": float(features[name]),
                "deviation": float(dev),
                "contribution": float(dev)
            }
            for name, dev in sorted_features
        ]
        
        # Generate human-readable reason
        reason = self._generate_reason(top_features, features)
        
        return {
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
            deviation = feat["deviation"]
            
            if "vol_spike" in name:
                if value > 3.0:
                    reasons.append(f"Volume spike: {value:.2f}x normal (deviation: {deviation:.2f})")
            elif "imbalance" in name:
                if abs(value) > 0.5:
                    direction = "buy" if value > 0 else "sell"
                    reasons.append(f"Order imbalance: {direction} pressure ({value:.2f})")
            elif "volatility" in name or "std_return" in name:
                if value > 0.1:
                    reasons.append(f"Elevated volatility: {value:.4f} (deviation: {deviation:.2f})")
            elif "price_change" in name:
                if abs(value) > 0.05:
                    direction = "increase" if value > 0 else "decrease"
                    reasons.append(f"Price {direction}: {abs(value)*100:.2f}%")
            elif "return" in name:
                if abs(value) > 0.02:
                    reasons.append(f"Unusual return: {value:.4f}")
        
        if not reasons:
            reasons.append("Multiple features show deviations from normal patterns")
        
        return "; ".join(reasons)

