"""Pydantic schemas for API and validation."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class AlertCreate(BaseModel):
    """Schema for creating an alert."""

    timestamp: datetime
    symbol: str
    anomaly_score: float
    is_anomaly: bool
    features: Dict[str, float]
    explanation: Dict[str, Any]
