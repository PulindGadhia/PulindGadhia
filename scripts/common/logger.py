"""
Centralized logging utilities.

This module provides a production-ready logging system for the GitHub
Profile Generator.

Features
--------
- Colored console logging
- Rotating log files
- Thread-safe singleton logger
- Exception logging helper
- Function execution timer
- Configurable log levels
"""

from __future__ import annotations

import functools
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Any, Callable, ParamSpec, TypeVar

from .config import ROOT_DIR

P = ParamSpec("P")
R = TypeVar("R")

LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "project.log"


# ---------------------------------------------------------
# Console Formatter
# ---------------------------------------------------------


class ColoredFormatter(logging.Formatter):
    """Colored console formatter."""

    COLORS = {
        logging.DEBUG: "\033[36m",      # Cyan
        logging.INFO: "\033[32m",       # Green
        logging.WARNING: "\033[33m",    # Yellow
        logging.ERROR: "\033[31m",      # Red
        logging.CRITICAL: "\033[41m",   # White on Red
    }

    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# ---------------------------------------------------------
# Logger Factory
# ---------------------------------------------------------


def _create_console_handler(level: int) -> logging.Handler:
    handler = logging.StreamHandler(sys.stdout)

    formatter = ColoredFormatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


def _create_file_handler(level: int) -> logging.Handler:
    handler = logging.handlers.RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


# ---------------------------------------------------------
# Singleton Logger
# ---------------------------------------------------------

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(
    name: str,
    *,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Return a configured singleton logger.

    Args:
        name:
            Logger name.

        level:
            Logging level.

    Returns:
        Configured logger.
    """

    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)

    logger.setLevel(level)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(_create_console_handler(level))
        logger.addHandler(_create_file_handler(level))

    _LOGGERS[name] = logger

    return logger


# ---------------------------------------------------------
# Exception Helper
# ---------------------------------------------------------


def log_exception(
    logger: logging.Logger,
    exception: Exception,
    *,
    message: str | None = None,
) -> None:
    """
    Log an exception with traceback.

    Args:
        logger:
            Logger instance.

        exception:
            Exception to log.

        message:
            Optional message.
    """

    logger.exception(message or str(exception))


# ---------------------------------------------------------
# Timing Decorator
# ---------------------------------------------------------


def log_execution_time(
    logger: logging.Logger,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that logs execution time.

    Example:
        logger = get_logger(__name__)

        @log_execution_time(logger)
        def generate():
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            start = time.perf_counter()

            try:
                return func(*args, **kwargs)

            finally:
                elapsed = time.perf_counter() - start

                logger.info(
                    "%s completed in %.3f seconds",
                    func.__name__,
                    elapsed,
                )

        return wrapper

    return decorator


# ---------------------------------------------------------
# Performance Helper
# ---------------------------------------------------------


class PerformanceTimer:
    """
    Context manager for measuring execution time.

    Example:
        with PerformanceTimer(logger, "Generate SVG"):
            ...
    """

    def __init__(
        self,
        logger: logging.Logger,
        label: str,
    ) -> None:
        self.logger = logger
        self.label = label
        self.start = 0.0

    def __enter__(self) -> "PerformanceTimer":
        self.start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        elapsed = time.perf_counter() - self.start

        self.logger.info(
            "%s finished in %.3f seconds",
            self.label,
            elapsed,
        )


# ---------------------------------------------------------
# Default Project Logger
# ---------------------------------------------------------

logger = get_logger("GitHubProfile")