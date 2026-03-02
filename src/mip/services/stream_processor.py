"""Stream processing service for worker runtime."""

from __future__ import annotations

from pathlib import Path

from ..config import settings
from ..detection.isolation_forest import IsolationForestDetector
from ..detection.river_detector import RiverDetector
from ..detection.thresholding import StaticThreshold
from ..explainability.rule_mapper import RuleMapperExplainer
from ..explainability.shap_explainer import SHAPExplainer
from ..feature_engine.store import FeatureStore
from ..ingestion.replay import ReplayIngestion
from ..persistence.alerts_repo import AlertsRepository
from .stream_pipeline import StreamPipeline


class StreamProcessor:
    """Orchestrates streaming events through detection and alerting."""

    def __init__(
        self,
        detector_type: str = "isolation_forest",
        explainer_type: str = "shap",
        alerts_repo: AlertsRepository | None = None,
    ) -> None:
        self.detector_type = detector_type
        self.explainer_type = explainer_type
        self.alerts_repo = alerts_repo or AlertsRepository()
        self.feature_store = FeatureStore()
        self._anomaly_count = 0
        self._total = 0

        self.detector = (
            IsolationForestDetector() if detector_type == "isolation_forest" else RiverDetector()
        )
        self.threshold = (
            StaticThreshold(-0.5, "below")
            if detector_type == "isolation_forest"
            else StaticThreshold(0.5, "above")
        )
        self.explainer = RuleMapperExplainer() if explainer_type == "rules" else None

    def _on_alert(self, event, score, features, explanation) -> None:
        self._anomaly_count += 1
        self.alerts_repo.save(event.timestamp, event.symbol, score, True, features, explanation)

    async def warmup(self, ingestion: ReplayIngestion, data_path: Path, samples: int = 100) -> None:
        training = []
        async for event in ingestion.stream_from_csv(data_path):
            self.feature_store.update(event)
            f = self.feature_store.compute_features(event.symbol)
            if f:
                training.append(f)
                if len(training) >= samples:
                    break
        if not training:
            raise RuntimeError("No training features collected")
        self.detector.fit(training)
        if self.explainer is None:
            self.explainer = SHAPExplainer(
                self.detector,
                getattr(self.detector, "feature_names", None) or list(training[0].keys()),
            )

    async def run_replay(self, data_path: Path, speed: float = 1.0) -> dict[str, int]:
        ingestion = ReplayIngestion(speed_multiplier=speed)
        await self.warmup(ingestion, data_path)

        pipeline = StreamPipeline(
            feature_store=self.feature_store,
            detector=self.detector,
            threshold=self.threshold,
            explainer=self.explainer,
            on_alert=self._on_alert,
        )

        async def _counting_stream():
            async for event in ingestion.stream_from_csv(data_path):
                self._total += 1
                yield event

        await pipeline.process_stream(_counting_stream())
        return {"processed": self._total, "anomalies": self._anomaly_count}


async def run_default_worker() -> dict[str, int]:
    """Run replay worker with default settings."""
    processor = StreamProcessor(detector_type="isolation_forest", explainer_type="rules")
    return await processor.run_replay(settings.SAMPLE_DATA_PATH, speed=100.0)
