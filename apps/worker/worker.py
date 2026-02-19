"""Stream processor worker entrypoint."""

# TODO: Run stream_processor against Kafka/WebSocket
# For now, delegates to pipeline

import asyncio
from pathlib import Path

from mip.services.pipeline import run_pipeline
from mip.config import settings


def main():
    """Run pipeline as worker (replay mode)."""
    asyncio.run(run_pipeline(
        data_path=settings.SAMPLE_DATA_PATH,
        detector_type="isolation_forest",
        explainer_type="shap",
        speed=100.0,
    ))


if __name__ == "__main__":
    main()
