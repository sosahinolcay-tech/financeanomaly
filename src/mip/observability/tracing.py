"""Lightweight tracing primitives."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from time import perf_counter
from typing import Iterator
import uuid


@dataclass(frozen=True)
class TraceSpan:
    """Trace metadata for a single span."""

    trace_id: str
    span_id: str
    name: str
    duration_ms: float


@contextmanager
def trace_span(name: str, trace_id: str | None = None) -> Iterator[TraceSpan]:
    """Context manager that yields span metadata on exit.

    This can later be replaced by OpenTelemetry with the same call-site shape.
    """
    parent_trace_id = trace_id or str(uuid.uuid4())
    span_id = str(uuid.uuid4())
    start = perf_counter()
    span = TraceSpan(
        trace_id=parent_trace_id,
        span_id=span_id,
        name=name,
        duration_ms=0.0,
    )
    try:
        yield span
    finally:
        object.__setattr__(span, "duration_ms", (perf_counter() - start) * 1000.0)
