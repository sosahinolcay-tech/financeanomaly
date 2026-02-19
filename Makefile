.PHONY: dev test lint install

# Default: run API (run dashboard separately: make dashboard)
dev:
	@mkdir -p data
	@echo "Start API: uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"
	@echo "Start Dashboard: streamlit run apps/dashboard/app.py --server.port 8501"
	uvicorn apps.api.main:app --host 0.0.0.0 --port 8000

# Run tests
test:
	PYTHONPATH=.:src pytest tests/ -v --tb=short

# Run dashboard (separate terminal)
dashboard:
	streamlit run apps/dashboard/app.py --server.port 8501

# Install deps
install:
	pip install -r requirements.txt
	pip install -e .

# Generate sample data
data:
	python -m apps.cli.main generate-data --output data/sample_trades.csv

# Run pipeline
pipeline:
	python -m apps.cli.main run-pipeline --data data/sample_trades.csv --speed 100

# Docker Compose
docker:
	docker-compose -f docker/docker-compose.yml up --build
