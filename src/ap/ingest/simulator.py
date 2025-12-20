"""Market data stream simulator for local testing and demos."""

import asyncio
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncIterator, Optional
from dataclasses import dataclass
import pandas as pd

from ..utils.config import settings


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
            "side": self.side
        }


class StreamSimulator:
    """Simulates a market data stream from CSV or generates synthetic data."""
    
    def __init__(self, speed_multiplier: float = 1.0):
        """
        Initialize simulator.
        
        Args:
            speed_multiplier: Speed factor (1.0 = real-time, >1.0 = faster)
        """
        self.speed_multiplier = speed_multiplier
        self.running = False
    
    async def simulate_from_csv(
        self, 
        csv_path: Path,
        start_time: Optional[datetime] = None
    ) -> AsyncIterator[MarketEvent]:
        """
        Simulate stream from CSV file.
        
        Args:
            csv_path: Path to CSV file with columns: timestamp, symbol, price, size
            start_time: Optional start time (defaults to now)
        
        Yields:
            MarketEvent objects
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Parse timestamps
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            # Generate timestamps if not present
            if start_time is None:
                start_time = datetime.now()
            df["timestamp"] = pd.date_range(
                start=start_time,
                periods=len(df),
                freq="1S"
            )
        
        # Ensure required columns
        required_cols = ["symbol", "price", "size"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"CSV missing required column: {col}")
        
        # Sort by timestamp
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        self.running = True
        prev_ts = None
        
        for idx, row in df.iterrows():
            if not self.running:
                break
            
            event = MarketEvent(
                timestamp=row["timestamp"],
                symbol=str(row["symbol"]),
                price=float(row["price"]),
                size=float(row["size"]),
                side=row.get("side", random.choice(["buy", "sell"]))
            )
            
            # Calculate sleep time based on timestamp difference
            if prev_ts is not None:
                time_diff = (event.timestamp - prev_ts).total_seconds()
                sleep_time = max(0, time_diff / self.speed_multiplier)
                await asyncio.sleep(sleep_time)
            
            prev_ts = event.timestamp
            yield event
    
    async def generate_synthetic_stream(
        self,
        symbols: list[str],
        duration_seconds: int = 3600,
        events_per_second: float = 1.0,
        start_time: Optional[datetime] = None
    ) -> AsyncIterator[MarketEvent]:
        """
        Generate synthetic market data stream.
        
        Args:
            symbols: List of symbols to generate data for
            duration_seconds: How long to generate data
            events_per_second: Average events per second
            start_time: Optional start time (defaults to now)
        
        Yields:
            MarketEvent objects
        """
        if start_time is None:
            start_time = datetime.now()
        
        self.running = True
        end_time = start_time + timedelta(seconds=duration_seconds)
        current_time = start_time
        
        # Initialize prices per symbol
        prices = {symbol: 100.0 + random.uniform(-10, 10) for symbol in symbols}
        
        interval = 1.0 / events_per_second / self.speed_multiplier
        
        while current_time < end_time and self.running:
            symbol = random.choice(symbols)
            base_price = prices[symbol]
            
            # Random walk with slight drift
            change = random.gauss(0, 0.5)
            new_price = max(0.01, base_price + change)
            prices[symbol] = new_price
            
            event = MarketEvent(
                timestamp=current_time,
                symbol=symbol,
                price=new_price,
                size=random.uniform(0.1, 10.0),
                side=random.choice(["buy", "sell"])
            )
            
            yield event
            
            await asyncio.sleep(interval)
            current_time += timedelta(seconds=interval * self.speed_multiplier)
    
    def stop(self):
        """Stop the simulator."""
        self.running = False

