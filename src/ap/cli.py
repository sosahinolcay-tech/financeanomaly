"""Command-line interface for the anomaly platform."""

import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import random

from .ingest.simulator import StreamSimulator, MarketEvent
from .processing.features import FeatureStore
from .models.isolation_forest import IsolationForestDetector
from .models.online_detector import OnlineDetector
from .explain.shap_explainer import SHAPExplainer
from .explain.rules_explainer import RulesExplainer
from .persistence.store import AlertStore
from .utils.config import settings


async def run_pipeline(
    data_path: Path,
    detector_type: str = "isolation_forest",
    explainer_type: str = "shap",
    speed: float = 1.0
):
    """
    Run the anomaly detection pipeline.
    
    Args:
        data_path: Path to CSV data file
        detector_type: "isolation_forest" or "online"
        explainer_type: "shap" or "rules"
        speed: Stream speed multiplier
    """
    print(f"Starting anomaly detection pipeline...")
    print(f"Data: {data_path}")
    print(f"Detector: {detector_type}")
    print(f"Explainer: {explainer_type}")
    
    # Initialize components
    simulator = StreamSimulator(speed_multiplier=speed)
    feature_store = FeatureStore()
    alert_store = AlertStore()
    
    # Initialize detector
    if detector_type == "isolation_forest":
        detector = IsolationForestDetector()
    else:
        detector = OnlineDetector()
    
    # Initialize explainer
    if explainer_type == "shap":
        explainer = None  # Will be initialized after detector is fitted
    else:
        explainer = RulesExplainer()
    
    # Collect initial features for training
    print("Collecting training data...")
    training_features = []
    event_count = 0
    training_events = 100  # Number of events to use for training
    
    async for event in simulator.simulate_from_csv(data_path):
        feature_store.update(event)
        features = feature_store.compute_features(event.symbol)
        
        if features:
            training_features.append(features)
            event_count += 1
            
            if event_count >= training_events:
                break
    
    if not training_features:
        print("Error: No features collected for training")
        return
    
    # Train detector
    print(f"Training detector on {len(training_features)} samples...")
    detector.fit(training_features)
    
    # Initialize SHAP explainer if needed
    if explainer_type == "shap":
        if hasattr(detector, 'feature_names') and detector.feature_names:
            feature_names = detector.feature_names
        else:
            # Fallback: use feature names from first training sample
            feature_names = sorted(list(training_features[0].keys()))
        explainer = SHAPExplainer(detector, feature_names)
    
    print("Pipeline ready. Processing events...")
    
    # Process remaining events
    anomaly_count = 0
    total_processed = 0
    
    async for event in simulator.simulate_from_csv(data_path):
        feature_store.update(event)
        features = feature_store.compute_features(event.symbol)
        
        if not features:
            continue
        
        total_processed += 1
        
        # Score and detect
        try:
            score = detector.score(features)
            is_anomaly = detector.is_anomaly(features)
            
            if is_anomaly:
                anomaly_count += 1
                
                # Generate explanation
                if explainer_type == "shap":
                    explanation = explainer.explain(features)
                else:
                    explanation = explainer.explain(features, score)
                
                # Save alert
                alert_id = alert_store.save_alert(
                    timestamp=event.timestamp,
                    symbol=event.symbol,
                    anomaly_score=score,
                    is_anomaly=True,
                    features=features,
                    explanation=explanation
                )
                
                print(f"[ALERT #{alert_id}] {event.symbol} @ {event.timestamp} "
                      f"Score: {score:.3f} - {explanation.get('reason', 'N/A')}")
        
        except Exception as e:
            print(f"Error processing event: {e}")
            continue
        
        if total_processed % 100 == 0:
            print(f"Processed {total_processed} events, {anomaly_count} anomalies detected")
    
    print(f"\nPipeline complete!")
    print(f"Total events processed: {total_processed}")
    print(f"Anomalies detected: {anomaly_count}")
    print(f"Alerts saved to: {alert_store.db_path}")


def generate_sample_data(output_path: Path, num_events: int = 1000):
    """
    Generate sample market data with some anomalies.
    
    Args:
        output_path: Path to save CSV file
        num_events: Number of events to generate
    """
    print(f"Generating {num_events} sample events...")
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    events = []
    
    base_time = datetime.now()
    base_prices = {symbol: 100.0 + random.uniform(-10, 10) for symbol in symbols}
    
    for i in range(num_events):
        symbol = random.choice(symbols)
        base_price = base_prices[symbol]
        
        # Occasionally inject anomalies
        if random.random() < 0.05:  # 5% anomaly rate
            # Volume spike
            size = random.uniform(50, 100)
            price_change = random.uniform(-0.1, 0.1)
        else:
            size = random.uniform(0.1, 10.0)
            price_change = random.gauss(0, 0.01)
        
        new_price = max(0.01, base_price + price_change)
        base_prices[symbol] = new_price
        
        events.append({
            "timestamp": (base_time + pd.Timedelta(seconds=i)).isoformat(),
            "symbol": symbol,
            "price": new_price,
            "size": size,
            "side": random.choice(["buy", "sell"])
        })
    
    df = pd.DataFrame(events)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Sample data saved to {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Anomaly Detection Platform CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate data command
    gen_parser = subparsers.add_parser("generate-data", help="Generate sample data")
    gen_parser.add_argument("--output", type=Path, default=settings.SAMPLE_DATA_PATH,
                          help="Output CSV path")
    gen_parser.add_argument("--num-events", type=int, default=1000,
                          help="Number of events to generate")
    
    # Run pipeline command
    run_parser = subparsers.add_parser("run-pipeline", help="Run anomaly detection pipeline")
    run_parser.add_argument("--data", type=Path, default=settings.SAMPLE_DATA_PATH,
                          help="Input CSV data path")
    run_parser.add_argument("--detector", choices=["isolation_forest", "online"],
                          default="isolation_forest", help="Detector type")
    run_parser.add_argument("--explainer", choices=["shap", "rules"],
                          default="shap", help="Explainer type")
    run_parser.add_argument("--speed", type=float, default=1.0,
                          help="Stream speed multiplier")
    
    args = parser.parse_args()
    
    if args.command == "generate-data":
        generate_sample_data(args.output, args.num_events)
    elif args.command == "run-pipeline":
        asyncio.run(run_pipeline(
            args.data,
            detector_type=args.detector,
            explainer_type=args.explainer,
            speed=args.speed
        ))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

