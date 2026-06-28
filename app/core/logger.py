"""
Enterprise Knowledge Assistant
Centralized Logging Configuration

This module configures application-wide logging.
Every module in the project should use:

    from app.core.logger import get_logger

instead of configuring logging independently.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


LOG_DIRECTORY = Path("logs")
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIRECTORY / "application.log"


def configure_logger(
    level: int = logging.INFO,
    log_to_console: bool = True,
    log_to_file: bool = True,
) -> None:
    """
    Configure the root logger.

    Parameters
    ----------
    level : int
        Logging level.

    log_to_console : bool
        Enable console logging.

    log_to_file : bool
        Enable file logging.
    """

    root_logger = logging.getLogger()

    # Prevent duplicate handlers
    if root_logger.handlers:
        return

    root_logger.setLevel(level)

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)-8s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if log_to_console:

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(console_handler)

    if log_to_file:

        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8",
        )

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name : str | None

    Returns
    -------
    logging.Logger
    """

    return logging.getLogger(name)