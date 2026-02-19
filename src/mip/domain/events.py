"""Market event domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketEvent:
    """Represents a market trade event."""

    timestamp: datetime
    symbol: str
    price: float
    size: float
    side: str = "buy"  # "buy" or "sell"

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "price": self.price,
            "size": self.size,
            "side": self.side,
        }
