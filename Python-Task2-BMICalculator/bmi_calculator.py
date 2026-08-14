"""
bmi_calculator.py

Main entry point for the BMI Calculator application.

Provides:
    - BMI calculation and classification (BMICalculator class)
    - Validated terminal input helpers
    - An interactive terminal menu that ties together history,
      statistics, unit conversion, and CSV export.

Run this file directly to start the application:
    python bmi_calculator.py
"""

from datetime import datetime
from typing import Optional

import config
import unit_converter
import statistics as bmi_statistics  # local statistics.py, not the stdlib module
from bmi_history import BMIHistory
from logger import get_logger

logger = get_logger(__name__)


class BMICalculator:
    """Encapsulates the core BMI calculation and classification logic."""

    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """
        Calculate BMI from weight in kilograms and height in centimeters.

        BMI = weight (kg) / (height (m) ** 2)

        :raises ValueError: if weight or height is not a positive number.
        """
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than zero.")
        if height_cm <= 0:
            raise ValueError("Height must be greater than zero.")

        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, config.BMI_PRECISION)

    @staticmethod
    def classify_bmi(bmi: float) -> str:
        """Return the BMI category name for a given BMI value."""
        for lower, upper, label in config.BMI_CATEGORIES:
            if lower <= bmi < upper:
                return label
        # Should not be reached given the category ranges cover [0, inf)
        return "Unknown"


# ==========================================================================
# Validated input helpers
# ==========================================================================

def prompt_positive_float(prompt: str) -> float:
    """
    Repeatedly prompt the user until a valid positive float is entered.

    Rejects empty input, non-numeric input, zero, and negative values.
    """
    while True:
        raw = input(prompt).strip()

        if raw == "":
            print("  Input cannot be empty. Please enter a number.")
            continue

        try:
            value = float(raw)
        except ValueError:
            print("  Invalid input. Please enter a numeric value (e.g. 70 or 70.5).")
            continue

        if value == 0:
            print("  Value cannot be zero. Please enter a positive number.")
            continue

        if value < 0:
            print("  Value cannot be negative. Please enter a positive number.")
            continue

        return value


def prompt_non_empty_text(prompt: str) -> str:
    """Repeatedly prompt until the user enters non-empty text."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print("  This field cannot be empty.")
            continue
        return raw


def prompt_units() -> str:
    """Prompt the user to choose a unit system."""
    print("  1. Metric (kilograms, centimeters)")
    print("  2. Imperial (pounds, inches)")
    while True:
        choice = input("  Select units [1-2]: ").strip()
        if choice == "1":
            return config.UNIT_METRIC
        elif choice == "2":
            return config.UNIT_IMPERIAL
        else:
            print("  Invalid choice. Please enter 1 or 2.")


def prompt_yes_no(prompt: str) -> bool:
    """Prompt for a yes/no confirmation. Returns True for yes."""
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  Please answer 'y' or 'n'.")


# ==========================================================================
# Application
# ==========================================================================

class BMIApp:
    """Ties together the calculator, history, statistics, and terminal UI."""

    def __init__(self):
        config.ensure_directories()
        self.history = BMIHistory(config.DATA_FILE)

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the interactive menu loop."""
        logger.info("Application started.")
        print(f"Welcome to the {config.APP_NAME}!")

        while True:
            self._print_menu()
            choice = input("Select an option [1-8]: ").strip()

            if choice == "1":
                self.calculate_bmi_flow()
            elif choice == "2":
                self.view_history()
            elif choice == "3":
                self.view_progress()
            elif choice == "4":
                self.view_statistics()
            elif choice == "5":
                self.export_history()
            elif choice == "6":
                self.change_units_info()
            elif choice == "7":
                self.clear_history()
            elif choice == "8":
                print("\nThank you for using the BMI Calculator. Goodbye!")
                logger.info("Application exited normally.")
                break
            else:
                print("Invalid option. Please choose a number from 1 to 8.\n")

    @staticmethod
    def _print_menu() -> None:
        print("\n========== BMI CALCULATOR ==========")
        print("1. Calculate BMI")
        print("2. View BMI History")
        print("3. View Progress")
        print("4. View Statistics")
        print("5. Export History")
        print("6. Change Units")
        print("7. Clear History")
        print("8. Exit")
        print("=====================================")

    # ------------------------------------------------------------------
    def calculate_bmi_flow(self) -> None:
        """Guide the user through entering data and calculating a BMI."""
        print("\n--- Calculate BMI ---")
        name = prompt_non_empty_text("Enter your name: ")
        units = prompt_units()

        if units == config.UNIT_METRIC:
            weight = prompt_positive_float("Enter weight (kg): ")
            height = prompt_positive_float("Enter height (cm): ")
        else:
            weight = prompt_positive_float("Enter weight (lb): ")
            height = prompt_positive_float("Enter height (in): ")

        try:
            weight_kg, height_cm = unit_converter.to_metric(weight, height, units)
            bmi = BMICalculator.calculate_bmi(weight_kg, height_cm)
            category = BMICalculator.classify_bmi(bmi)
        except ValueError as exc:
            print(f"  Could not calculate BMI: {exc}")
            logger.error("BMI calculation failed: %s", exc)
            return

        now = datetime.now()
        record = {
            "name": name,
            "weight": weight,
            "height": height,
            "units": units,
            "weight_kg": round(weight_kg, 2),
            "height_cm": round(height_cm, 2),
            "bmi": bmi,
            "category": category,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
        }

        self._print_result(record)

        previous = self.history.get_last(name)

        saved = self.history.add_record(record)
        if not saved:
            print("  Warning: the record could not be saved to history.")

        if previous is not None:
            trend = bmi_statistics.compare_bmi(bmi, previous["bmi"])
            print(f"Compared to your previous BMI ({previous['bmi']}), your BMI has {trend}.")

        if prompt_yes_no("Would you like to set/compare a target BMI? [y/n]: "):
            target = prompt_positive_float("Enter your target BMI: ")
            diff = bmi_statistics.target_difference(bmi, target)
            if diff > 0:
                print(f"You are {abs(diff)} above your target BMI.")
            elif diff < 0:
                print(f"You are {abs(diff)} below your target BMI.")
            else:
                print("You have reached your target BMI!")

    @staticmethod
    def _print_result(record: dict) -> None:
        unit_label = "kg" if record["units"] == config.UNIT_METRIC else "lb"
        height_label = "cm" if record["units"] == config.UNIT_METRIC else "in"

        print("\n========================================")
        print("BMI CALCULATION")
        print()
        print(f"Name: {record['name']}")
        print(f"Weight: {record['weight']} {unit_label}")
        print(f"Height: {record['height']} {height_label}")
        print(f"BMI: {record['bmi']}")
        print(f"Category: {record['category']}")
        print("========================================")

    # ------------------------------------------------------------------
    def view_history(self) -> None:
        print("\n--- BMI History ---")
        records = self.history.get_all()
        if not records:
            print("No BMI records found yet.")
            return

        for i, r in enumerate(records, start=1):
            print(f"{i}. {r.get('date')} {r.get('time')} | {r.get('name')} | "
                  f"Weight: {r.get('weight')} | Height: {r.get('height')} | "
                  f"BMI: {r.get('bmi')} | Category: {r.get('category')}")

    # ------------------------------------------------------------------
    def view_progress(self) -> None:
        print("\n--- BMI Progress ---")
        name = prompt_non_empty_text("Enter your name to view progress: ")
        records = self.history.get_by_name(name)

        if not records:
            print(f"No history found for '{name}'.")
            return

        if len(records) == 1:
            print(f"Only one record found for '{name}'. Need at least two to show progress.")
            print(f"Current BMI: {records[-1]['bmi']} ({records[-1]['category']})")
            return

        print(f"Progress for {name}:")
        for i in range(1, len(records)):
            prev, curr = records[i - 1], records[i]
            trend = bmi_statistics.compare_bmi(curr["bmi"], prev["bmi"])
            print(f"  {prev['date']} -> {curr['date']}: "
                  f"{prev['bmi']} -> {curr['bmi']} ({trend})")

    # ------------------------------------------------------------------
    def view_statistics(self) -> None:
        print("\n--- BMI Statistics ---")
        stats = bmi_statistics.calculate_statistics(self.history.get_all())
        if stats is None:
            print("No records available to calculate statistics.")
            return

        print(f"Number of records: {stats['count']}")
        print(f"Average BMI: {stats['average']}")
        print(f"Lowest BMI: {stats['lowest']}")
        print(f"Highest BMI: {stats['highest']}")
        print(f"Latest BMI: {stats['latest']}")

    # ------------------------------------------------------------------
    def export_history(self) -> None:
        print("\n--- Export History ---")
        success = self.history.export_to_csv(config.EXPORT_FILE)
        if success:
            print(f"History exported successfully to: {config.EXPORT_FILE}")
        else:
            print("Export failed. There may be no records to export, or a file error occurred.")

    # ------------------------------------------------------------------
    def change_units_info(self) -> None:
        print("\n--- Units ---")
        print("Units are selected each time you calculate a BMI.")
        print("Supported units:")
        print("  - Metric: kilograms (kg) and centimeters (cm)")
        print("  - Imperial: pounds (lb) and inches (in)")

    # ------------------------------------------------------------------
    def clear_history(self) -> None:
        print("\n--- Clear History ---")
        if not self.history.get_all():
            print("History is already empty.")
            return

        confirmed = prompt_yes_no(
            "Are you sure you want to delete ALL BMI history? This cannot be undone. [y/n]: "
        )
        if confirmed:
            success = self.history.clear()
            if success:
                print("History cleared successfully.")
            else:
                print("Failed to clear history due to a file error.")
        else:
            print("Clear history cancelled.")


def main() -> None:
    app = BMIApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Goodbye!")
        logger.info("Application interrupted by KeyboardInterrupt.")
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        print(f"\nAn unexpected error occurred: {exc}")
        print("The error has been logged. Please restart the application.")


if __name__ == "__main__":
    main()
