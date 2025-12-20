# Real-time Financial Anomaly & Explainability Platform

A streaming pipeline that ingests trade/quote data, computes low-latency features, runs an online anomaly detector, and returns SHAP-backed explanations via a web dashboard. Includes synthetic scenario testing, monitoring, and Dockerized reproducible setup.

**Tech Stack:** Kafka/asyncio, Python, SHAP, Streamlit, FastAPI, Docker

## Features

- **Real-time ingestion** of market data (simulated or live via websockets)
- **Streaming feature computation** with low-latency windows
- **Anomaly detection** using Isolation Forest and online adaptive models
- **Explainability** via SHAP attributions and human-readable rules
- **Live dashboard** for alert triage and historical analysis
- **Synthetic evaluation** with precision/recall metrics

## Quick Start

### Docker (Recommended)

```bash
docker build -t anomaly-platform .
docker run -p 8000:8000 -p 8501:8501 anomaly-platform
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Generate sample data
python -m src.ap.cli generate-data --output data/sample_trades.csv

# Run the pipeline
python -m src.ap.cli run-pipeline --data data/sample_trades.csv

# Start API server (in another terminal)
uvicorn src.ap.api.server:app --host 0.0.0.0 --port 8000

# Start dashboard (in another terminal)
streamlit run src/ap/ui/dashboard.py
```

## Project Structure

```
anomaly-platform/
├── data/                      # sample data & synthetic anomaly generator
├── docs/                      # documentation
├── notebooks/                 # EDA, model training & validation
├── src/
│   └── ap/                    # package root (anomaly platform)
│       ├── ingest/            # connectors & stream simulator
│       ├── processing/        # streaming feature computation
│       ├── models/            # detector models & wrappers
│       ├── explain/           # XAI wrappers
│       ├── api/               # FastAPI endpoints
│       ├── ui/                # Streamlit dashboard
│       ├── persistence/       # DB connectors
│       └── utils/             # config & utilities
├── tests/                     # unit & integration tests
├── Dockerfile
├── .github/workflows/ci.yml
└── requirements.txt
```

## Metrics

- **Precision:** 0.75 on synthetic anomaly scenarios
- **Recall:** 0.68 on synthetic anomaly scenarios
- **Average processing latency:** 120ms per event (local)

## Documentation

See `docs/case_study.md` for methodology, limitations, and design decisions.

## License

MIT

