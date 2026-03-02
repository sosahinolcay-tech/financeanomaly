"""Stream processor worker entrypoint."""

import asyncio

from mip.services.stream_processor import run_default_worker


def main():
    """Run the default worker process."""
    stats = asyncio.run(run_default_worker())
    print(f"Worker complete. Processed={stats['processed']}, anomalies={stats['anomalies']}")


if __name__ == "__main__":
    main()
