"""Feature store - sliding windows and per-symbol computation."""

from collections import defaultdict, deque
from typing import Dict

import numpy as np
from datetime import timedelta

from ..config import settings
from ..domain.events import MarketEvent


class FeatureStore:
    """Maintains sliding windows and computes features per symbol."""

    def __init__(self, window_seconds: int = None):
        self.window_seconds = window_seconds or settings.FEATURE_WINDOW_SIZE
        self.min_events = settings.MIN_EVENTS_FOR_FEATURES
        self.events: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

    def update(self, event: MarketEvent) -> None:
        cutoff_time = event.timestamp - timedelta(seconds=self.window_seconds)
        self.events[event.symbol].append((event.timestamp, event.price, event.size, event.side))
        while self.events[event.symbol] and self.events[event.symbol][0][0] < cutoff_time:
            self.events[event.symbol].popleft()

    def compute_features(self, symbol: str) -> Dict[str, float]:
        events = self.events.get(symbol, deque())
        if len(events) < self.min_events:
            return {}
        timestamps = np.array([e[0] for e in events])
        prices = np.array([e[1] for e in events])
        sizes = np.array([e[2] for e in events])
        sides = np.array([e[3] for e in events])
        features = {}
        if len(prices) >= 2:
            returns = np.diff(prices) / prices[:-1]
            features["mean_return"] = float(np.mean(returns))
            features["std_return"] = float(np.std(returns)) if len(returns) > 1 else 0.0
            features["max_return"] = float(np.max(returns)) if len(returns) > 0 else 0.0
            features["min_return"] = float(np.min(returns)) if len(returns) > 0 else 0.0
            if features["std_return"] > 0:
                features["volatility"] = float(features["std_return"] * np.sqrt(252 * 24 * 3600))
            else:
                features["volatility"] = 0.0
        if len(sizes) > 0:
            features["total_volume"] = float(np.sum(sizes))
            features["mean_volume"] = float(np.mean(sizes))
            features["max_volume"] = float(np.max(sizes))
            features["vol_spike"] = float(sizes[-1] / features["mean_volume"]) if features["mean_volume"] > 0 else 0.0
        buy_vol = np.sum(sizes[sides == "buy"])
        sell_vol = np.sum(sizes[sides == "sell"])
        total_vol = buy_vol + sell_vol
        features["imbalance"] = float((buy_vol - sell_vol) / total_vol) if total_vol > 0 else 0.0
        if len(prices) >= 2:
            price_change = prices[-1] - prices[0]
            features["price_change"] = float(price_change)
            features["price_change_pct"] = float(price_change / prices[0]) if prices[0] > 0 else 0.0
        if len(timestamps) >= 2:
            time_span = (timestamps[-1] - timestamps[0]).total_seconds()
            features["events_per_second"] = float(len(events) / time_span) if time_span > 0 else 0.0
        for key in ["vol_spike", "imbalance", "price_change_pct"]:
            if key in features:
                features[key] = float(np.clip(features[key], -10, 10))
        return features

    def get_feature_names(self) -> list:
        return [
            "mean_return", "std_return", "max_return", "min_return",
            "volatility", "total_volume", "mean_volume", "max_volume",
            "vol_spike", "imbalance", "price_change", "price_change_pct",
            "events_per_second",
        ]
