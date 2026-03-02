"""Simple async interval scheduler for maintenance jobs."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict


@dataclass
class _JobSpec:
    name: str
    interval_seconds: float
    coroutine_factory: Callable[[], Awaitable[None]]


class AsyncScheduler:
    """Lightweight in-process scheduler for retrain/backfill tasks."""

    def __init__(self) -> None:
        self._jobs: Dict[str, _JobSpec] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    def add_interval_job(
        self,
        name: str,
        interval_seconds: float,
        coroutine_factory: Callable[[], Awaitable[None]],
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self._jobs[name] = _JobSpec(
            name=name,
            interval_seconds=interval_seconds,
            coroutine_factory=coroutine_factory,
        )

    async def _runner(self, spec: _JobSpec) -> None:
        while self._running:
            try:
                await spec.coroutine_factory()
            except Exception:
                # Keep scheduler alive; caller can wire structured logging here.
                pass
            await asyncio.sleep(spec.interval_seconds)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        for spec in self._jobs.values():
            self._tasks[spec.name] = asyncio.create_task(self._runner(spec), name=f"scheduler:{spec.name}")

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks.values():
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._tasks.clear()
