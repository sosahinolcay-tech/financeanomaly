"""Alert service - orchestration of scoring, explanation, persistence."""

from datetime import datetime
from typing import Any, Dict

from ..detection.base import BaseDetector
from ..explainability.shap_explainer import SHAPExplainer
from ..explainability.rule_mapper import RuleMapperExplainer
from ..persistence.alerts_repo import AlertsRepository


class AlertService:
    """Creates and persists alerts."""

    def __init__(self, alerts_repo: AlertsRepository):
        self.repo = alerts_repo

    def create_alert(
        self,
        timestamp: datetime,
        symbol: str,
        score: float,
        is_anomaly: bool,
        features: Dict[str, float],
        detector: BaseDetector,
        explainer: SHAPExplainer | RuleMapperExplainer,
    ) -> int:
        if isinstance(explainer, SHAPExplainer):
            explanation = explainer.explain(features)
        else:
            explanation = explainer.explain(features, score)
        return self.repo.save(timestamp, symbol, score, is_anomaly, features, explanation)
