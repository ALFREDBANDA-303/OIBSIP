"""
weather_data.py

Converts raw OpenWeatherMap JSON responses into clean, typed Python
structures that the GUI and CLI can use directly, without needing to
know anything about the shape of the underlying API response.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import config
import weather_api


class WeatherDataError(Exception):
    """Raised when a weather API response is missing expected fields."""


@dataclass
class CurrentWeather:
    """A clean representation of a current-weather API response."""

    location_name: str
    country: str
    temperature: float
    feels_like: float
    condition: str
    description: str
    humidity: int
    pressure: int
    wind_speed: float
    visibility_km: Optional[float]
    icon_code: str
    icon_url: str
    sunrise: Optional[datetime]
    sunset: Optional[datetime]
    units: str

    @property
    def temperature_unit_symbol(self) -> str:
        return config.UNIT_SYMBOLS.get(self.units, "")

    @property
    def wind_speed_unit(self) -> str:
        return config.WIND_SPEED_UNITS.get(self.units, "")


@dataclass
class ForecastEntry:
    """A single 3-hour forecast data point."""

    timestamp: datetime
    temperature: float
    condition: str
    description: str
    humidity: int
    wind_speed: float
    icon_code: str
    icon_url: str


@dataclass
class DailyForecast:
    """A summarized single-day forecast (min/max across the day's entries)."""

    date: str
    min_temperature: float
    max_temperature: float
    condition: str
    description: str
    icon_code: str
    icon_url: str


@dataclass
class Forecast:
    """A full forecast: short-term (hourly-ish) entries plus a daily summary."""

    location_name: str
    country: str
    hourly: List[ForecastEntry] = field(default_factory=list)
    daily: List[DailyForecast] = field(default_factory=list)


def _safe_get(d: Dict[str, Any], *keys, default=None):
    """Traverse nested dictionaries safely, returning ``default`` on any miss."""
    current = d
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _to_datetime(unix_ts: Optional[int]) -> Optional[datetime]:
    """Convert a Unix timestamp (seconds) to a UTC ``datetime``, or None."""
    if unix_ts is None:
        return None
    try:
        return datetime.fromtimestamp(unix_ts, tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        return None


def parse_current_weather(raw: Dict[str, Any], units: str) -> CurrentWeather:
    """
    Parse a raw current-weather API response into a ``CurrentWeather``.

    Args:
        raw: The JSON dictionary returned by
            ``weather_api.fetch_current_weather``.
        units: The unit system ("metric" or "imperial") the request
            was made with, used only to attach display symbols.

    Returns:
        A populated ``CurrentWeather`` instance.

    Raises:
        WeatherDataError: If required fields are missing from ``raw``.
    """
    name = raw.get("name")
    country = _safe_get(raw, "sys", "country")
    temp = _safe_get(raw, "main", "temp")
    feels_like = _safe_get(raw, "main", "feels_like")
    humidity = _safe_get(raw, "main", "humidity")
    pressure = _safe_get(raw, "main", "pressure")
    wind_speed = _safe_get(raw, "wind", "speed")
    weather_list = raw.get("weather") or []

    if not weather_list:
        raise WeatherDataError("Weather response is missing condition data.")

    condition = weather_list[0].get("main", "")
    description = weather_list[0].get("description", "")
    icon_code = weather_list[0].get("icon", "")

    if name is None or temp is None or humidity is None or pressure is None:
        raise WeatherDataError("Weather response is missing required fields.")

    visibility_m = raw.get("visibility")
    visibility_km = round(visibility_m / 1000, 1) if isinstance(visibility_m, (int, float)) else None

    sunrise = _to_datetime(_safe_get(raw, "sys", "sunrise"))
    sunset = _to_datetime(_safe_get(raw, "sys", "sunset"))

    return CurrentWeather(
        location_name=name,
        country=country or "",
        temperature=float(temp),
        feels_like=float(feels_like) if feels_like is not None else float(temp),
        condition=condition,
        description=description.capitalize() if description else "",
        humidity=int(humidity),
        pressure=int(pressure),
        wind_speed=float(wind_speed) if wind_speed is not None else 0.0,
        visibility_km=visibility_km,
        icon_code=icon_code,
        icon_url=weather_api.icon_url(icon_code),
        sunrise=sunrise,
        sunset=sunset,
        units=units,
    )


def _parse_forecast_entry(item: Dict[str, Any]) -> ForecastEntry:
    """Parse a single item from the forecast API's 'list' array."""
    weather_list = item.get("weather") or [{}]
    weather0 = weather_list[0]
    icon_code = weather0.get("icon", "")

    timestamp = _to_datetime(item.get("dt")) or datetime.now(tz=timezone.utc)

    return ForecastEntry(
        timestamp=timestamp,
        temperature=float(_safe_get(item, "main", "temp", default=0.0)),
        condition=weather0.get("main", ""),
        description=(weather0.get("description", "") or "").capitalize(),
        humidity=int(_safe_get(item, "main", "humidity", default=0)),
        wind_speed=float(_safe_get(item, "wind", "speed", default=0.0)),
        icon_code=icon_code,
        icon_url=weather_api.icon_url(icon_code),
    )


def _summarize_daily(entries: List[ForecastEntry]) -> List[DailyForecast]:
    """Group hourly forecast entries by calendar date and summarize each day."""
    by_date: Dict[str, List[ForecastEntry]] = {}
    for entry in entries:
        date_key = entry.timestamp.strftime("%Y-%m-%d")
        by_date.setdefault(date_key, []).append(entry)

    daily: List[DailyForecast] = []
    for date_key in sorted(by_date.keys())[: config.FORECAST_DAILY_DAYS]:
        day_entries = by_date[date_key]
        temps = [e.temperature for e in day_entries]

        # Prefer the entry closest to midday to represent the day's condition.
        representative = min(
            day_entries, key=lambda e: abs(e.timestamp.hour - 12)
        )

        daily.append(DailyForecast(
            date=date_key,
            min_temperature=min(temps),
            max_temperature=max(temps),
            condition=representative.condition,
            description=representative.description,
            icon_code=representative.icon_code,
            icon_url=representative.icon_url,
        ))

    return daily


def parse_forecast(raw: Dict[str, Any]) -> Forecast:
    """
    Parse a raw forecast API response into a ``Forecast``.

    Args:
        raw: The JSON dictionary returned by
            ``weather_api.fetch_forecast``.

    Returns:
        A populated ``Forecast`` instance with both a short-term
        ("hourly") list and a summarized daily list.

    Raises:
        WeatherDataError: If the response has no forecast entries.
    """
    items = raw.get("list")
    if not items:
        raise WeatherDataError("Forecast response contains no data.")

    city = raw.get("city") or {}
    location_name = city.get("name", "")
    country = city.get("country", "")

    entries = [_parse_forecast_entry(item) for item in items]
    hourly = entries[: config.FORECAST_HOURLY_STEPS]
    daily = _summarize_daily(entries)

    return Forecast(
        location_name=location_name,
        country=country,
        hourly=hourly,
        daily=daily,
    )


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a temperature value between metric (Celsius) and imperial
    (Fahrenheit) unit systems.

    Args:
        value: The temperature value to convert.
        from_unit: The unit system ``value`` is currently in
            ("metric" or "imperial").
        to_unit: The unit system to convert to.

    Returns:
        The converted temperature, rounded to 1 decimal place. If
        ``from_unit == to_unit``, the original value is returned
        unchanged.
    """
    if from_unit == to_unit:
        return round(value, 1)

    if from_unit == config.UNIT_METRIC and to_unit == config.UNIT_IMPERIAL:
        return round((value * 9 / 5) + 32, 1)

    if from_unit == config.UNIT_IMPERIAL and to_unit == config.UNIT_METRIC:
        return round((value - 32) * 5 / 9, 1)

    return round(value, 1)
