"""
main.py

Command-line entry point for the Weather Application.

Usage:
    python main.py
    python main.py --city Lilongwe
    python main.py --city Zomba --unit metric
    python main.py --city "New York,US" --unit imperial --forecast

If no arguments are supplied, the program prompts interactively for a
location. This module contains no API-parsing logic itself; it calls
into ``weather_api`` and ``weather_data`` and only formats the results
for display.
"""

import argparse
import sys

import config
import weather_api
import weather_data
from logger import get_logger

logger = get_logger("main")


def format_current_weather(weather: "weather_data.CurrentWeather") -> str:
    """Format a ``CurrentWeather`` object as readable CLI text."""
    lines = [
        f"Weather for {weather.location_name}, {weather.country}",
        "-" * 40,
        f"Condition:     {weather.condition} ({weather.description})",
        f"Temperature:   {weather.temperature}{weather.temperature_unit_symbol}",
        f"Feels like:    {weather.feels_like}{weather.temperature_unit_symbol}",
        f"Humidity:      {weather.humidity}%",
        f"Pressure:      {weather.pressure} hPa",
        f"Wind speed:    {weather.wind_speed} {weather.wind_speed_unit}",
    ]
    if weather.visibility_km is not None:
        lines.append(f"Visibility:    {weather.visibility_km} km")
    if weather.sunrise:
        lines.append(f"Sunrise (UTC): {weather.sunrise.strftime('%H:%M')}")
    if weather.sunset:
        lines.append(f"Sunset (UTC):  {weather.sunset.strftime('%H:%M')}")
    return "\n".join(lines)


def format_forecast(forecast: "weather_data.Forecast") -> str:
    """Format a ``Forecast`` object as readable CLI text."""
    lines = [
        "",
        f"5-Day Forecast for {forecast.location_name}, {forecast.country}",
        "-" * 40,
    ]
    for day in forecast.daily:
        lines.append(
            f"{day.date}: {day.min_temperature}-{day.max_temperature} "
            f"| {day.condition} ({day.description})"
        )
    return "\n".join(lines)


def run(location: str, unit: str, show_forecast: bool) -> int:
    """
    Fetch and print weather (and optionally forecast) for a location.

    Returns:
        Process exit code: 0 on success, 1 on any handled error.
    """
    try:
        raw_current = weather_api.fetch_current_weather(location, unit)
        current = weather_data.parse_current_weather(raw_current, unit)
        print(format_current_weather(current))

        if show_forecast:
            raw_forecast = weather_api.fetch_forecast(location, unit)
            forecast = weather_data.parse_forecast(raw_forecast)
            print(format_forecast(forecast))

        return 0

    except weather_api.InvalidLocationError as exc:
        print(f"[error] {exc}")
    except weather_api.MissingAPIKeyError as exc:
        print(f"[error] {exc}")
    except weather_api.LocationNotFoundError as exc:
        print(f"[error] {exc}")
    except weather_api.AuthenticationError as exc:
        print(f"[error] {exc}")
    except weather_api.RateLimitError as exc:
        print(f"[error] {exc}")
    except weather_api.NetworkError as exc:
        print(f"[error] {exc}")
    except weather_api.WeatherAPIError as exc:
        print(f"[error] {exc}")
    except weather_data.WeatherDataError as exc:
        print(f"[error] {exc}")

    logger.error("CLI request for '%s' failed", location)
    return 1


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description=f"{config.APP_NAME} -- retrieve real-time weather from OpenWeatherMap.",
    )
    parser.add_argument("--city", help="City name, 'City,Country', or postal code")
    parser.add_argument(
        "--unit",
        choices=sorted(config.VALID_UNITS),
        default=config.DEFAULT_UNIT,
        help=f"Temperature unit system (default: {config.DEFAULT_UNIT})",
    )
    parser.add_argument(
        "--forecast", action="store_true", help="Also display a 5-day forecast summary"
    )
    parser.add_argument(
        "--gui", action="store_true", help="Launch the graphical interface instead of the CLI"
    )
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = parse_args()

    if args.gui:
        import gui
        gui.main()
        return

    logger.info("Application started")

    location = args.city
    if not location:
        try:
            location = input("Enter a city name (e.g. Lilongwe): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(1)

    exit_code = run(location, args.unit, args.forecast)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
