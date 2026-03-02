"""StreamPipeline - orchestrates ingest → feature_engine → detection → explain → alert."""

from typing import Callable, AsyncIterator

from ..domain.events import MarketEvent
from ..feature_engine.store import FeatureStore
from ..detection.base import Detector
from ..detection.thresholding import ThresholdStrategy
from ..explainability.shap_explainer import SHAPExplainer
from ..explainability.rule_mapper import RuleMapperExplainer


class StreamPipeline:
    """
    Orchestration layer. Depends on:
    - ingestion (async iterator of MarketEvent)
    - feature_engine (FeatureStore)
    - detection (Detector + ThresholdStrategy)
    - explainability (SHAP or rules)
    - alert persistence (callable)
    """

    def __init__(
        self,
        feature_store: FeatureStore,
        detector: Detector,
        threshold: ThresholdStrategy,
        explainer: SHAPExplainer | RuleMapperExplainer,
        on_alert: Callable,
    ):
        self.feature_store = feature_store
        self.detector = detector
        self.threshold = threshold
        self.explainer = explainer
        self.on_alert = on_alert

    async def process_stream(self, events: AsyncIterator[MarketEvent]) -> None:
        """Process event stream: update features, score, threshold, explain, alert."""
        async for event in events:
            self.feature_store.update(event)
            f = self.feature_store.compute_features(event.symbol)
            if not f:
                continue
            score = self.detector.score(f)
            if self.threshold.is_anomaly(score):
                expl = (
                    self.explainer.explain(f)
                    if isinstance(self.explainer, SHAPExplainer)
                    else self.explainer.explain(f, score)
                )
                self.on_alert(event, score, f, expl)
