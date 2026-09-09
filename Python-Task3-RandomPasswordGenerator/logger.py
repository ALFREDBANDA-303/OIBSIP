"""
logger.py
---------
Centralized logging configuration for the Random Password Generator.

This module configures a single application-wide logger that writes to both
the console and a rotating log file. It is critical from a security
standpoint that this module (and every module that uses it) NEVER logs the
actual contents of a generated password. Only metadata such as password
length, character-set options, and strength category should ever be logged.
"""

import logging
import logging.handlers

import config


def get_logger(name: str = "password_generator") -> logging.Logger:
    """
    Create and return a configured logger instance.

    The logger writes INFO-level (and above) messages to a rotating log
    file located at config.LOG_FILE, and also streams them to the console.
    Calling this function multiple times with the same name returns the
    same underlying logger without duplicating handlers.

    Args:
        name: The name of the logger (defaults to "password_generator").

    Returns:
        A configured logging.Logger instance.
    """
    config.ensure_directories()

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    # Avoid adding duplicate handlers if this function is called more than
    # once (e.g. imported by several modules).
    if logger.handlers:
        return logger

    formatter = logging.Formatter(fmt=config.LOG_FORMAT, datefmt=config.LOG_DATE_FORMAT)

    # Rotating file handler: keeps log files from growing indefinitely.
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE, maxBytes=512_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for immediate feedback during development / CLI use.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)  # keep console output clean
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger


# A shared, module-level logger instance for convenience.
app_logger = get_logger()


def log_startup() -> None:
    """Log an application startup event."""
    app_logger.info("Application started.")


def log_shutdown() -> None:
    """Log an application shutdown event."""
    app_logger.info("Application shutting down.")


def log_password_generated(length: int, count: int, strength: str) -> None:
    """
    Log that a password was generated, without ever logging the password
    itself.

    Args:
        length: The length of the generated password(s).
        count: How many passwords were generated in this operation.
        strength: The strength category of the generated password
            (e.g. "Strong"). Only used for the last generated password when
            count > 1.
    """
    app_logger.info(
        "Password generated | length=%d | count=%d | strength=%s",
        length,
        count,
        strength,
    )


def log_error(message: str) -> None:
    """Log an error message."""
    app_logger.error(message)


def log_history_event(event: str) -> None:
    """Log a password-history-related event (save, load, clear, etc.)."""
    app_logger.info("History event: %s", event)


def log_clipboard_event(event: str, success: bool) -> None:
    """Log a clipboard-related event."""
    status = "SUCCESS" if success else "FAILED"
    app_logger.info("Clipboard event: %s | status=%s", event, status)
