"""Base ingestion interface."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator

from ..domain.events import MarketEvent


class BaseIngestion(ABC):
    """Base class for market data ingestion."""

    @abstractmethod
    async def stream(self) -> AsyncIterator[MarketEvent]:
        """Stream market events."""
        pass

    def stop(self) -> None:
        """Stop the ingestion."""
        pass
