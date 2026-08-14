"""
bmi_history.py

Manages persistence of BMI records: loading from and saving to a JSON
file, appending new records, clearing history, and exporting to CSV.

The BMIHistory class is deliberately independent of the terminal UI so
it can be reused (and unit tested) without any user interaction.
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional

from logger import get_logger

logger = get_logger(__name__)


class BMIHistory:
    """Handles loading, saving, and querying of stored BMI records."""

    def __init__(self, data_file: str):
        self.data_file = data_file
        self.records: List[Dict[str, Any]] = []
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def load(self) -> None:
        """
        Load records from the JSON data file into memory.

        Handles a missing file (starts with an empty history) and a
        corrupted/unreadable file (logs the error, starts empty, and
        does not crash the application).
        """
        if not os.path.exists(self.data_file):
            self.records = []
            logger.info("No existing history file found; starting fresh.")
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                self.records = json.loads(content) if content else []
            if not isinstance(self.records, list):
                raise ValueError("History file does not contain a list of records.")
            logger.info("Loaded %d record(s) from history file.", len(self.records))
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            logger.error("Failed to load history file (%s). Starting with empty history.", exc)
            self.records = []

    def save(self) -> bool:
        """
        Persist the current in-memory records to the JSON data file.

        :return: True on success, False if saving failed.
        """
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4)
            logger.info("Saved %d record(s) to history file.", len(self.records))
            return True
        except OSError as exc:
            logger.error("Failed to save history file: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Record management
    # ------------------------------------------------------------------
    def add_record(self, record: Dict[str, Any]) -> bool:
        """Append a new record and persist it. Returns True on success."""
        self.records.append(record)
        return self.save()

    def get_all(self) -> List[Dict[str, Any]]:
        """Return all stored records (most recent last)."""
        return self.records

    def get_last(self, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Return the most recent record, optionally filtered by user name.
        Returns None if there is no matching record.
        """
        pool = self.records
        if name is not None:
            pool = [r for r in self.records if r.get("name", "").lower() == name.lower()]
        return pool[-1] if pool else None

    def get_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Return all records belonging to a given user name."""
        return [r for r in self.records if r.get("name", "").lower() == name.lower()]

    def clear(self) -> bool:
        """Delete all stored records. Returns True on success."""
        self.records = []
        success = self.save()
        if success:
            logger.info("History cleared by user.")
        return success

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def export_to_csv(self, export_file: str) -> bool:
        """
        Export all records to a CSV file.

        :return: True on success, False if export failed or there is
                 nothing to export.
        """
        if not self.records:
            logger.warning("Export requested but history is empty.")
            return False

        fieldnames = [
            "name", "weight", "height", "units",
            "weight_kg", "height_cm", "bmi", "category", "date", "time",
        ]

        try:
            os.makedirs(os.path.dirname(export_file), exist_ok=True)
            with open(export_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                for record in self.records:
                    writer.writerow(record)
            logger.info("Exported %d record(s) to CSV.", len(self.records))
            return True
        except OSError as exc:
            logger.error("Failed to export history to CSV: %s", exc)
            return False
