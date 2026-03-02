"""Structured logging helpers with graceful fallback."""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

try:
    import structlog
except Exception:  # pragma: no cover - optional dependency
    structlog = None


def configure_logging(level: int = logging.INFO) -> None:
    """Configure stdlib + structlog when available."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )
    if structlog is None:
        return

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """Return structlog logger if available, else stdlib logger."""
    if structlog is not None:
        return structlog.get_logger(name)
    return logging.getLogger(name)


def bind_context(logger, **kwargs: Dict[str, Any]):
    """Bind context fields when supported."""
    if hasattr(logger, "bind"):
        return logger.bind(**kwargs)
    return logger
