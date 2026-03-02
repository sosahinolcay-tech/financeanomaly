"""Microstructure feature utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from ..domain.events import MarketEvent


def compute_microprice(
    best_bid: float,
    best_ask: float,
    bid_size: float,
    ask_size: float,
) -> float:
    """Compute microprice from top-of-book quote and sizes."""
    denom = bid_size + ask_size
    if denom <= 0:
        return (best_bid + best_ask) / 2.0
    return (best_bid * ask_size + best_ask * bid_size) / denom


def compute_spread(best_bid: float, best_ask: float, relative: bool = False) -> float:
    """Compute spread (absolute or relative to midpoint)."""
    spread = max(0.0, best_ask - best_bid)
    if not relative:
        return spread
    midpoint = (best_bid + best_ask) / 2.0
    return spread / midpoint if midpoint > 0 else 0.0


def compute_order_flow_imbalance(events: Iterable[MarketEvent]) -> float:
    """Compute OFI proxy from buy/sell aggressor trade sizes."""
    buy = 0.0
    sell = 0.0
    for e in events:
        if e.side == "buy":
            buy += float(e.size)
        else:
            sell += float(e.size)
    total = buy + sell
    if total <= 0:
        return 0.0
    return (buy - sell) / total


def compute_volume_spike_ratio(current_size: float, historical_sizes: Iterable[float]) -> float:
    """Compute size spike vs trailing mean size."""
    hist = np.asarray(list(historical_sizes), dtype=float)
    baseline = float(np.mean(hist)) if hist.size else 0.0
    if baseline <= 0:
        return 0.0
    return float(current_size / baseline)


def compute_microstructure_features(
    order_book: dict,
    recent_events: Iterable[MarketEvent],
    historical_sizes: Iterable[float],
) -> dict[str, float]:
    """Compute a compact set of microstructure-aware features."""
    bid = float(order_book.get("bid", 0.0))
    ask = float(order_book.get("ask", 0.0))
    bid_size = float(order_book.get("bid_size", 0.0))
    ask_size = float(order_book.get("ask_size", 0.0))
    events = list(recent_events)
    latest_size = events[-1].size if events else 0.0

    return {
        "microprice": compute_microprice(bid, ask, bid_size, ask_size),
        "spread": compute_spread(bid, ask, relative=False),
        "relative_spread": compute_spread(bid, ask, relative=True),
        "ofi": compute_order_flow_imbalance(events),
        "volume_spike_ratio": compute_volume_spike_ratio(latest_size, historical_sizes),
    }
