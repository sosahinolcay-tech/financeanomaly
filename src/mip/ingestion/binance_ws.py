"""Binance WebSocket ingestion with reconnect/backoff."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncIterator, Iterable

from ..domain.events import MarketEvent
from .base import BaseIngestion

try:
    import websockets
except Exception:  # pragma: no cover - optional runtime dependency
    websockets = None


class BinanceWebSocketIngestion(BaseIngestion):
    """Live ingestion client for Binance trade streams."""

    def __init__(
        self,
        symbols: Iterable[str],
        reconnect_base_delay: float = 1.0,
        reconnect_max_delay: float = 30.0,
    ) -> None:
        super().__init__()
        self.symbols = [s.lower() for s in symbols]
        self.reconnect_base_delay = reconnect_base_delay
        self.reconnect_max_delay = reconnect_max_delay

    @staticmethod
    def _build_uri(symbols: list[str]) -> str:
        streams = "/".join(f"{symbol}@trade" for symbol in symbols)
        return f"wss://stream.binance.com:9443/stream?streams={streams}"

    @staticmethod
    def _parse_trade_message(raw: str) -> MarketEvent | None:
        payload = json.loads(raw)
        data = payload.get("data", payload)
        if not isinstance(data, dict) or "p" not in data or "q" not in data:
            return None

        ts_ms = int(data.get("T", 0))
        side = "sell" if bool(data.get("m", False)) else "buy"
        return MarketEvent(
            timestamp=datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).replace(tzinfo=None),
            symbol=str(data.get("s", "")).upper(),
            price=float(data["p"]),
            size=float(data["q"]),
            side=side,
        )

    async def stream(self) -> AsyncIterator[MarketEvent]:
        """Stream trades from Binance with retry and exponential backoff."""
        if websockets is None:
            raise RuntimeError("websockets is required for Binance ingestion: pip install websockets")

        uri = self._build_uri(self.symbols)
        delay = self.reconnect_base_delay
        while self.is_running:
            try:
                async with websockets.connect(uri, ping_interval=20, ping_timeout=20) as ws:
                    delay = self.reconnect_base_delay
                    async for raw in ws:
                        if not self.is_running:
                            break
                        event = self._parse_trade_message(raw)
                        if event is not None:
                            yield event
            except Exception:
                if not self.is_running:
                    break
                await asyncio.sleep(delay)
                delay = min(self.reconnect_max_delay, delay * 2)
