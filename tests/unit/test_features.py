"""Unit tests for feature computation."""

import pytest
from datetime import datetime, timedelta
from src.ap.ingest.simulator import MarketEvent
from src.ap.processing.features import FeatureStore


def test_feature_store_update():
    """Test feature store updates correctly."""
    store = FeatureStore(window_seconds=60)
    
    event = MarketEvent(
        timestamp=datetime.now(),
        symbol="AAPL",
        price=100.0,
        size=1.0,
        side="buy"
    )
    
    store.update(event)
    assert "AAPL" in store.events
    assert len(store.events["AAPL"]) == 1


def test_feature_computation():
    """Test feature computation with multiple events."""
    store = FeatureStore(window_seconds=60)
    
    base_time = datetime.now()
    
    # Add multiple events
    for i in range(10):
        event = MarketEvent(
            timestamp=base_time + timedelta(seconds=i),
            symbol="AAPL",
            price=100.0 + i * 0.1,
            size=1.0 + i * 0.1,
            side="buy" if i % 2 == 0 else "sell"
        )
        store.update(event)
    
    features = store.compute_features("AAPL")
    
    assert "mean_return" in features
    assert "vol_spike" in features
    assert "imbalance" in features
    assert len(features) > 0


def test_feature_store_min_events():
    """Test that features require minimum events."""
    store = FeatureStore(window_seconds=60)
    
    event = MarketEvent(
        timestamp=datetime.now(),
        symbol="AAPL",
        price=100.0,
        size=1.0,
        side="buy"
    )
    
    store.update(event)
    features = store.compute_features("AAPL")
    
    # Should return empty dict if not enough events
    assert features == {}

