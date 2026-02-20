"""Observability - metrics, logging, tracing."""

try:
    from .metrics import (
        event_latency_seconds,
        model_inference_seconds,
        anomaly_score,
        alerts_total,
        alerts_per_symbol,
        feature_drift_statistic,
        adwin_drift_events_total,
        queue_depth,
        events_processed_total,
        websocket_reconnects_total,
    )
except ImportError:
    pass  # prometheus_client not installed
