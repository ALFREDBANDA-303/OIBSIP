# Basic Weather App

**OASIS INFOBYTE Python Programming Internship — Task 4**

A modular Python weather application that retrieves real-time weather
data and a 5-day forecast from the OpenWeatherMap API, available both
as a command-line tool and a Tkinter GUI.

---

## Project Description

This project lets a user enter a location — a city name, "City,Country",
or a supported postal code — and displays current weather conditions
plus a short-term and daily forecast. All API communication and JSON
parsing are isolated from the presentation layer, so the same core
logic powers both the CLI and the GUI.

---

## Features

* Location search by city name, "City,Country", or postal code
* Real-time current weather: temperature, feels-like, condition,
  description, humidity, pressure, wind speed, visibility, sunrise,
  and sunset
* Celsius / Fahrenheit unit switching, including converting
  already-fetched data in the GUI without an extra API call
* Weather icons rendered from OpenWeatherMap's icon set, with graceful
  fallback if an icon fails to load
* Short-term forecast (24 hours in 3-hour steps) and a summarized
  5-day daily forecast (min/max temperature, condition)
* Professional Tkinter GUI with a responsive interface — API calls run
  on a background thread so the window never freezes
* CLI with optional `--city`, `--unit`, `--forecast`, and `--gui` flags
* Centralized configuration (`config.py`) — no hardcoded values or keys
* API key loaded from an environment variable or a local `.env` file,
  never hardcoded or logged
* File + console logging of searches, errors, and failures
* Graceful handling of invalid input, invalid/missing API keys, invalid
  locations, and network failures
* Automated test suite (`unittest`) covering parsing, validation,
  conversion, and error handling

---

## Technologies

* Python 3
* `requests` — HTTP communication with the OpenWeatherMap API
* `json` (via `requests`' built-in JSON handling)
* `tkinter` — graphical user interface
* `logging` — application event logging
* `unittest` — automated testing
* `argparse` — command-line argument parsing
* `dataclasses` — clean, typed weather data structures

---

## Project Structure

```
Python-Task4-WeatherApp/
│
├── main.py             # CLI entry point (and GUI launcher via --gui)
├── weather_api.py       # All HTTP/API communication and error handling
├── weather_data.py       # Parses raw API JSON into clean data structures
├── config.py               # Centralized configuration + .env loading
├── logger.py                 # Logging setup (console + file)
├── gui.py                      # Tkinter GUI client
├── tests.py                      # Automated unittest suite
├── requirements.txt                # External dependencies (requests)
├── .env.example                      # Template for the API key variable
├── .gitignore
├── README.md                           # This file
│
├── logs/
│   └── weather_app.log               # Created automatically at runtime
│
└── screenshots/
    └── gui_screenshot.png            # GUI screenshot for demonstration
```

---

## Architecture

```
 ┌─────────────┐        ┌───────────────┐        ┌────────────────┐
 │   main.py   │ ─────▶ │ weather_api.py │ ─────▶ │ OpenWeatherMap │
 │   (CLI)     │        │ (HTTP, errors) │        │      API       │
 └──────┬──────┘        └───────┬────────┘        └────────────────┘
        │                        │ raw JSON
        │                        ▼
        │                ┌────────────────┐
        │                │ weather_data.py │
        │                │ (parsing, unit  │
        │                │  conversion)    │
        │                └───────┬────────┘
        │                        │ clean dataclasses
        ▼                        ▼
 ┌─────────────┐        ┌────────────────┐
 │  gui.py     │ ─────▶ │  (same modules  │
 │  (Tkinter)  │        │   as above)     │
 └─────────────┘        └────────────────┘
```

* **`weather_api.py`** never lets the GUI or CLI parse raw JSON itself,
  and never lets a network failure propagate as an unhandled exception
  — every failure mode (missing key, bad location, timeout, connection
  error, rate limiting, bad JSON) is translated into a specific,
  catchable exception type.
* **`weather_data.py`** converts raw API responses into `CurrentWeather`,
  `ForecastEntry`, and `DailyForecast` dataclasses, and provides
  `convert_temperature` so the GUI can re-render already-fetched data
  in a new unit without making another API call.
* **`gui.py`** runs all API calls on a background thread and
  communicates results back to the Tkinter main thread through a
  thread-safe queue, so the window stays responsive during a search.
* **`config.py`** centralizes every constant and includes a minimal,
  dependency-free `.env` file loader — real environment variables
  always take precedence over `.env` file values.

---

## Prerequisites

* Python 3.8 or later
* `tkinter` — usually bundled with Python; on some Linux distributions
  install it separately, e.g. `sudo apt install python3-tk`
* A free OpenWeatherMap API key (see below)

---

## Installation

```bash
git clone <your-fork-url>
cd Python-Task4-WeatherApp
```

### Virtual Environment Setup

```bash
python3 -m venv venv

# Activate:
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

### Dependency Installation

```bash
pip install -r requirements.txt
```

---

## OpenWeatherMap API Setup

1. Create a free account at <https://openweathermap.org/api>.
2. Generate an API key from your account dashboard.
3. Note that newly created keys can take a short while to activate.

## Environment Variable Setup

Copy the example file and fill in your real key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENWEATHER_API_KEY=your_real_key_here
```

`.env` is listed in `.gitignore` and will never be committed. You can
alternatively export the variable directly in your shell instead of
using a `.env` file:

```bash
export OPENWEATHER_API_KEY=your_real_key_here      # Linux / macOS
set OPENWEATHER_API_KEY=your_real_key_here          # Windows (cmd)
```

---

## How to Run the Application

### CLI Instructions

Interactive prompt:

```bash
python main.py
```

Direct city lookup:

```bash
python main.py --city Lilongwe
```

With unit and forecast:

```bash
python main.py --city Zomba --unit metric --forecast
python main.py --city "New York,US" --unit imperial --forecast
```

See all options:

```bash
python main.py --help
```

### GUI Instructions

```bash
python gui.py
```

or, equivalently:

```bash
python main.py --gui
```

1. Enter a location (city name, "City,Country", or postal code).
2. Choose Celsius or Fahrenheit.
3. Click **Search** (or press Enter).
4. View current conditions, the weather icon, and the 5-day forecast.
5. Switch units at any time — already-fetched data updates instantly
   without a new network request.
6. Click **Clear** to reset the form.

---

## Testing Instructions

Run the full automated test suite:

```bash
python tests.py
```

The suite uses mocked HTTP responses (via `unittest.mock`) so it runs
without a real API key or network access, while still exercising the
exact same code paths used in production: URL/parameter construction,
location validation, JSON parsing, temperature conversion, and every
API/network error branch (404, 401, 429, 500, timeout, connection
error, invalid JSON, missing key).

Also verify the project compiles cleanly:

```bash
python -m compileall .
```

---

## Error Handling

The application handles, without crashing:

* Empty, whitespace-only, or excessively long location input
* Missing or empty API key (clear message, no crash)
* Invalid or rejected API key (HTTP 401)
* Location not found (HTTP 404)
* API rate limiting (HTTP 429)
* Other non-2xx API responses
* Request timeouts
* Connection failures (no internet, DNS failure, etc.)
* Invalid or unparseable JSON responses
* Missing expected fields in an otherwise valid API response
* Failed weather-icon downloads (icon is simply omitted, rest of the
  data still displays)

All failures are logged (without ever logging the API key itself) and
surfaced to the user with a clear, human-readable message.

---

## Security Considerations

* The API key is **never** hardcoded in source code.
* The key is read from the `OPENWEATHER_API_KEY` environment variable,
  optionally via a local `.env` file.
* `.env` is excluded via `.gitignore` — only `.env.example` (with a
  placeholder) is committed.
* The API key is never printed to the console or written to the log
  file; log messages reference request outcomes and locations only.
* Screenshots in this repository do not contain any API key or other
  credential.
* All outbound HTTP requests use an explicit timeout to avoid the
  application hanging indefinitely on a slow or unresponsive network.

---

## Screenshots

See `screenshots/gui_screenshot.png` for a screenshot of the Tkinter
GUI displaying current weather and a 5-day forecast. No credentials
are visible in this or any other screenshot.

---

## Future Improvements

* Hourly forecast chart/graph view
* Search history / recently searched locations
* Geolocation-based "weather near me"
* Multiple saved favorite locations
* Dark mode theme for the GUI
* Localization / multi-language support

---

## Author

Developed as part of the **OASIS INFOBYTE Python Programming Internship**,
Task 4 — Basic Weather App.
