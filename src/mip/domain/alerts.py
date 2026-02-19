"""Alert domain model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


@dataclass
class Alert:
    """Anomaly alert."""

    id: int
    timestamp: datetime
    symbol: str
    anomaly_score: float
    is_anomaly: bool
    features: Dict[str, float]
    explanation: Dict[str, Any]
    created_at: str
