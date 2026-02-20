# Architecture

## Clean Layered Design

```
                    ┌────────────────────────────┐
                    │        Exchange APIs       │
                    │  (Binance / Alpaca WS)     │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Ingestion Layer        │
                    │ Async WS Clients + Retry   │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Stream Processor       │
                    │  Event Normalization       │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Feature Engine         │
                    │ Microstructure + Rolling   │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │     Detection Engine       │
                    │ Ensemble + Adaptive Thresh │
                    └──────────────┬─────────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 ▼                                   ▼
     ┌─────────────────────┐            ┌─────────────────────┐
     │ Drift Monitoring     │            │ Explainability       │
     │ ADWIN / KS / PSI     │            │ SHAP + Counterfactual│
     └─────────────┬───────┘            └─────────────┬───────┘
                   │                                     │
                   └──────────────┬──────────────────────┘
                                  ▼
                    ┌────────────────────────────┐
                    │       Alert Service        │
                    │ Persistence + Routing      │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │ API + Dashboard            │
                    └──────────────┬─────────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │ Observability Layer        │
                    │ Prometheus + Grafana       │
                    └────────────────────────────┘
```

## Dependency Direction

```
domain           (pure objects, no infra)
   ↑
feature_engine   (uses MarketEvent → FeatureVector)
   ↑
detection        (uses FeatureVector → score)
   ↑
services         (orchestrates ingest → features → detect → explain → alert)
   ↑
apps             (entrypoints: API, dashboard, worker, CLI)
```

## Module Boundaries

| Layer | Contents | Depends On |
|-------|----------|------------|
| **domain** | MarketEvent, FeatureVector, AnomalyScore | nothing |
| **feature_engine** | FeatureStore, microstructure | domain |
| **detection** | Detector protocol, IsolationForest, River, ThresholdStrategy | domain |
| **explainability** | SHAP, rule mapper, counterfactual | domain, detection |
| **services** | StreamPipeline, pipeline orchestration | all above |
| **apps** | FastAPI, Streamlit, CLI | services |

## Grafana Dashboards

Provisioned in `infrastructure/grafana/dashboards/`:

1. **System Health** — Latency p50/p95/p99, events/s, model inference, queue depth, reconnects, errors
2. **Detection Intelligence** — Anomaly score time series, score distribution, threshold vs score, alerts/min, alerts per symbol
3. **Drift Monitoring** — Feature drift (KS), PSI, ADWIN timeline, alert-rate shift
4. **Market Intelligence** — Price + anomaly markers, realized vol, OFI heatmap, regime timeline

## Prometheus Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `event_latency_seconds` | Histogram | Per-event processing latency |
| `model_inference_seconds` | Histogram | Model inference time |
| `anomaly_score` | Histogram | Score distribution by symbol |
| `alerts_total` | Counter | Alerts by symbol/severity |
| `alerts_per_symbol` | Gauge | Rolling alerts per symbol |
| `feature_drift_statistic` | Gauge | KS/PSI per feature |
| `adwin_drift_events_total` | Counter | ADWIN drift triggers |
| `queue_depth` | Gauge | Queue depth |
