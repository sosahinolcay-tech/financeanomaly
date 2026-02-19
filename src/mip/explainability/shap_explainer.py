"""SHAP-based explainability."""

from typing import Dict, List, Optional

import numpy as np
import shap

from ..config import settings
from ..detection.base import BaseDetector


class SHAPExplainer:
    """SHAP explainer for anomaly detection models."""

    def __init__(self, detector: BaseDetector, feature_names: List[str]):
        self.detector = detector
        self.feature_names = feature_names
        self.explainer: Optional[shap.TreeExplainer] = None
        if hasattr(detector, "model") and detector.model is not None:
            try:
                if hasattr(detector.model, "estimators_"):
                    self.explainer = shap.TreeExplainer(detector.model)
            except Exception:
                pass

    def explain(self, features: Dict[str, float], top_k: int = None) -> Dict:
        top_k = top_k or settings.SHAP_TOP_K_FEATURES
        arr = np.array([features.get(n, 0.0) for n in self.feature_names])
        if self.explainer is not None:
            vals = self.explainer.shap_values(arr.reshape(1, -1))
            vals = vals[0] if isinstance(vals, list) else vals
            shap_vals = vals.flatten()
        else:
            shap_vals = np.abs(arr) / (np.sum(np.abs(arr)) + 1e-9)
        top_idx = np.argsort(np.abs(shap_vals))[-top_k:][::-1]
        top_features = [
            {"feature": self.feature_names[i], "value": float(arr[i]), "contribution": float(shap_vals[i])}
            for i in top_idx
        ]
        reason = self._reason(top_features)
        return {
            "shap_values": {n: float(v) for n, v in zip(self.feature_names, shap_vals)},
            "top_features": top_features,
            "reason": reason,
        }

    def _reason(self, top: List[Dict]) -> str:
        parts = []
        for f in top:
            n, v = f["feature"], f["value"]
            if "vol_spike" in n and v > 3:
                parts.append(f"Volume spike ({v:.2f}x baseline)")
            elif "imbalance" in n and abs(v) > 0.5:
                parts.append(f"Order imbalance ({v:.2f})")
            elif "volatility" in n and v > 0.1:
                parts.append(f"High volatility ({v:.4f})")
        return "; ".join(parts) if parts else "Multiple features contributed"
