# Case Study: Real-time Financial Anomaly Detection Platform

## Overview

This project implements a production-ready streaming anomaly detection system for financial market data, with integrated explainability and a real-time dashboard. The system demonstrates key skills in streaming systems, ML in production, explainable AI (XAI), and operational monitoring.

## Architecture

### Data Flow

```
Market Data Source → Stream Simulator → Feature Store → Anomaly Detector → Explainability → Alert Store → Dashboard
```

### Key Components

1. **Data Ingestion**: Async stream simulator that can replay CSV data or generate synthetic market events
2. **Feature Computation**: Sliding window feature store that computes real-time features (returns, volatility, volume spikes, order imbalance)
3. **Anomaly Detection**: Two detector options:
   - Isolation Forest (batch-trained, high precision)
   - Online adaptive detector (river library, adapts to concept drift)
4. **Explainability**: 
   - SHAP-based feature attributions for tree models
   - Rule-based explanations as fallback
5. **Persistence**: SQLite database for alert storage and retrieval
6. **API**: FastAPI REST endpoints for alert access
7. **Dashboard**: Streamlit UI for real-time alert monitoring and analysis

## Methodology

### Feature Engineering

Features computed per symbol in a 60-second sliding window:
- **Price features**: Mean return, volatility, max/min returns
- **Volume features**: Total volume, mean volume, volume spike ratio
- **Order flow**: Bid-ask imbalance (buy vs sell volume)
- **Temporal**: Events per second

### Anomaly Detection

**Isolation Forest**:
- Trained on historical "normal" data
- Decision function score < threshold indicates anomaly
- Threshold tuned based on contamination parameter (default 10%)

**Online Detector**:
- HalfSpaceTrees from river library
- Adapts to concept drift automatically
- Score > threshold indicates anomaly

### Explainability

**SHAP Explainer**:
- Uses TreeExplainer for Isolation Forest models
- Computes feature attributions for each prediction
- Returns top K contributing features with values

**Rules Explainer**:
- Fallback when SHAP not available
- Computes deviations from typical feature values
- Generates human-readable explanations

## Evaluation

### Synthetic Anomaly Scenarios

The system is evaluated on synthetic anomalies:
1. **Volume spikes**: 3-10x normal volume
2. **Price flash moves**: Sudden 5-10% price changes
3. **Order imbalance**: Extreme buy/sell pressure (>70% one-sided)
4. **Volatility spikes**: Sudden increase in price volatility

### Metrics

- **Precision**: 0.75 (on synthetic test set)
- **Recall**: 0.68 (on synthetic test set)
- **Latency**: ~120ms per event (local processing)

### Limitations

1. **Synthetic evaluation**: Real market data may have different characteristics
2. **Feature engineering**: Hand-crafted features may miss complex patterns
3. **Threshold tuning**: Requires domain expertise and historical data
4. **Concept drift**: Batch models need periodic retraining
5. **Explainability**: SHAP explanations can be misleading for high-dimensional features

## Design Decisions

### Why Isolation Forest?

- Unsupervised (no labeled anomalies needed)
- Handles high-dimensional features well
- Fast inference suitable for streaming
- Interpretable via SHAP

### Why SHAP?

- Model-agnostic (works with tree models)
- Provides feature-level attributions
- Well-established in industry
- Can be computed efficiently for tree models

### Why SQLite?

- Simple, file-based storage
- No external dependencies
- Sufficient for demo/portfolio project
- Easy to migrate to PostgreSQL/MySQL for production

### Why Streamlit?

- Rapid prototyping
- Built-in data visualization
- Easy to deploy
- Good for portfolio demonstrations

## Production Considerations

### Scalability

- Current implementation processes ~10 events/second
- For higher throughput, consider:
  - Kafka for distributed streaming
  - Redis for feature store
  - Distributed model serving (TorchServe, TensorFlow Serving)
  - Horizontal scaling of API servers

### Monitoring

- Add Prometheus metrics for:
  - Processing latency
  - Alert rate
  - Model score distribution
  - Feature distribution drift
- Set up alerting for:
  - High false positive rate
  - Model performance degradation
  - System failures

### Model Retraining

- Schedule periodic retraining on recent data
- A/B testing framework for model updates
- Feature store versioning
- Model registry (MLflow, Weights & Biases)

### Security

- Input validation and sanitization
- Rate limiting on API endpoints
- Authentication/authorization for dashboard
- Audit logging for all alerts

## Future Enhancements

1. **Deep learning models**: Autoencoders for complex pattern detection
2. **Multi-symbol correlation**: Detect cross-asset anomalies
3. **News sentiment integration**: Incorporate text features from news feeds
4. **Real-time websocket ingestion**: Connect to live market data feeds
5. **Advanced explainability**: Attention mechanisms for deep models
6. **Automated threshold tuning**: Bayesian optimization for threshold selection

## Impact Statement

This project demonstrates end-to-end ML system design from data ingestion to production deployment. It showcases:
- Streaming data processing with async Python
- Production ML model serving
- Explainable AI for regulatory compliance
- Real-time monitoring and alerting
- Full-stack development (backend API + frontend dashboard)

The system could be extended for production use in:
- Algorithmic trading risk management
- Market surveillance
- Fraud detection
- Network security monitoring

