FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY apps/ ./apps/
COPY configs/ ./configs/
COPY data/ ./data/
ENV PYTHONPATH=/app:/app/src
RUN python -m apps.cli.main generate-data --output data/sample_trades.csv --num-events 500
CMD ["python", "-m", "apps.cli.main", "run-pipeline", "--data", "data/sample_trades.csv", "--speed", "100"]
