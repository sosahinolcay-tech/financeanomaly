"""Rule-based semantic explanation."""

from typing import Dict, List

from ..config import settings


class RuleMapperExplainer:
    """Rule-based explainer for anomaly alerts."""

    def __init__(self, top_k: int = None):
        self.top_k = top_k or settings.SHAP_TOP_K_FEATURES
        self.typical = {"vol_spike": 1.0, "imbalance": 0.0, "volatility": 0.05, "mean_return": 0.0}

    def explain(self, features: Dict[str, float], anomaly_score: float) -> Dict:
        devs = {n: abs(v - self.typical.get(n, 0)) for n, v in features.items()}
        top = sorted(devs.items(), key=lambda x: x[1], reverse=True)[: self.top_k]
        top_features = [{"feature": n, "value": features[n], "deviation": d} for n, d in top]
        reason = self._reason(top_features)
        return {"top_features": top_features, "reason": reason}

    def _reason(self, top: List[Dict]) -> str:
        parts = []
        for f in top:
            n, v = f["feature"], f["value"]
            if "vol_spike" in n and v > 3:
                parts.append(f"Volume spike: {v:.2f}x")
            elif "imbalance" in n and abs(v) > 0.5:
                parts.append(f"Order imbalance: {v:.2f}")
        return "; ".join(parts) if parts else "Multiple features deviate"
