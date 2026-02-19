# Product Requirements Document

## Real-Time Market Microstructure Anomaly & Regime Detection Platform

> A real-time market microstructure anomaly & regime detection platform with explainable risk signals and operational monitoring.

That framing alone changes how it feels.

---

## Vision

Transform the current anomaly detection prototype into a **production-grade market intelligence system** that detects liquidity shocks, volatility regime shifts, and structural breaks using online ML, adaptive thresholding, and microstructure-aware features. Target: a legitimate portfolio flagship suitable for quant research teams at major hedge funds.

---

## Phase 1 — Remove "Toy Project" Signals

### What Makes It Look Weak

| Signal | Current State |
|--------|---------------|
| Synthetic anomaly injection | Heavy reliance on generated anomalies in CSV replay |
| Single model dominance | Isolation Forest without benchmarking |
| Static thresholding | Hardcoded `ANOMALY_THRESHOLD` |
| Limited evaluation realism | Fake labels, no real-event validation |
| No drift handling | No concept or regime change detection |
| No economic interpretation | Generic "anomaly" without market context |

---

## Phase 2 — Make It Real

### 1. Use Real Streaming Data (No Synthetic Labeling)

**Replace:** CSV replay with injected anomalies

**With:** Live exchange feeds

| Source | Asset Class | Data |
|--------|-------------|------|
| Binance WebSocket | Crypto (BTC/ETH perpetuals) | Trades, order book snapshots |
| Polygon.io | Equities | Trade stream |
| Alpaca | Equities | Trade stream |

**Focus on:**
- Trades (price, size, side)
- Order book snapshots
- Volume, spread, trade direction (buy/sell aggressor)

**Pipeline:**
```
Live exchange → Feature extraction → Online anomaly scoring → Alert system
```

Anomalies become **naturally occurring market events**, not injected.

---

### 2. Upgrade: Multi-Signal Risk Scoring

**Replace:** Single anomaly detector

**With:** Multi-model risk engine

| Component | Implementation |
|-----------|----------------|
| **A. Statistical Signals** | Z-score volume surge, realized volatility spike, order book imbalance, microprice shift |
| **B. Online ML Detector** | River HalfSpaceTrees, AdaptiveRandomForest, Online Autoencoder |
| **C. Regime Detection** | HMM, Bayesian Change Point, ADWIN drift detection |

**Detect:**
- Liquidity shocks
- Regime transitions
- Structural breaks
- Flash crash conditions

---

### 3. Market Microstructure Intelligence

**Replace:** Generic features (`mean_return`, `volatility`)

**With:** Microstructure-aware features

| Feature | Description |
|---------|-------------|
| Microprice | Weighted mid using order book (bid/ask depth) |
| Order Flow Imbalance (OFI) | Buy vs sell aggressor imbalance |
| VPIN-like toxicity | Trade imbalance toxicity metric |
| Spread widening | Bid-ask spread dynamics |
| Trade clustering bursts | Temporal clustering of trades |

---

### 4. Adaptive Scoring (Replace Static Thresholds)

**Replace:** `threshold = -0.5` (hardcoded)

**With:**
```python
dynamic_threshold = rolling_quantile(score, 0.99)
# or
EWMA baseline
# or
Adaptive threshold using percentile bands
```

---

### 5. Explainability That Actually Impresses

**Replace:** SHAP-only attribution

**Add:**
- Feature contribution waterfall chart
- **Counterfactual explanation:** *"If volume were within 1.2x baseline, this would not trigger."*
- Model confidence interval
- **Historical similarity retrieval:** *"Similar anomaly occurred at 14:32 during CPI release."*

---

### 6. Drift Monitoring

| What to Track | Action on Drift |
|---------------|-----------------|
| Feature distribution shift (KS test) | Retrain trigger |
| Population stability index | Alert calibration |
| Alert frequency shift | Model health check |
| Score distribution shift | Threshold recalibration |

---

### 7. Operational Hardening

**Observability:**
- Prometheus metrics: latency/event, queue depth, alert rate, inference time
- Grafana dashboard

**Resilience:**
- Retry logic
- Backpressure handling
- Graceful WebSocket reconnect
- Circuit breaker pattern

---

### 8. Real Evaluation (Replace Synthetic)

**Replace:** Fake labeled anomalies

**With:**
- Historical known events (FOMC, CPI, ETF approval)
- Anomaly score vs realized volatility spike
- **Backtest:** Did anomaly score predict large move in next 30 seconds?
- Precision@K for top anomaly windows

---

## Phase 3 — Research Artifact

### Research Notebook
- Compare Isolation Forest vs River vs Autoencoder
- Compare static vs adaptive threshold
- ROC / PR curves
- Drift impact analysis
- Latency benchmarks

### Case Study Document
- Failure modes
- False positive types
- Regime dependency
- Data leakage risks
- Explainability limitations

---

## Phase 4 — One Advanced Feature

Pick **one** to differentiate:

| Option | Description |
|--------|-------------|
| **A. Cross-Asset Correlation Shock** | Detect when BTC and ETH decouple unexpectedly |
| **B. News-Conditioned Detection** | FinBERT sentiment to condition anomaly score |
| **C. Order Book Stress Testing** | Replay historical crash, show detection behavior |
| **D. Anomaly Clustering** | Cluster into types: liquidity shock, momentum ignition, volatility compression break, toxic flow spike |

---

## Target Architecture

```
Live Exchange Feed
        ↓
Async Ingestion Layer
        ↓
Feature Engine (microstructure aware)
        ↓
Multi-Model Risk Engine
   ├── Statistical Signals
   ├── Online ML
   ├── Drift Detector
   └── Regime Classifier
        ↓
Explainability Layer
   ├── SHAP
   ├── Rule mapping
   ├── Counterfactual
        ↓
Alert Service
        ↓
Dashboard + Metrics + Storage
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Latency per event | < 200ms |
| Architecture | Modular, dependency inversion |
| Test coverage | Unit + integration |
| Deployment | Dockerized |
| Monitoring | Prometheus + Grafana |

---

## Resume Evolution

**Before:**
> Engineered streaming ML pipeline for real-time anomaly detection in market data

**After:**
> Designed and deployed a production-grade real-time market surveillance system detecting liquidity shocks, volatility regime shifts, and structural breaks using online ML (River), adaptive thresholding, and microstructure-aware features; integrated SHAP-based and counterfactual explanations with live observability (Prometheus/Grafana).

---

## Appendix: Master Cursor Prompt

```
You are a senior distributed systems + quantitative ML engineer helping me transform a real-time financial anomaly detection project into a production-grade market intelligence system.

Goals:
- Replace synthetic anomaly injection with live exchange data ingestion (Binance websocket)
- Implement microstructure-aware feature computation (microprice, OFI, spread, volatility clustering)
- Add adaptive thresholding and drift detection (ADWIN or KS-based monitoring)
- Integrate an online anomaly model using River
- Implement model benchmarking framework comparing IsolationForest vs River vs Autoencoder
- Add explainability layer with SHAP + rule mapping + counterfactual explanation
- Improve architecture for resilience, observability, and latency under 200ms per event
- Add Prometheus metrics and structured logging
- Refactor codebase to enforce modular design and dependency inversion

Constraints:
- Async-first architecture
- Clean separation between ingestion, feature store, models, and explainability
- Full unit and integration tests
- Dockerized
- Production-quality logging and monitoring

Deliverables:
- Refactored architecture
- Production-ready pipeline
- Evaluation notebook with real market data
- Monitoring dashboard
- Clean README with architecture diagram and metrics

Write code that prioritizes:
- Readability
- Extensibility
- Performance
- Proper error handling
- Type hints

Think like you're building for a quant research team at a major hedge fund.
```

---

## Elite Tier Checklist

If you implement:
- [ ] Online learning
- [ ] Drift detection
- [ ] Microstructure features
- [ ] Real data (no synthetic injection)
- [ ] Adaptive thresholds
- [ ] Observability (Prometheus/Grafana)
- [ ] Counterfactual explanations

**This becomes:** *Real-time market surveillance & regime detection engine*

That is no longer a class project.  
That's a legitimate portfolio flagship.
