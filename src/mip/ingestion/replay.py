"""CSV replay ingestion for testing and demos."""

import asyncio
import random
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

import pandas as pd

from ..config import settings
from ..domain.events import MarketEvent
from .base import BaseIngestion


class ReplayIngestion(BaseIngestion):
    """Replays market events from CSV or generates synthetic data."""

    def __init__(self, speed_multiplier: float = None):
        super().__init__()
        self.speed_multiplier = speed_multiplier or settings.STREAM_SPEED_MULTIPLIER

    async def stream_from_csv(
        self,
        csv_path: Path,
        start_time: Optional[datetime] = None,
    ) -> AsyncIterator[MarketEvent]:
        """Stream events from CSV file."""
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = pd.read_csv(csv_path)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            if start_time is None:
                start_time = datetime.now()
            df["timestamp"] = pd.date_range(
                start=start_time, periods=len(df), freq="1S"
            )

        for col in ["symbol", "price", "size"]:
            if col not in df.columns:
                raise ValueError(f"CSV missing required column: {col}")

        df = df.sort_values("timestamp").reset_index(drop=True)
        self._running = True
        prev_ts = None

        for _, row in df.iterrows():
            if not self.is_running:
                break
            event = MarketEvent(
                timestamp=row["timestamp"],
                symbol=str(row["symbol"]),
                price=float(row["price"]),
                size=float(row["size"]),
                side=row.get("side", random.choice(["buy", "sell"])),
            )
            if prev_ts is not None:
                time_diff = (event.timestamp - prev_ts).total_seconds()
                sleep_time = max(0, time_diff / self.speed_multiplier)
                await asyncio.sleep(sleep_time)
            prev_ts = event.timestamp
            yield event

    async def stream(self) -> AsyncIterator[MarketEvent]:
        """Default: stream from sample data path."""
        async for event in self.stream_from_csv(settings.SAMPLE_DATA_PATH):
            yield event

    def stop(self) -> None:
        super().stop()
