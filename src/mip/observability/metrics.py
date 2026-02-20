"""Prometheus metrics for observability."""

from prometheus_client import Counter, Histogram, Gauge

# Latency & Throughput
event_latency_seconds = Histogram(
    "event_latency_seconds",
    "Time to process a single event",
    ["stage"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0],
)
model_inference_seconds = Histogram(
    "model_inference_seconds",
    "Model inference time per event",
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1],
)
events_processed_total = Counter(
    "events_processed_total",
    "Total events processed",
)
events_per_second = Gauge(
    "events_per_second",
    "Current events per second",
)

# Queue & Backpressure
queue_depth = Gauge(
    "queue_depth",
    "Current queue depth (Redis/Kafka)",
    ["queue"],
)
websocket_reconnects_total = Counter(
    "websocket_reconnects_total",
    "WebSocket reconnection count",
    ["source"],
)
dropped_events_total = Counter(
    "dropped_events_total",
    "Dropped events count",
)
backpressure_activations_total = Counter(
    "backpressure_activations_total",
    "Backpressure activation count",
)

# Detection
anomaly_score = Histogram(
    "anomaly_score",
    "Anomaly score distribution",
    ["symbol"],
    buckets=[-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0],
)
alerts_total = Counter(
    "alerts_total",
    "Total alerts created",
    ["symbol", "severity"],
)
alerts_per_symbol = Gauge(
    "alerts_per_symbol",
    "Alerts per symbol (rolling)",
    ["symbol"],
)

# Drift
feature_drift_statistic = Gauge(
    "feature_drift_statistic",
    "KS statistic or drift measure per feature",
    ["feature"],
)
adwin_drift_events_total = Counter(
    "adwin_drift_events_total",
    "ADWIN drift detection events",
)
exception_rate = Counter(
    "exception_total",
    "Exceptions by type",
    ["type"],
)
