"""Base ingestion interface."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from ..domain.events import MarketEvent


class BaseIngestion(ABC):
    """Base class for market data ingestion."""

    def __init__(self) -> None:
        self._running = True

    @abstractmethod
    async def stream(self) -> AsyncIterator[MarketEvent]:
        """Stream market events."""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop the ingestion."""
        self._running = False

    @property
    def is_running(self) -> bool:
        """Current running state."""
        return self._running
