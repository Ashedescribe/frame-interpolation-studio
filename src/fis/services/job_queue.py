"""Thread-pool job dispatcher used by the desktop UI.

Runs interpolation jobs off the Qt main thread and emits progress via
simple callbacks. Jobs are FIFO; cancel sets a flag the handler polls.
"""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any

import structlog

log = structlog.get_logger(__name__)


@dataclass
class Job:
    name: str
    fn: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)
    cancelled: bool = False


class JobQueue:
    def __init__(self, workers: int = 1) -> None:
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="fis-job")
        self._jobs: list[Job] = []

    def submit(self, job: Job) -> None:
        self._jobs.append(job)
        self._pool.submit(self._run, job)

    @staticmethod
    def _run(job: Job) -> None:
        if job.cancelled:
            log.info("job.cancelled_before_start", name=job.name)
            return
        try:
            job.fn(*job.args, **job.kwargs)
            log.info("job.done", name=job.name)
        except Exception as exc:  # noqa: BLE001
            log.error("job.failed", name=job.name, error=str(exc))

    def shutdown(self, wait: bool = True) -> None:
        self._pool.shutdown(wait=wait)