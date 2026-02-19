"""Configuration management."""

from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings  # type: ignore


class Settings(BaseSettings):
    """Application settings."""

    # Data paths
    DATA_DIR: Path = Path("data")
    SAMPLE_DATA_PATH: Path = DATA_DIR / "sample_trades.csv"

    # Feature computation
    FEATURE_WINDOW_SIZE: int = 60
    MIN_EVENTS_FOR_FEATURES: int = 2

    # Anomaly detection
    ANOMALY_THRESHOLD: float = -0.5
    ISOLATION_FOREST_N_ESTIMATORS: int = 100
    ISOLATION_FOREST_CONTAMINATION: float = 0.1

    # Online detector
    ONLINE_DETECTOR_THRESHOLD: float = 0.5
    ONLINE_DETECTOR_N_TREES: int = 10

    # Explainability
    SHAP_TOP_K_FEATURES: int = 3

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Dashboard
    DASHBOARD_PORT: int = 8501

    # Persistence
    DB_PATH: Path = DATA_DIR / "alerts.db"

    # Streaming
    STREAM_SPEED_MULTIPLIER: float = 1.0

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
