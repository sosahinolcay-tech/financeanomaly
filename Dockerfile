FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY notebooks/ ./notebooks/

# Generate sample data for pipeline
ENV PYTHONPATH=/app
RUN python -m src.ap.cli generate-data --output data/sample_trades.csv --num-events 500

# Expose ports
EXPOSE 8000 8501

# Run pipeline (populates DB), then start API server
CMD ["sh", "-c", "python -m src.ap.cli run-pipeline --data data/sample_trades.csv --speed 100 && exec uvicorn src.ap.api.server:app --host 0.0.0.0 --port 8000"]

