"""
config.py

Central configuration for the BMI Calculator application.
Keeps file paths and application constants in one place so that
other modules never hard-code paths or settings.
"""

import os

# Base directory of the project (directory this file lives in)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Application metadata
APP_NAME = "BMI Calculator"
APP_VERSION = "1.0.0"

# Data storage
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "bmi_history.json")

# Export storage
EXPORT_DIR = os.path.join(BASE_DIR, "exports")
EXPORT_FILE = os.path.join(EXPORT_DIR, "bmi_history.csv")

# Logging
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "bmi_calculator.log")

# BMI settings
BMI_PRECISION = 2  # number of decimal places shown for BMI values

# BMI classification thresholds (inclusive lower bound, exclusive upper bound
# except for the final "Obesity" category which has no upper bound)
BMI_CATEGORIES = (
    (0.0, 18.5, "Underweight"),
    (18.5, 25.0, "Normal weight"),
    (25.0, 30.0, "Overweight"),
    (30.0, float("inf"), "Obesity"),
)

# Supported measurement unit systems
UNIT_METRIC = "metric"      # kilograms + centimeters
UNIT_IMPERIAL = "imperial"  # pounds + inches
SUPPORTED_UNITS = (UNIT_METRIC, UNIT_IMPERIAL)


def ensure_directories() -> None:
    """Create the data, exports, and logs directories if they don't exist."""
    for directory in (DATA_DIR, EXPORT_DIR, LOG_DIR):
        os.makedirs(directory, exist_ok=True)
