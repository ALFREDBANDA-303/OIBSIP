"""
weather_api.py

Handles all communication with the OpenWeatherMap API.

Responsibilities:
    * Validate location input.
    * Build request URLs and parameters.
    * Perform HTTP requests with a timeout.
    * Translate HTTP/network failures into typed, catchable exceptions.
    * Return raw JSON (as Python dicts) to the caller -- this module
      does NOT know how to interpret weather fields; that is the job
      of ``weather_data.py``.

The API key is read once from ``config.get_api_key()`` and is never
logged, printed, or included in exception messages.
"""

from typing import Any, Dict

import requests

import config
from logger import get_logger

logger = get_logger("weather_api")


class WeatherAPIError(Exception):
    """Base class for all weather-API-related errors."""


class MissingAPIKeyError(WeatherAPIError):
    """Raised when no API key is configured."""


class InvalidLocationError(WeatherAPIError):
    """Raised when the location input is empty or otherwise invalid."""


class LocationNotFoundError(WeatherAPIError):
    """Raised when the API cannot find the requested location (HTTP 404)."""


class AuthenticationError(WeatherAPIError):
    """Raised when the API rejects the key (HTTP 401)."""


class RateLimitError(WeatherAPIError):
    """Raised when the API reports too many requests (HTTP 429)."""


class NetworkError(WeatherAPIError):
    """Raised for connection failures, timeouts, or other network issues."""


def validate_location(location: str) -> str:
    """
    Validate and normalize a location string entered by the user.

    Args:
        location: Raw location text (city name, "City,Country", or
            postal code).

    Returns:
        The trimmed location string.

    Raises:
        InvalidLocationError: If the location is empty, whitespace
            only, or exceeds the maximum allowed length.
    """
    if location is None:
        raise InvalidLocationError("Location cannot be empty.")

    trimmed = location.strip()

    if len(trimmed) < config.MIN_LOCATION_LENGTH:
        raise InvalidLocationError("Location cannot be empty.")

    if len(trimmed) > config.MAX_LOCATION_LENGTH:
        raise InvalidLocationError(
            f"Location cannot exceed {config.MAX_LOCATION_LENGTH} characters."
        )

    return trimmed


def _get_api_key_or_raise() -> str:
    """Return the configured API key, raising if it is missing."""
    api_key = config.get_api_key()
    if not api_key:
        raise MissingAPIKeyError(
            f"No API key found. Set the {config.API_KEY_ENV_VAR} "
            "environment variable (see .env.example)."
        )
    return api_key


def _perform_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a GET request against the API and return parsed JSON.

    Args:
        url: The endpoint URL.
        params: Query parameters, including the API key.

    Returns:
        The parsed JSON response body as a dictionary.

    Raises:
        LocationNotFoundError: On HTTP 404.
        AuthenticationError: On HTTP 401.
        RateLimitError: On HTTP 429.
        NetworkError: On timeout, connection failure, or other
            request-level errors.
        WeatherAPIError: On any other non-2xx HTTP status or invalid
            JSON response.
    """
    try:
        response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
    except requests.exceptions.Timeout as exc:
        logger.error("Request timed out contacting weather API")
        raise NetworkError("The request to the weather service timed out.") from exc
    except requests.exceptions.ConnectionError as exc:
        logger.error("Network connection error contacting weather API")
        raise NetworkError(
            "Could not connect to the weather service. Check your internet connection."
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.error("Unexpected request error: %s", type(exc).__name__)
        raise NetworkError(f"An unexpected network error occurred: {type(exc).__name__}") from exc

    if response.status_code == 401:
        logger.error("API authentication failed (401)")
        raise AuthenticationError(
            "The weather service rejected the API key. Verify it is correct and active."
        )

    if response.status_code == 404:
        logger.warning("Location not found (404)")
        raise LocationNotFoundError("Location not found. Check the spelling and try again.")

    if response.status_code == 429:
        logger.warning("API rate limit exceeded (429)")
        raise RateLimitError("Too many requests to the weather service. Please try again shortly.")

    if not response.ok:
        logger.error("Weather API returned unexpected status %s", response.status_code)
        raise WeatherAPIError(f"Weather service returned an error (HTTP {response.status_code}).")

    try:
        return response.json()
    except ValueError as exc:
        logger.error("Weather API returned invalid JSON")
        raise WeatherAPIError("Weather service returned an invalid response.") from exc


def build_current_weather_params(location: str, units: str, api_key: str) -> Dict[str, Any]:
    """Build the query parameters for a current-weather request."""
    return {"q": location, "units": units, "appid": api_key}


def build_forecast_params(location: str, units: str, api_key: str) -> Dict[str, Any]:
    """Build the query parameters for a forecast request."""
    return {"q": location, "units": units, "appid": api_key}


def fetch_current_weather(location: str, units: str = config.DEFAULT_UNIT) -> Dict[str, Any]:
    """
    Fetch current weather data for a location.

    Args:
        location: City name, "City,Country", or supported postal code.
        units: One of ``config.VALID_UNITS`` ("metric" or "imperial").

    Returns:
        The raw JSON response from OpenWeatherMap's current-weather
        endpoint, as a dictionary.

    Raises:
        InvalidLocationError: If the location is invalid.
        MissingAPIKeyError: If no API key is configured.
        LocationNotFoundError, AuthenticationError, RateLimitError,
        NetworkError, WeatherAPIError: On respective API/network failures.
    """
    location = validate_location(location)
    if units not in config.VALID_UNITS:
        units = config.DEFAULT_UNIT

    api_key = _get_api_key_or_raise()
    params = build_current_weather_params(location, units, api_key)

    logger.info("Fetching current weather for '%s' (units=%s)", location, units)
    data = _perform_request(config.CURRENT_WEATHER_ENDPOINT, params)
    logger.info("Current weather fetched successfully for '%s'", location)
    return data


def fetch_forecast(location: str, units: str = config.DEFAULT_UNIT) -> Dict[str, Any]:
    """
    Fetch forecast data for a location.

    Args:
        location: City name, "City,Country", or supported postal code.
        units: One of ``config.VALID_UNITS`` ("metric" or "imperial").

    Returns:
        The raw JSON response from OpenWeatherMap's forecast endpoint,
        as a dictionary.

    Raises:
        Same exceptions as ``fetch_current_weather``.
    """
    location = validate_location(location)
    if units not in config.VALID_UNITS:
        units = config.DEFAULT_UNIT

    api_key = _get_api_key_or_raise()
    params = build_forecast_params(location, units, api_key)

    logger.info("Fetching forecast for '%s' (units=%s)", location, units)
    data = _perform_request(config.FORECAST_ENDPOINT, params)
    logger.info("Forecast fetched successfully for '%s'", location)
    return data


def icon_url(icon_code: str) -> str:
    """
    Build the URL for a weather icon image.

    Args:
        icon_code: The icon code returned by the API (e.g. "01d").

    Returns:
        A full URL to the icon PNG, or an empty string if
        ``icon_code`` is falsy.
    """
    if not icon_code:
        return ""
    return f"{config.ICON_BASE_URL}/{icon_code}@2x.png"
