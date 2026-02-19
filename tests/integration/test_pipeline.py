"""Integration tests for pipeline."""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime
import pandas as pd
import tempfile

from mip.domain.events import MarketEvent
from mip.ingestion.replay import ReplayIngestion
from mip.feature_engine.store import FeatureStore
from mip.detection.isolation_forest import IsolationForestDetector
from mip.persistence.alerts_repo import AlertsRepository


@pytest.mark.asyncio
async def test_end_to_end():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        base = datetime.now()
        df = pd.DataFrame([
            {"timestamp": (base + pd.Timedelta(seconds=i)).isoformat(), "symbol": "TEST", "price": 100.0 + i * 0.1, "size": 1.0, "side": "buy"}
            for i in range(50)
        ])
        df.to_csv(f.name, index=False)
        path = Path(f.name)

    db_path = Path(tempfile.mktemp(suffix=".db"))
    try:
        ingestion = ReplayIngestion(speed_multiplier=100.0)
        store = FeatureStore()
        detector = IsolationForestDetector()
        repo = AlertsRepository(db_path=db_path)

        training = []
        async for event in ingestion.stream_from_csv(path):
            store.update(event)
            f = store.compute_features(event.symbol)
            if f:
                training.append(f)
                if len(training) >= 20:
                    break

        assert len(training) > 0
        detector.fit(training)

        anomaly_count = 0
        async for event in ingestion.stream_from_csv(path):
            store.update(event)
            f = store.compute_features(event.symbol)
            if f:
                try:
                    score = detector.score(f)
                    if detector.is_anomaly(f):
                        anomaly_count += 1
                        repo.save(event.timestamp, event.symbol, score, True, f, {"reason": "test"})
                except Exception:
                    pass

        alerts = repo.get_recent(limit=100)
        assert len(alerts) == anomaly_count
    finally:
        path.unlink(missing_ok=True)
        db_path.unlink(missing_ok=True)
