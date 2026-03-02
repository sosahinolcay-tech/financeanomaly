"""Alpaca WebSocket ingestion with reconnect/backoff."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import AsyncIterator, Iterable

from ..domain.events import MarketEvent
from .base import BaseIngestion

try:
    import websockets
except Exception:  # pragma: no cover - optional runtime dependency
    websockets = None


class AlpacaWebSocketIngestion(BaseIngestion):
    """Live ingestion client for Alpaca trade stream."""

    def __init__(
        self,
        symbols: Iterable[str],
        api_key: str | None = None,
        secret_key: str | None = None,
        feed: str = "iex",
        reconnect_base_delay: float = 1.0,
        reconnect_max_delay: float = 30.0,
    ) -> None:
        super().__init__()
        self.symbols = [s.upper() for s in symbols]
        self.api_key = api_key
        self.secret_key = secret_key
        self.feed = feed
        self.reconnect_base_delay = reconnect_base_delay
        self.reconnect_max_delay = reconnect_max_delay

    @property
    def uri(self) -> str:
        return f"wss://stream.data.alpaca.markets/v2/{self.feed}"

    @staticmethod
    def _parse_trade(msg: dict) -> MarketEvent | None:
        if msg.get("T") != "t":
            return None
        ts = msg.get("t")
        if not ts:
            return None
        timestamp = datetime.fromisoformat(str(ts).replace("Z", "+00:00")).replace(tzinfo=None)
        return MarketEvent(
            timestamp=timestamp,
            symbol=str(msg.get("S", "")).upper(),
            price=float(msg.get("p", 0.0)),
            size=float(msg.get("s", 0.0)),
            side="buy",
        )

    async def _authenticate_and_subscribe(self, ws) -> None:
        if self.api_key and self.secret_key:
            await ws.send(
                json.dumps(
                    {"action": "auth", "key": self.api_key, "secret": self.secret_key}
                )
            )
        await ws.send(json.dumps({"action": "subscribe", "trades": self.symbols}))

    async def stream(self) -> AsyncIterator[MarketEvent]:
        """Stream trades from Alpaca with retry and exponential backoff."""
        if websockets is None:
            raise RuntimeError("websockets is required for Alpaca ingestion: pip install websockets")

        delay = self.reconnect_base_delay
        while self.is_running:
            try:
                async with websockets.connect(self.uri, ping_interval=20, ping_timeout=20) as ws:
                    await self._authenticate_and_subscribe(ws)
                    delay = self.reconnect_base_delay
                    async for raw in ws:
                        if not self.is_running:
                            break
                        payload = json.loads(raw)
                        messages = payload if isinstance(payload, list) else [payload]
                        for msg in messages:
                            event = self._parse_trade(msg)
                            if event is not None:
                                yield event
            except Exception:
                if not self.is_running:
                    break
                await asyncio.sleep(delay)
                delay = min(self.reconnect_max_delay, delay * 2)
