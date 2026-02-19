#!/bin/bash
set -e
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/src"
mkdir -p data
[ ! -f data/sample_trades.csv ] && python -m apps.cli.main generate-data --output data/sample_trades.csv
python -m apps.cli.main run-pipeline --data data/sample_trades.csv --speed 100 &
sleep 5
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 &
