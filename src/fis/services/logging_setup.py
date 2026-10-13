"""Structured logging configuration for the desktop and CLI entry points."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "fis.log"


def configure_logging(level: int = logging.INFO) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=level,
        handlers=[logging.StreamHandler(sys.stderr), logging.FileHandler(LOG_FILE, encoding="utf-8")],
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )