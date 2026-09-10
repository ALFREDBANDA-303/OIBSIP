"""
gui.py

Tkinter GUI for the Weather Application.

This module contains ONLY presentation logic. All API communication
goes through ``weather_api`` and all response parsing goes through
``weather_data`` -- the GUI never touches raw API JSON directly.

API requests are performed on a background thread so the interface
stays responsive; results are posted back to the main thread through
a thread-safe ``queue.Queue`` and drained via ``after()`` polling.
"""

import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

import requests

import config
import weather_api
import weather_data
from logger import get_logger

logger = get_logger("gui")

POLL_INTERVAL_MS = 100


class WeatherGUI:
    """Main Tkinter application window for the weather app."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(config.APP_NAME)
        self.root.geometry("560x640")
        self.root.minsize(480, 560)

        self.unit_var = tk.StringVar(value=config.DEFAULT_UNIT)
        self.location_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")
        self.error_var = tk.StringVar(value="")

        self._event_queue: "queue.Queue[tuple]" = queue.Queue()
        self._icon_image: Optional[tk.PhotoImage] = None
        self._last_current: Optional[weather_data.CurrentWeather] = None
        self._last_forecast: Optional[weather_data.Forecast] = None

        self._build_widgets()
        self.root.after(POLL_INTERVAL_MS, self._poll_events)

    # ------------------------------------------------------------------
    # Widget construction
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text=config.APP_NAME, font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 8)
        )

        ttk.Label(top, text="Location:").grid(row=1, column=0, sticky="w")
        location_entry = ttk.Entry(top, textvariable=self.location_var, width=24)
        location_entry.grid(row=1, column=1, padx=4, sticky="we")
        location_entry.bind("<Return>", lambda _e: self._on_search())

        self.search_btn = ttk.Button(top, text="Search", command=self._on_search)
        self.search_btn.grid(row=1, column=2, padx=4)

        self.clear_btn = ttk.Button(top, text="Clear", command=self._on_clear)
        self.clear_btn.grid(row=1, column=3, padx=4)

        ttk.Label(top, text="Units:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        unit_frame = ttk.Frame(top)
        unit_frame.grid(row=2, column=1, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Radiobutton(
            unit_frame, text="Celsius (°C)", variable=self.unit_var,
            value=config.UNIT_METRIC, command=self._on_unit_change,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            unit_frame, text="Fahrenheit (°F)", variable=self.unit_var,
            value=config.UNIT_IMPERIAL, command=self._on_unit_change,
        ).pack(side=tk.LEFT, padx=(10, 0))

        top.columnconfigure(1, weight=1)

        ttk.Label(self.root, textvariable=self.status_var, foreground="#555555", padding=(10, 0)).pack(
            side=tk.TOP, anchor="w"
        )
        ttk.Label(self.root, textvariable=self.error_var, foreground="#c0392b", padding=(10, 0)).pack(
            side=tk.TOP, anchor="w"
        )

        # --- Current weather panel ---
        current_frame = ttk.LabelFrame(self.root, text="Current Weather", padding=10)
        current_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(6, 6))

        self.icon_label = ttk.Label(current_frame)
        self.icon_label.grid(row=0, column=0, rowspan=4, padx=(0, 10))

        self.location_result_var = tk.StringVar(value="--")
        self.temp_var = tk.StringVar(value="--")
        self.condition_var = tk.StringVar(value="--")
        self.humidity_var = tk.StringVar(value="--")
        self.wind_var = tk.StringVar(value="--")
        self.pressure_var = tk.StringVar(value="--")

        ttk.Label(current_frame, textvariable=self.location_result_var, font=("TkDefaultFont", 12, "bold")).grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(current_frame, textvariable=self.temp_var, font=("TkDefaultFont", 20, "bold")).grid(
            row=1, column=1, sticky="w"
        )
        ttk.Label(current_frame, textvariable=self.condition_var).grid(row=2, column=1, sticky="w")

        details = ttk.Frame(current_frame)
        details.grid(row=3, column=1, sticky="w", pady=(6, 0))
        ttk.Label(details, textvariable=self.humidity_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(details, textvariable=self.wind_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(details, textvariable=self.pressure_var).pack(side=tk.LEFT)

        # --- Forecast panel ---
        forecast_frame = ttk.LabelFrame(self.root, text="5-Day Forecast", padding=10)
        forecast_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.forecast_list = tk.Listbox(forecast_frame)
        self.forecast_list.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._set_busy(False)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _on_search(self) -> None:
        location = self.location_var.get().strip()

        try:
            weather_api.validate_location(location)
        except weather_api.InvalidLocationError as exc:
            self._show_error(str(exc))
            return

        self._clear_error()
        self._set_busy(True)
        self.status_var.set(f"Searching for '{location}'...")

        unit = self.unit_var.get()
        thread = threading.Thread(
            target=self._fetch_weather_worker, args=(location, unit), daemon=True
        )
        thread.start()

    def _on_clear(self) -> None:
        self.location_var.set("")
        self._clear_error()
        self.status_var.set("")
        self.location_result_var.set("--")
        self.temp_var.set("--")
        self.condition_var.set("--")
        self.humidity_var.set("--")
        self.wind_var.set("--")
        self.pressure_var.set("--")
        self.icon_label.configure(image="")
        self._icon_image = None
        self.forecast_list.delete(0, tk.END)
        self._last_current = None
        self._last_forecast = None

    def _on_unit_change(self) -> None:
        """Re-render already-fetched data in the new unit, without a new API call."""
        if self._last_current is None:
            return

        new_unit = self.unit_var.get()
        old_unit = self._last_current.units

        if new_unit == old_unit:
            return

        converted_temp = weather_data.convert_temperature(
            self._last_current.temperature, old_unit, new_unit
        )
        converted_feels = weather_data.convert_temperature(
            self._last_current.feels_like, old_unit, new_unit
        )
        self._last_current.temperature = converted_temp
        self._last_current.feels_like = converted_feels
        self._last_current.units = new_unit

        self._render_current(self._last_current)

        if self._last_forecast is not None:
            for entry in self._last_forecast.hourly:
                entry.temperature = weather_data.convert_temperature(
                    entry.temperature, old_unit, new_unit
                )
            for day in self._last_forecast.daily:
                day.min_temperature = weather_data.convert_temperature(
                    day.min_temperature, old_unit, new_unit
                )
                day.max_temperature = weather_data.convert_temperature(
                    day.max_temperature, old_unit, new_unit
                )
            self._render_forecast(self._last_forecast, new_unit)

    # ------------------------------------------------------------------
    # Background worker (runs on a separate thread)
    # ------------------------------------------------------------------

    def _fetch_weather_worker(self, location: str, unit: str) -> None:
        """Perform API calls off the main thread; post results via queue."""
        try:
            raw_current = weather_api.fetch_current_weather(location, unit)
            current = weather_data.parse_current_weather(raw_current, unit)

            raw_forecast = weather_api.fetch_forecast(location, unit)
            forecast = weather_data.parse_forecast(raw_forecast)

            icon_bytes = self._fetch_icon_bytes(current.icon_url)

            self._event_queue.put(("success", (current, forecast, icon_bytes)))
        except weather_api.WeatherAPIError as exc:
            self._event_queue.put(("error", str(exc)))
        except weather_data.WeatherDataError as exc:
            self._event_queue.put(("error", str(exc)))
        except Exception as exc:  # noqa: BLE001 - never let the GUI thread die
            logger.exception("Unexpected error during weather fetch")
            self._event_queue.put(("error", f"Unexpected error: {exc}"))

    @staticmethod
    def _fetch_icon_bytes(icon_url: str) -> Optional[bytes]:
        """
        Download the weather icon image bytes.

        Returns None (rather than raising) on any failure, so a broken
        icon never prevents the rest of the weather data from displaying.
        """
        if not icon_url:
            return None
        try:
            response = requests.get(icon_url, timeout=config.REQUEST_TIMEOUT)
            if response.ok:
                return response.content
        except requests.exceptions.RequestException:
            logger.warning("Failed to download weather icon")
        return None

    # ------------------------------------------------------------------
    # Queue polling (runs on the main / Tkinter thread)
    # ------------------------------------------------------------------

    def _poll_events(self) -> None:
        try:
            while True:
                kind, data = self._event_queue.get_nowait()
                if kind == "success":
                    current, forecast, icon_bytes = data
                    self._handle_success(current, forecast, icon_bytes)
                elif kind == "error":
                    self._handle_error(data)
        except queue.Empty:
            pass
        finally:
            self.root.after(POLL_INTERVAL_MS, self._poll_events)

    def _handle_success(
        self,
        current: weather_data.CurrentWeather,
        forecast: weather_data.Forecast,
        icon_bytes: Optional[bytes],
    ) -> None:
        self._set_busy(False)
        self._clear_error()
        self.status_var.set(f"Last updated: {current.location_name}, {current.country}")

        self._last_current = current
        self._last_forecast = forecast

        self._render_current(current)
        self._render_forecast(forecast, current.units)
        self._render_icon(icon_bytes)

    def _handle_error(self, message: str) -> None:
        self._set_busy(False)
        self.status_var.set("")
        self._show_error(message)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render_current(self, current: weather_data.CurrentWeather) -> None:
        self.location_result_var.set(f"{current.location_name}, {current.country}")
        self.temp_var.set(f"{current.temperature}{current.temperature_unit_symbol}")
        self.condition_var.set(
            f"{current.condition} - {current.description} "
            f"(feels like {current.feels_like}{current.temperature_unit_symbol})"
        )
        self.humidity_var.set(f"Humidity: {current.humidity}%")
        self.wind_var.set(f"Wind: {current.wind_speed} {current.wind_speed_unit}")
        self.pressure_var.set(f"Pressure: {current.pressure} hPa")

    def _render_forecast(self, forecast: weather_data.Forecast, unit: str) -> None:
        self.forecast_list.delete(0, tk.END)
        symbol = config.UNIT_SYMBOLS.get(unit, "")
        for day in forecast.daily:
            self.forecast_list.insert(
                tk.END,
                f"{day.date}:  {day.min_temperature}{symbol} - {day.max_temperature}{symbol}  "
                f"| {day.condition} ({day.description})",
            )

    def _render_icon(self, icon_bytes: Optional[bytes]) -> None:
        if not icon_bytes:
            self.icon_label.configure(image="")
            self._icon_image = None
            return
        try:
            image = tk.PhotoImage(data=icon_bytes)
            self._icon_image = image  # keep a reference; Tk needs it to persist
            self.icon_label.configure(image=image)
        except tk.TclError:
            # Unsupported image format or corrupt data -- fail silently,
            # the rest of the weather data is still shown.
            logger.warning("Could not render weather icon image")
            self.icon_label.configure(image="")
            self._icon_image = None

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.search_btn.configure(state=state)
        if busy:
            self.status_var.set(self.status_var.get() or "Loading...")

    def _show_error(self, message: str) -> None:
        self.error_var.set(message)

    def _clear_error(self) -> None:
        self.error_var.set("")


def main() -> None:
    """Entry point: launch the Tkinter GUI."""
    root = tk.Tk()
    WeatherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
