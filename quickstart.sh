#!/bin/bash
# Quick start script for the anomaly platform

set -e

echo "🚀 Starting Anomaly Detection Platform..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.10+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Generate sample data if it doesn't exist
if [ ! -f "data/sample_trades.csv" ]; then
    echo "📊 Generating sample data..."
    python -m src.ap.cli generate-data --output data/sample_trades.csv --num-events 1000
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the pipeline:"
echo "  python -m src.ap.cli run-pipeline --data data/sample_trades.csv"
echo ""
echo "To start the API server (in another terminal):"
echo "  uvicorn src.ap.api.server:app --host 0.0.0.0 --port 8000"
echo ""
echo "To start the dashboard (in another terminal):"
echo "  streamlit run src/ap/ui/dashboard.py"
echo ""

