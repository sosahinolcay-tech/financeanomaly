"""Anomaly score domain model - pure, no infra."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AnomalyScore:
    """Anomaly score from detector."""

    value: float
    symbol: str
    timestamp: datetime
