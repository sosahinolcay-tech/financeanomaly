"""Alert scoring utilities."""

from typing import Dict


def compute_alert_score(features: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """Simple weighted score (placeholder for ensemble)."""
    if weights is None:
        return 0.0
    return sum(features.get(k, 0) * w for k, w in weights.items())
