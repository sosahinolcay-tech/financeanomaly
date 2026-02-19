"""Feature vector domain model."""

from typing import Dict


class FeatureVector:
    """Typed feature vector for anomaly detection."""

    def __init__(self, symbol: str, features: Dict[str, float]):
        self.symbol = symbol
        self.features = features

    def to_dict(self) -> Dict[str, float]:
        return dict(self.features)
