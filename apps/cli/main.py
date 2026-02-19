"""CLI entrypoint."""

import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import random

from mip.config import settings
from mip.services.pipeline import run_pipeline


def generate_data(output: Path, num_events: int = 1000) -> None:
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    base_time = datetime.now()
    prices = {s: 100.0 + random.uniform(-10, 10) for s in symbols}
    events = []
    for i in range(num_events):
        s = random.choice(symbols)
        p = prices[s]
        if random.random() < 0.05:
            size = random.uniform(50, 100)
            change = random.uniform(-0.1, 0.1)
        else:
            size = random.uniform(0.1, 10.0)
            change = random.gauss(0, 0.01)
        p = max(0.01, p + change)
        prices[s] = p
        events.append({
            "timestamp": (base_time + pd.Timedelta(seconds=i)).isoformat(),
            "symbol": s,
            "price": p,
            "size": size,
            "side": random.choice(["buy", "sell"]),
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(events).to_csv(output, index=False)
    print(f"Saved {num_events} events to {output}")


def main():
    parser = argparse.ArgumentParser(description="Market Intelligence Platform CLI")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("generate-data", help="Generate sample data")
    gen.add_argument("--output", type=Path, default=settings.SAMPLE_DATA_PATH)
    gen.add_argument("--num-events", type=int, default=1000)

    run = sub.add_parser("run-pipeline", help="Run anomaly detection pipeline")
    run.add_argument("--data", type=Path, default=settings.SAMPLE_DATA_PATH)
    run.add_argument("--detector", choices=["isolation_forest", "online"], default="isolation_forest")
    run.add_argument("--explainer", choices=["shap", "rules"], default="shap")
    run.add_argument("--speed", type=float, default=1.0)

    args = parser.parse_args()

    if args.cmd == "generate-data":
        generate_data(args.output, args.num_events)
    elif args.cmd == "run-pipeline":
        asyncio.run(run_pipeline(
            data_path=args.data,
            detector_type=args.detector,
            explainer_type=args.explainer,
            speed=args.speed,
        ))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
