"""Streaming feature computation for market events."""

from collections import defaultdict, deque
from typing import Dict, Optional
import numpy as np
from datetime import datetime, timedelta

from ..ingest.simulator import MarketEvent
from ..utils.config import settings


class FeatureStore:
    """Maintains sliding windows and computes features per symbol."""
    
    def __init__(self, window_seconds: int = None):
        """
        Initialize feature store.
        
        Args:
            window_seconds: Time window for feature computation (default from config)
        """
        self.window_seconds = window_seconds or settings.FEATURE_WINDOW_SIZE
        self.min_events = settings.MIN_EVENTS_FOR_FEATURES
        
        # Per-symbol storage: deque of (timestamp, price, size)
        self.events: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)  # reasonable maxlen
        )
    
    def update(self, event: MarketEvent):
        """
        Update feature store with new event.
        
        Args:
            event: MarketEvent to add
        """
        cutoff_time = event.timestamp - timedelta(seconds=self.window_seconds)
        
        # Add new event
        self.events[event.symbol].append((
            event.timestamp,
            event.price,
            event.size,
            event.side
        ))
        
        # Remove old events (cleanup)
        while (self.events[event.symbol] and 
               self.events[event.symbol][0][0] < cutoff_time):
            self.events[event.symbol].popleft()
    
    def compute_features(self, symbol: str) -> Dict[str, float]:
        """
        Compute features for a symbol.
        
        Args:
            symbol: Symbol to compute features for
        
        Returns:
            Dictionary of feature names to values
        """
        events = self.events.get(symbol, deque())
        
        if len(events) < self.min_events:
            return {}
        
        # Extract arrays
        timestamps = np.array([e[0] for e in events])
        prices = np.array([e[1] for e in events])
        sizes = np.array([e[2] for e in events])
        sides = np.array([e[3] for e in events])
        
        features = {}
        
        # Price-based features
        if len(prices) >= 2:
            # Returns
            returns = np.diff(prices) / prices[:-1]
            features["mean_return"] = float(np.mean(returns))
            features["std_return"] = float(np.std(returns)) if len(returns) > 1 else 0.0
            features["max_return"] = float(np.max(returns)) if len(returns) > 0 else 0.0
            features["min_return"] = float(np.min(returns)) if len(returns) > 0 else 0.0
            
            # Volatility (annualized approximation)
            if features["std_return"] > 0:
                features["volatility"] = float(features["std_return"] * np.sqrt(252 * 24 * 3600))
            else:
                features["volatility"] = 0.0
        
        # Volume features
        if len(sizes) > 0:
            features["total_volume"] = float(np.sum(sizes))
            features["mean_volume"] = float(np.mean(sizes))
            features["max_volume"] = float(np.max(sizes))
            
            # Volume spike (current vs mean)
            if features["mean_volume"] > 0:
                features["vol_spike"] = float(sizes[-1] / features["mean_volume"])
            else:
                features["vol_spike"] = 0.0
        
        # Bid-ask imbalance (simplified: buy vs sell volume)
        buy_volume = np.sum(sizes[sides == "buy"])
        sell_volume = np.sum(sizes[sides == "sell"])
        total_vol = buy_volume + sell_volume
        if total_vol > 0:
            features["imbalance"] = float((buy_volume - sell_volume) / total_vol)
        else:
            features["imbalance"] = 0.0
        
        # Price change features
        if len(prices) >= 2:
            price_change = prices[-1] - prices[0]
            price_change_pct = price_change / prices[0] if prices[0] > 0 else 0.0
            features["price_change"] = float(price_change)
            features["price_change_pct"] = float(price_change_pct)
        
        # Event frequency
        if len(timestamps) >= 2:
            time_span = (timestamps[-1] - timestamps[0]).total_seconds()
            if time_span > 0:
                features["events_per_second"] = float(len(events) / time_span)
            else:
                features["events_per_second"] = 0.0
        
        # Normalize features to avoid extreme values
        for key in ["vol_spike", "imbalance", "price_change_pct"]:
            if key in features:
                features[key] = np.clip(features[key], -10, 10)
        
        return features
    
    def get_feature_names(self) -> list[str]:
        """Get list of all possible feature names."""
        return [
            "mean_return", "std_return", "max_return", "min_return",
            "volatility", "total_volume", "mean_volume", "max_volume",
            "vol_spike", "imbalance", "price_change", "price_change_pct",
            "events_per_second"
        ]

