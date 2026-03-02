"""Configuration management."""

from pathlib import Path
from typing import Any, get_type_hints
import os

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # pydantic v1 fallback
    try:
        from pydantic import BaseSettings  # type: ignore
    except Exception:
        # Lightweight fallback so local runs/tests don't hard-fail when
        # pydantic-settings is missing in the active environment.
        class BaseSettings:  # type: ignore
            """Minimal BaseSettings-compatible fallback."""

            def __init__(self, **overrides: Any) -> None:
                hints = get_type_hints(self.__class__)
                for key, typ in hints.items():
                    if key.startswith("_"):
                        continue
                    default = getattr(self.__class__, key, None)
                    raw = overrides.get(key, os.getenv(key, default))
                    setattr(self, key, self._coerce(raw, typ))

            @staticmethod
            def _coerce(value: Any, typ: Any) -> Any:
                if value is None:
                    return value
                if typ is Path:
                    return Path(value)
                if typ is bool:
                    if isinstance(value, bool):
                        return value
                    return str(value).strip().lower() in {"1", "true", "yes", "on"}
                if typ is int:
                    return int(value)
                if typ is float:
                    return float(value)
                return value


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
