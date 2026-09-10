"""
tests.py

Automated test suite for the Weather Application.

Covers:
    * API URL / parameter construction
    * Input (location) validation
    * Weather data parsing (current + forecast)
    * Temperature conversion
    * API error handling (404, 401, 429, timeout, connection error)
    * Network error handling
    * Missing API key handling
    * Invalid location handling
    * Forecast parsing
    * Configuration
    * Application (main.py) functions

Run with:
    python tests.py
"""

import os
import unittest
from unittest.mock import Mock, patch

import requests

import config
import weather_api
import weather_data
import main


# ----------------------------------------------------------------------
# Configuration tests
# ----------------------------------------------------------------------

class TestConfiguration(unittest.TestCase):
    def test_default_unit_is_valid(self):
        self.assertIn(config.DEFAULT_UNIT, config.VALID_UNITS)

    def test_valid_units_contains_metric_and_imperial(self):
        self.assertEqual(config.VALID_UNITS, {"metric", "imperial"})

    def test_unit_symbols_defined_for_all_units(self):
        for unit in config.VALID_UNITS:
            self.assertIn(unit, config.UNIT_SYMBOLS)

    def test_request_timeout_positive(self):
        self.assertGreater(config.REQUEST_TIMEOUT, 0)

    def test_api_key_env_var_name_defined(self):
        self.assertEqual(config.API_KEY_ENV_VAR, "OPENWEATHER_API_KEY")

    def test_get_api_key_returns_string(self):
        self.assertIsInstance(config.get_api_key(), str)

    def test_get_api_key_reflects_environment(self):
        original = os.environ.get(config.API_KEY_ENV_VAR)
        try:
            os.environ[config.API_KEY_ENV_VAR] = "unit_test_key_value"
            self.assertEqual(config.get_api_key(), "unit_test_key_value")
        finally:
            if original is None:
                os.environ.pop(config.API_KEY_ENV_VAR, None)
            else:
                os.environ[config.API_KEY_ENV_VAR] = original

    def test_dotenv_loader_does_not_override_existing_env(self):
        original = os.environ.get(config.API_KEY_ENV_VAR)
        try:
            os.environ[config.API_KEY_ENV_VAR] = "already_set"
            with open(".env.test_tmp", "w", encoding="utf-8") as f:
                f.write("OPENWEATHER_API_KEY=from_file_should_not_apply\n")
            config._load_dotenv(".env.test_tmp")
            self.assertEqual(os.environ[config.API_KEY_ENV_VAR], "already_set")
        finally:
            if os.path.exists(".env.test_tmp"):
                os.remove(".env.test_tmp")
            if original is None:
                os.environ.pop(config.API_KEY_ENV_VAR, None)
            else:
                os.environ[config.API_KEY_ENV_VAR] = original


# ----------------------------------------------------------------------
# Input validation tests
# ----------------------------------------------------------------------

class TestLocationValidation(unittest.TestCase):
    def test_valid_location_passes(self):
        self.assertEqual(weather_api.validate_location("Lilongwe"), "Lilongwe")

    def test_location_is_trimmed(self):
        self.assertEqual(weather_api.validate_location("  Zomba  "), "Zomba")

    def test_empty_location_rejected(self):
        with self.assertRaises(weather_api.InvalidLocationError):
            weather_api.validate_location("")

    def test_whitespace_only_location_rejected(self):
        with self.assertRaises(weather_api.InvalidLocationError):
            weather_api.validate_location("    ")

    def test_none_location_rejected(self):
        with self.assertRaises(weather_api.InvalidLocationError):
            weather_api.validate_location(None)

    def test_too_long_location_rejected(self):
        long_location = "x" * (config.MAX_LOCATION_LENGTH + 1)
        with self.assertRaises(weather_api.InvalidLocationError):
            weather_api.validate_location(long_location)

    def test_city_country_format_accepted(self):
        self.assertEqual(weather_api.validate_location("Blantyre,MW"), "Blantyre,MW")


# ----------------------------------------------------------------------
# API URL / parameter construction tests
# ----------------------------------------------------------------------

class TestAPIRequestConstruction(unittest.TestCase):
    def test_current_weather_endpoint_url(self):
        self.assertTrue(config.CURRENT_WEATHER_ENDPOINT.endswith("/weather"))
        self.assertTrue(config.CURRENT_WEATHER_ENDPOINT.startswith("https://"))

    def test_forecast_endpoint_url(self):
        self.assertTrue(config.FORECAST_ENDPOINT.endswith("/forecast"))

    def test_build_current_weather_params(self):
        params = weather_api.build_current_weather_params("Lilongwe", "metric", "KEY123")
        self.assertEqual(params, {"q": "Lilongwe", "units": "metric", "appid": "KEY123"})

    def test_build_forecast_params(self):
        params = weather_api.build_forecast_params("Zomba", "imperial", "KEY123")
        self.assertEqual(params["q"], "Zomba")
        self.assertEqual(params["units"], "imperial")
        self.assertEqual(params["appid"], "KEY123")

    def test_icon_url_builds_correctly(self):
        url = weather_api.icon_url("01d")
        self.assertIn("01d", url)
        self.assertTrue(url.startswith(config.ICON_BASE_URL))

    def test_icon_url_empty_for_missing_code(self):
        self.assertEqual(weather_api.icon_url(""), "")
        self.assertEqual(weather_api.icon_url(None), "")


# ----------------------------------------------------------------------
# Missing API key handling
# ----------------------------------------------------------------------

class TestMissingAPIKey(unittest.TestCase):
    def setUp(self):
        self._original = os.environ.pop(config.API_KEY_ENV_VAR, None)

    def tearDown(self):
        if self._original is not None:
            os.environ[config.API_KEY_ENV_VAR] = self._original

    def test_fetch_current_weather_raises_without_key(self):
        with self.assertRaises(weather_api.MissingAPIKeyError):
            weather_api.fetch_current_weather("Lilongwe")

    def test_fetch_forecast_raises_without_key(self):
        with self.assertRaises(weather_api.MissingAPIKeyError):
            weather_api.fetch_forecast("Lilongwe")

    def test_missing_key_error_message_does_not_contain_key(self):
        try:
            weather_api.fetch_current_weather("Lilongwe")
        except weather_api.MissingAPIKeyError as exc:
            self.assertNotIn("appid", str(exc))


# ----------------------------------------------------------------------
# API / network error handling (mocked HTTP layer)
# ----------------------------------------------------------------------

class TestAPIErrorHandling(unittest.TestCase):
    def setUp(self):
        self._original = os.environ.get(config.API_KEY_ENV_VAR)
        os.environ[config.API_KEY_ENV_VAR] = "fake_test_key"

    def tearDown(self):
        if self._original is None:
            os.environ.pop(config.API_KEY_ENV_VAR, None)
        else:
            os.environ[config.API_KEY_ENV_VAR] = self._original

    def test_404_raises_location_not_found(self):
        with patch("weather_api.requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=404, ok=False)
            with self.assertRaises(weather_api.LocationNotFoundError):
                weather_api.fetch_current_weather("Nowhereville")

    def test_401_raises_authentication_error(self):
        with patch("weather_api.requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=401, ok=False)
            with self.assertRaises(weather_api.AuthenticationError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_429_raises_rate_limit_error(self):
        with patch("weather_api.requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=429, ok=False)
            with self.assertRaises(weather_api.RateLimitError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_500_raises_generic_weather_api_error(self):
        with patch("weather_api.requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=500, ok=False)
            with self.assertRaises(weather_api.WeatherAPIError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_timeout_raises_network_error(self):
        with patch("weather_api.requests.get", side_effect=requests.exceptions.Timeout()):
            with self.assertRaises(weather_api.NetworkError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_connection_error_raises_network_error(self):
        with patch("weather_api.requests.get", side_effect=requests.exceptions.ConnectionError()):
            with self.assertRaises(weather_api.NetworkError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_invalid_json_raises_weather_api_error(self):
        with patch("weather_api.requests.get") as mock_get:
            resp = Mock(status_code=200, ok=True)
            resp.json.side_effect = ValueError("not json")
            mock_get.return_value = resp
            with self.assertRaises(weather_api.WeatherAPIError):
                weather_api.fetch_current_weather("Lilongwe")

    def test_successful_request_returns_json(self):
        with patch("weather_api.requests.get") as mock_get:
            resp = Mock(status_code=200, ok=True)
            resp.json.return_value = {"name": "Lilongwe"}
            mock_get.return_value = resp
            data = weather_api.fetch_current_weather("Lilongwe")
            self.assertEqual(data["name"], "Lilongwe")

    def test_request_uses_timeout(self):
        with patch("weather_api.requests.get") as mock_get:
            resp = Mock(status_code=200, ok=True)
            resp.json.return_value = {}
            mock_get.return_value = resp
            weather_api.fetch_current_weather("Lilongwe")
            _, kwargs = mock_get.call_args
            self.assertEqual(kwargs.get("timeout"), config.REQUEST_TIMEOUT)

    def test_invalid_location_never_reaches_http_layer(self):
        with patch("weather_api.requests.get") as mock_get:
            with self.assertRaises(weather_api.InvalidLocationError):
                weather_api.fetch_current_weather("")
            mock_get.assert_not_called()


# ----------------------------------------------------------------------
# Weather data parsing tests
# ----------------------------------------------------------------------

class TestCurrentWeatherParsing(unittest.TestCase):
    def setUp(self):
        self.sample = {
            "name": "Lilongwe",
            "sys": {"country": "MW", "sunrise": 1700000000, "sunset": 1700040000},
            "main": {"temp": 25.3, "feels_like": 26.0, "humidity": 55, "pressure": 1012},
            "wind": {"speed": 3.1},
            "weather": [{"main": "Clouds", "description": "scattered clouds", "icon": "03d"}],
            "visibility": 10000,
        }

    def test_parses_basic_fields(self):
        cw = weather_data.parse_current_weather(self.sample, "metric")
        self.assertEqual(cw.location_name, "Lilongwe")
        self.assertEqual(cw.country, "MW")
        self.assertEqual(cw.temperature, 25.3)
        self.assertEqual(cw.humidity, 55)
        self.assertEqual(cw.pressure, 1012)

    def test_description_is_capitalized(self):
        cw = weather_data.parse_current_weather(self.sample, "metric")
        self.assertEqual(cw.description, "Scattered clouds")

    def test_icon_url_is_built(self):
        cw = weather_data.parse_current_weather(self.sample, "metric")
        self.assertIn("03d", cw.icon_url)

    def test_visibility_converted_to_km(self):
        cw = weather_data.parse_current_weather(self.sample, "metric")
        self.assertEqual(cw.visibility_km, 10.0)

    def test_missing_visibility_is_none(self):
        sample = dict(self.sample)
        sample.pop("visibility")
        cw = weather_data.parse_current_weather(sample, "metric")
        self.assertIsNone(cw.visibility_km)

    def test_sunrise_sunset_parsed_as_datetime(self):
        cw = weather_data.parse_current_weather(self.sample, "metric")
        self.assertIsNotNone(cw.sunrise)
        self.assertIsNotNone(cw.sunset)

    def test_missing_weather_list_raises(self):
        sample = dict(self.sample)
        sample["weather"] = []
        with self.assertRaises(weather_data.WeatherDataError):
            weather_data.parse_current_weather(sample, "metric")

    def test_missing_required_field_raises(self):
        sample = dict(self.sample)
        del sample["name"]
        with self.assertRaises(weather_data.WeatherDataError):
            weather_data.parse_current_weather(sample, "metric")

    def test_unit_symbol_matches_units(self):
        cw_metric = weather_data.parse_current_weather(self.sample, "metric")
        cw_imperial = weather_data.parse_current_weather(self.sample, "imperial")
        self.assertEqual(cw_metric.temperature_unit_symbol, "\u00b0C")
        self.assertEqual(cw_imperial.temperature_unit_symbol, "\u00b0F")


class TestForecastParsing(unittest.TestCase):
    def setUp(self):
        self.sample = {
            "city": {"name": "Lilongwe", "country": "MW"},
            "list": [
                {
                    "dt": 1700000000 + i * 10800,
                    "main": {"temp": 20 + i, "humidity": 50},
                    "wind": {"speed": 2.0},
                    "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
                }
                for i in range(16)
            ],
        }

    def test_parses_location(self):
        fc = weather_data.parse_forecast(self.sample)
        self.assertEqual(fc.location_name, "Lilongwe")
        self.assertEqual(fc.country, "MW")

    def test_hourly_entries_limited_to_configured_steps(self):
        fc = weather_data.parse_forecast(self.sample)
        self.assertEqual(len(fc.hourly), config.FORECAST_HOURLY_STEPS)

    def test_daily_entries_grouped_by_date(self):
        fc = weather_data.parse_forecast(self.sample)
        dates = [d.date for d in fc.daily]
        self.assertEqual(len(dates), len(set(dates)))

    def test_daily_min_max_temperatures(self):
        fc = weather_data.parse_forecast(self.sample)
        for day in fc.daily:
            self.assertLessEqual(day.min_temperature, day.max_temperature)

    def test_empty_list_raises(self):
        with self.assertRaises(weather_data.WeatherDataError):
            weather_data.parse_forecast({"city": {}, "list": []})

    def test_missing_list_raises(self):
        with self.assertRaises(weather_data.WeatherDataError):
            weather_data.parse_forecast({"city": {}})


# ----------------------------------------------------------------------
# Temperature conversion tests
# ----------------------------------------------------------------------

class TestTemperatureConversion(unittest.TestCase):
    def test_celsius_to_fahrenheit(self):
        self.assertEqual(weather_data.convert_temperature(0, "metric", "imperial"), 32.0)
        self.assertEqual(weather_data.convert_temperature(100, "metric", "imperial"), 212.0)

    def test_fahrenheit_to_celsius(self):
        self.assertEqual(weather_data.convert_temperature(32, "imperial", "metric"), 0.0)
        self.assertEqual(weather_data.convert_temperature(212, "imperial", "metric"), 100.0)

    def test_same_unit_returns_unchanged(self):
        self.assertEqual(weather_data.convert_temperature(25.567, "metric", "metric"), 25.6)

    def test_rounding_to_one_decimal(self):
        result = weather_data.convert_temperature(25, "metric", "imperial")
        self.assertEqual(result, round(result, 1))


# ----------------------------------------------------------------------
# main.py (application) tests
# ----------------------------------------------------------------------

class TestMainApplication(unittest.TestCase):
    def setUp(self):
        self._original = os.environ.get(config.API_KEY_ENV_VAR)
        os.environ[config.API_KEY_ENV_VAR] = "fake_test_key"

    def tearDown(self):
        if self._original is None:
            os.environ.pop(config.API_KEY_ENV_VAR, None)
        else:
            os.environ[config.API_KEY_ENV_VAR] = self._original

    def test_run_returns_zero_on_success(self):
        with patch("weather_api.requests.get") as mock_get:
            resp = Mock(status_code=200, ok=True)
            resp.json.return_value = {
                "name": "Lilongwe",
                "sys": {"country": "MW"},
                "main": {"temp": 20, "feels_like": 20, "humidity": 50, "pressure": 1000},
                "wind": {"speed": 1},
                "weather": [{"main": "Clear", "description": "clear sky", "icon": "01d"}],
            }
            mock_get.return_value = resp
            self.assertEqual(main.run("Lilongwe", "metric", False), 0)

    def test_run_returns_one_on_invalid_location(self):
        self.assertEqual(main.run("", "metric", False), 1)

    def test_run_returns_one_on_missing_key(self):
        os.environ.pop(config.API_KEY_ENV_VAR, None)
        self.assertEqual(main.run("Lilongwe", "metric", False), 1)

    def test_run_returns_one_on_location_not_found(self):
        with patch("weather_api.requests.get") as mock_get:
            mock_get.return_value = Mock(status_code=404, ok=False)
            self.assertEqual(main.run("Nowhereville", "metric", False), 1)

    def test_format_current_weather_contains_key_fields(self):
        sample = {
            "name": "Lilongwe",
            "sys": {"country": "MW"},
            "main": {"temp": 20, "feels_like": 19, "humidity": 60, "pressure": 1005},
            "wind": {"speed": 2},
            "weather": [{"main": "Rain", "description": "light rain", "icon": "10d"}],
        }
        cw = weather_data.parse_current_weather(sample, "metric")
        text = main.format_current_weather(cw)
        self.assertIn("Lilongwe", text)
        self.assertIn("Rain", text)
        self.assertIn("Humidity", text)

    def test_parse_args_defaults(self):
        with patch("sys.argv", ["main.py"]):
            args = main.parse_args()
            self.assertIsNone(args.city)
            self.assertEqual(args.unit, config.DEFAULT_UNIT)
            self.assertFalse(args.forecast)

    def test_parse_args_with_city_and_unit(self):
        with patch("sys.argv", ["main.py", "--city", "Zomba", "--unit", "imperial"]):
            args = main.parse_args()
            self.assertEqual(args.city, "Zomba")
            self.assertEqual(args.unit, "imperial")


if __name__ == "__main__":
    unittest.main(verbosity=2)
