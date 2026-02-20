"""Pipeline orchestration."""

import time
from pathlib import Path

from ..config import settings
from ..ingestion.replay import ReplayIngestion
from ..feature_engine.store import FeatureStore
from ..detection.isolation_forest import IsolationForestDetector
from ..detection.river_detector import RiverDetector
from ..detection.thresholding import StaticThreshold, ThresholdStrategy
from ..explainability.shap_explainer import SHAPExplainer
from ..explainability.rule_mapper import RuleMapperExplainer
from ..persistence.alerts_repo import AlertsRepository

try:
    from ..observability.metrics import (
        event_latency_seconds,
        model_inference_seconds,
        anomaly_score as anomaly_score_metric,
        alerts_total as alerts_total_counter,
        events_processed_total,
    )
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False


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
    threshold_strategy: ThresholdStrategy = (
        StaticThreshold(-0.5, "below") if detector_type == "isolation_forest"
        else StaticThreshold(0.5, "above")
    )
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
        t0 = time.perf_counter() if METRICS_ENABLED else None
        try:
            score = detector.score(f)
            is_anomaly = threshold_strategy.is_anomaly(score)
            if METRICS_ENABLED:
                model_inference_seconds.observe(time.perf_counter() - t0)
                event_latency_seconds.labels(stage="full").observe(time.perf_counter() - t0)
                anomaly_score_metric.labels(symbol=event.symbol).observe(score)
            if is_anomaly:
                anomaly_count += 1
                if METRICS_ENABLED:
                    alerts_total_counter.labels(symbol=event.symbol, severity="anomaly").inc()
                expl = explainer.explain(f) if isinstance(explainer, SHAPExplainer) else explainer.explain(f, score)
                aid = alerts_repo.save(
                    event.timestamp, event.symbol, score, True, f, expl
                )
                print(f"[ALERT #{aid}] {event.symbol} @ {event.timestamp} Score: {score:.3f}")
        except Exception as e:
            print(f"Error: {e}")
        if METRICS_ENABLED:
            events_processed_total.inc()
        if total % 100 == 0:
            print(f"Processed {total}, anomalies: {anomaly_count}")

    print(f"Done. Total: {total}, Anomalies: {anomaly_count}")
