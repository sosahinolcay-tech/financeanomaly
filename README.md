# Real-Time Market Intelligence & Anomaly Detection System

Production-grade streaming market surveillance engine for detecting liquidity shocks, volatility regime shifts, and structural anomalies in real time using adaptive ML and explainable AI.

## Overview

This system ingests live market data (trades, order book updates), computes microstructure-aware features, applies online anomaly detection and regime modeling, and surfaces explainable alerts via a live dashboard.

Designed to demonstrate:

- Streaming systems engineering
- Online ML in production
- Adaptive thresholding
- Drift detection
- Explainable AI (SHAP + counterfactuals)
- Observability & monitoring
- Production deployment patterns

## Architecture

```
Exchange Websocket
        ↓
Async Ingestion Layer
        ↓
Feature Engine (microstructure-aware)
        ↓
Multi-Model Detection Engine
   ├── Statistical Signals
   ├── Online ML (River)
   ├── Autoencoder
   └── Drift Monitor (ADWIN / KS)
        ↓
Explainability Layer
   ├── SHAP attribution
   ├── Rule mapping
   ├── Counterfactual reasoning
        ↓
Alert Service
        ↓
API + Dashboard
        ↓
Prometheus + Grafana
```

## Core Capabilities

### Real-Time Ingestion

- Binance / Alpaca websocket connectors
- Async event-driven architecture
- Reconnection and backpressure handling

### Microstructure Feature Engine

- Log returns
- Realized volatility
- Order Flow Imbalance (OFI)
- Microprice
- Spread widening
- Volume spike ratio
- Regime indicators

### Detection Engine

- Isolation Forest (batch baseline)
- River HalfSpaceTrees (online)
- AdaptiveRandomForest
- Online Autoencoder
- Ensemble scoring
- Dynamic percentile-based thresholding

### Drift Detection

- ADWIN
- KS-test distribution monitoring
- Population Stability Index (PSI)
- Alert-rate drift

### Explainability

- SHAP feature attribution
- Rule-based semantic explanation
- Counterfactual reasoning
- Historical similarity search

### Observability

- Prometheus metrics:
  - Event latency
  - Model inference time
  - Alert frequency
  - Score distribution
- Grafana dashboards
- Structured JSON logging

## Evaluation

Evaluation is performed on:

- Real market volatility events
- Precision@K on forward volatility spikes
- Score-to-future-move correlation
- Latency benchmarks (<200ms per event target)

Research artifacts are in:

- `research/benchmarking/`

## Running Locally

```bash
# Install deps and generate data
make install
make data

# Run pipeline (populates alerts DB)
make pipeline

# Start API (terminal 1)
make dev

# Start dashboard (terminal 2)
make dashboard
```

Or with Docker:

```bash
docker-compose -f docker/docker-compose.yml up --build
```

**Services:**

| Service    | URL                     |
|-----------|-------------------------|
| API       | http://localhost:8000   |
| Dashboard | http://localhost:8501   |
| Prometheus| http://localhost:9090    |
| Grafana   | http://localhost:3000    |

## Configuration

All runtime behavior is configurable via:

- `configs/`

Environment overrides supported.

## Testing

```bash
make test
```

Includes:

- Unit tests
- Integration tests
- Performance tests
- Deterministic replay tests

## Production Design Principles

- Async-first architecture
- Modular detection engine
- Dependency inversion
- Config-driven runtime
- Observability by default
- Deterministic replay for audit
- Reproducible Docker builds

## Tech Stack

- Python 3.10+
- asyncio
- FastAPI
- River
- scikit-learn
- PyTorch
- SHAP
- Redis
- Prometheus
- Grafana
- Docker
- GitHub Actions

## Portfolio Impact

This system demonstrates:

- End-to-end ML system design
- Real-time stream processing
- Online learning under concept drift
- Explainable AI for high-stakes domains
- Production-grade observability
