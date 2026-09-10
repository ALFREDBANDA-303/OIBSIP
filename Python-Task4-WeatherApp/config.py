"""
config.py

Central configuration for the Weather Application.

All configurable values live here so nothing is hardcoded throughout
the project. The real OpenWeatherMap API key is never stored in this
file -- it is read from the environment variable named by
``API_KEY_ENV_VAR`` at runtime (see ``weather_api.get_api_key``).
"""

import os

# ----------------------------------------------------------------------
# Lightweight .env loader (no external dependency required)
# ----------------------------------------------------------------------

def _load_dotenv(path: str = ".env") -> None:
    """
    Load simple KEY=VALUE pairs from a .env file into the environment.

    This is a minimal, dependency-free stand-in for python-dotenv,
    sufficient for a single API key. Existing environment variables
    are never overwritten, so real environment configuration always
    takes precedence over the .env file. Values are never logged or
    printed by this function.
    """
    if not os.path.isfile(path):
        return

    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        # Missing or unreadable .env is not fatal; the app falls back
        # to whatever is already in the environment.
        pass


_load_dotenv()

# ----------------------------------------------------------------------
# API configuration
# ----------------------------------------------------------------------

# Name of the environment variable that holds the real API key.
# The key itself is never written in this file or anywhere in source
# control -- see .env.example for the expected format.
API_KEY_ENV_VAR = "OPENWEATHER_API_KEY"

API_BASE_URL = "https://api.openweathermap.org/data/2.5"
CURRENT_WEATHER_ENDPOINT = f"{API_BASE_URL}/weather"
FORECAST_ENDPOINT = f"{API_BASE_URL}/forecast"

ICON_BASE_URL = "https://openweathermap.org/img/wn"

# Seconds to wait before giving up on a request to the weather API.
REQUEST_TIMEOUT = 10

# ----------------------------------------------------------------------
# Units
# ----------------------------------------------------------------------

UNIT_METRIC = "metric"     # Celsius, meters/sec
UNIT_IMPERIAL = "imperial"  # Fahrenheit, miles/hour

VALID_UNITS = {UNIT_METRIC, UNIT_IMPERIAL}
DEFAULT_UNIT = UNIT_METRIC

UNIT_SYMBOLS = {
    UNIT_METRIC: "\u00b0C",
    UNIT_IMPERIAL: "\u00b0F",
}

WIND_SPEED_UNITS = {
    UNIT_METRIC: "m/s",
    UNIT_IMPERIAL: "mph",
}

# ----------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------

MIN_LOCATION_LENGTH = 1
MAX_LOCATION_LENGTH = 100

# ----------------------------------------------------------------------
# Forecast display settings
# ----------------------------------------------------------------------

# The forecast endpoint returns data in 3-hour steps. This controls how
# many of those steps are shown in the short-term ("hourly") forecast.
FORECAST_HOURLY_STEPS = 8   # 8 steps * 3 hours = 24 hours

# Number of distinct calendar days to summarize in the daily forecast.
FORECAST_DAILY_DAYS = 5

# ----------------------------------------------------------------------
# Application metadata
# ----------------------------------------------------------------------

APP_NAME = "Basic Weather App"
APP_VERSION = "1.0.0"

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------

LOG_DIR = "logs"
LOG_FILE = "weather_app.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_api_key() -> str:
    """
    Read the OpenWeatherMap API key from the environment.

    Returns:
        The API key string, or an empty string if it is not set.
    """
    return os.environ.get(API_KEY_ENV_VAR, "").strip()
