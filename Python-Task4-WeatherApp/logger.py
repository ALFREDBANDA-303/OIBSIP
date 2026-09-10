"""
logger.py

Centralized logging configuration for the Weather Application.

Provides a single ``get_logger`` function that returns a configured
logger writing to both the console and a rotating log file under
``logs/weather_app.log``. The API key is never logged by any code in
this project; callers must not pass secret values into log messages.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

import config

_LOGGERS_CONFIGURED = set()


def _ensure_log_directory() -> None:
    """Create the logs directory if it does not already exist."""
    if not os.path.isdir(config.LOG_DIR):
        os.makedirs(config.LOG_DIR, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.

    The logger writes INFO-and-above messages to the console and
    DEBUG-and-above messages to a rotating log file. Calling this
    function multiple times with the same name is safe; handlers are
    only attached once per logger name.

    Args:
        name: The name of the logger, typically ``__name__`` of the
            calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    logger = logging.getLogger(name)

    if name in _LOGGERS_CONFIGURED:
        return logger

    _ensure_log_directory()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt=config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT
    )

    log_path = os.path.join(config.LOG_DIR, config.LOG_FILE)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _LOGGERS_CONFIGURED.add(name)
    return logger
