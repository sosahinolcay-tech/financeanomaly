"""Counterfactual explanation utilities."""

from __future__ import annotations

from typing import Dict


class CounterfactualExplainer:
    """Generate simple actionable counterfactual statements."""

    def explain(self, features: Dict[str, float], anomaly_score: float, threshold: float) -> Dict[str, object]:
        """Produce a lightweight counterfactual explanation."""
        if not features:
            return {"reason": "Insufficient features for counterfactual analysis."}

        # Pick the strongest absolute contributor as a proxy for intervention target.
        top_feature = max(features.items(), key=lambda kv: abs(float(kv[1])))
        name, value = top_feature[0], float(top_feature[1])
        suggested = self._suggest(name, value)

        return {
            "feature": name,
            "current_value": value,
            "suggested_value": suggested,
            "message": (
                f"If `{name}` were {suggested:.4f} instead of {value:.4f}, "
                "this event would be less likely to trigger an alert."
            ),
            "score": anomaly_score,
            "threshold": threshold,
        }

    @staticmethod
    def _suggest(feature_name: str, current_value: float) -> float:
        """Heuristic counterfactual target for common anomaly drivers."""
        if "vol_spike" in feature_name:
            return min(current_value, 1.2)
        if "imbalance" in feature_name:
            return 0.0
        if "volatility" in feature_name:
            return current_value * 0.5
        if "price_change" in feature_name or "return" in feature_name:
            return current_value * 0.5
        return current_value * 0.8
