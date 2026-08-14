"""
logger.py

Centralized logging configuration for the BMI Calculator application.
All modules import `get_logger` from here rather than configuring
logging themselves, so log formatting and destination stay consistent.

No sensitive personal information (e.g. exact weight/height values)
is written to the log; only high-level events and errors are recorded.
"""

import logging
import os

import config


def get_logger(name: str = "bmi_calculator") -> logging.Logger:
    """
    Return a configured logger instance that writes to config.LOG_FILE.

    Safe to call multiple times (e.g. from multiple modules); handlers
    are only attached once per logger name.
    """
    os.makedirs(config.LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        try:
            file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except OSError:
            # If the log file cannot be created/opened, fall back to a
            # null handler so the application keeps running.
            logger.addHandler(logging.NullHandler())

        logger.propagate = False

    return logger
