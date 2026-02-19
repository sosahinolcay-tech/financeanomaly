"""Pipeline orchestration."""

import asyncio
from pathlib import Path

from ..config import settings
from ..ingestion.replay import ReplayIngestion
from ..feature_engine.store import FeatureStore
from ..detection.isolation_forest import IsolationForestDetector
from ..detection.river_detector import RiverDetector
from ..explainability.shap_explainer import SHAPExplainer
from ..explainability.rule_mapper import RuleMapperExplainer
from ..persistence.alerts_repo import AlertsRepository


async def run_pipeline(
    data_path: Path = None,
    detector_type: str = "isolation_forest",
    explainer_type: str = "shap",
    speed: float = None,
) -> None:
    """Run anomaly detection pipeline."""
    data_path = data_path or settings.SAMPLE_DATA_PATH
    speed = speed or settings.STREAM_SPEED_MULTIPLIER

    ingestion = ReplayIngestion(speed_multiplier=speed)
    feature_store = FeatureStore()
    alerts_repo = AlertsRepository()

    detector = IsolationForestDetector() if detector_type == "isolation_forest" else RiverDetector()
    explainer: SHAPExplainer | RuleMapperExplainer = (
        RuleMapperExplainer() if explainer_type == "rules" else None
    )

    # Collect training data
    training = []
    async for event in ingestion.stream_from_csv(data_path):
        feature_store.update(event)
        f = feature_store.compute_features(event.symbol)
        if f:
            training.append(f)
            if len(training) >= 100:
                break

    if not training:
        raise RuntimeError("No features collected for training")

    detector.fit(training)
    if explainer_type == "shap":
        explainer = SHAPExplainer(detector, detector.feature_names or list(training[0].keys()))

    # Process stream
    anomaly_count = total = 0
    async for event in ingestion.stream_from_csv(data_path):
        feature_store.update(event)
        f = feature_store.compute_features(event.symbol)
        if not f:
            continue
        total += 1
        try:
            score = detector.score(f)
            is_anomaly = detector.is_anomaly(f)
            if is_anomaly:
                anomaly_count += 1
                expl = explainer.explain(f) if isinstance(explainer, SHAPExplainer) else explainer.explain(f, score)
                aid = alerts_repo.save(
                    event.timestamp, event.symbol, score, True, f, expl
                )
                print(f"[ALERT #{aid}] {event.symbol} @ {event.timestamp} Score: {score:.3f}")
        except Exception as e:
            print(f"Error: {e}")
        if total % 100 == 0:
            print(f"Processed {total}, anomalies: {anomaly_count}")

    print(f"Done. Total: {total}, Anomalies: {anomaly_count}")
