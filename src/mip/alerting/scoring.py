"""Alert scoring utilities."""

from typing import Dict


def compute_alert_score(features: Dict[str, float], weights: Dict[str, float] = None) -> float:
    """Compute weighted risk score from features."""
    if not features:
        return 0.0

    default_weights = {
        "vol_spike": 0.35,
        "volatility": 0.25,
        "imbalance": 0.2,
        "price_change_pct": 0.2,
    }
    effective_weights = weights or default_weights

    score = 0.0
    normalizer = 0.0
    for key, weight in effective_weights.items():
        score += abs(float(features.get(key, 0.0))) * float(weight)
        normalizer += abs(float(weight))
    if normalizer <= 0:
        return 0.0
    return score / normalizer
