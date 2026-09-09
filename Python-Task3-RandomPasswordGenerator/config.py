"""
config.py
---------
Central configuration module for the Random Password Generator project.

This module defines all constants used across the application, including
password length boundaries, default settings, character sets, and file
locations for history and logging. Keeping these values in a single place
avoids hardcoding them throughout the codebase and makes the project easier
to maintain and extend.
"""

import os
import string

# ---------------------------------------------------------------------------
# Base directory (the folder this config.py file lives in)
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Password length settings
# ---------------------------------------------------------------------------
MIN_PASSWORD_LENGTH = 4
MAX_PASSWORD_LENGTH = 128
DEFAULT_PASSWORD_LENGTH = 12

# ---------------------------------------------------------------------------
# Default password generation options
# ---------------------------------------------------------------------------
DEFAULT_USE_UPPERCASE = True
DEFAULT_USE_LOWERCASE = True
DEFAULT_USE_NUMBERS = True
DEFAULT_USE_SPECIAL = True

# ---------------------------------------------------------------------------
# Character sets used for password generation
# ---------------------------------------------------------------------------
LOWERCASE_CHARS = string.ascii_lowercase
UPPERCASE_CHARS = string.ascii_uppercase
NUMBER_CHARS = string.digits
SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

# ---------------------------------------------------------------------------
# Default number of passwords to generate at once
# ---------------------------------------------------------------------------
DEFAULT_COUNT = 1
MAX_COUNT = 50

# ---------------------------------------------------------------------------
# File locations
# ---------------------------------------------------------------------------
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

HISTORY_FILE = os.path.join(DATA_DIR, "password_history.json")
LOG_FILE = os.path.join(LOGS_DIR, "password_generator.log")

# ---------------------------------------------------------------------------
# History settings
# ---------------------------------------------------------------------------
# Maximum number of entries retained in the password history file.
# Older entries are discarded once this limit is exceeded, preventing the
# history file from growing without bound.
MAX_HISTORY_ENTRIES = 200

# ---------------------------------------------------------------------------
# Strength analysis thresholds (used by password_strength.py)
# ---------------------------------------------------------------------------
STRENGTH_LEVELS = ("Weak", "Moderate", "Strong", "Very Strong")
STRONG_LENGTH_THRESHOLD = 12
VERY_STRONG_LENGTH_THRESHOLD = 16

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = "INFO"


def ensure_directories() -> None:
    """
    Ensure that the data and logs directories exist.

    This is called at application startup so that file operations against
    HISTORY_FILE and LOG_FILE do not fail because their parent directories
    are missing.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
