"""
password_history.py
--------------------
Password history management using a local JSON file.

Stores metadata about generated passwords (timestamp, length, strength).
By default, the actual password value is NOT stored, in keeping with the
security principle of avoiding unnecessary storage of sensitive data.
Callers may opt in to storing the password value itself via the
`store_password` flag, but this is off by default.

The module handles a missing or corrupted history file gracefully by
treating it as an empty history rather than crashing the application.
"""

import json
import os
from datetime import datetime

import config
from logger import log_error, log_history_event


class PasswordHistoryError(Exception):
    """Raised for unrecoverable password history operations."""


class PasswordHistoryManager:
    """Manages reading, writing, and clearing the password history file."""

    def __init__(self, history_file: str = config.HISTORY_FILE):
        self.history_file = history_file
        config.ensure_directories()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _read_raw(self) -> list:
        """
        Read the raw list of history entries from disk.

        Handles a missing file (returns empty list) and a corrupted /
        unparseable file (logs the error, returns empty list, and does NOT
        raise) so that a damaged history file never crashes the app.

        Returns:
            A list of history entry dictionaries.
        """
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
                if not isinstance(data, list):
                    log_error("History file content is not a list; resetting history.")
                    return []
                return data
        except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
            log_error(f"Failed to read history file ({exc}); treating as empty history.")
            return []

    def _write_raw(self, entries: list) -> None:
        """
        Write the given list of entries to the history file atomically.

        Args:
            entries: The full list of history entries to persist.

        Raises:
            PasswordHistoryError: If the file cannot be written.
        """
        try:
            tmp_path = f"{self.history_file}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, indent=2)
            os.replace(tmp_path, self.history_file)
        except OSError as exc:
            log_error(f"Failed to write history file: {exc}")
            raise PasswordHistoryError(f"Could not write history file: {exc}") from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add_entry(
        self,
        length: int,
        strength: str,
        password: str = None,
        store_password: bool = False,
    ) -> dict:
        """
        Add a new entry to the password history.

        Args:
            length: The length of the generated password.
            strength: The strength rating of the generated password.
            password: The actual password value (only stored if
                store_password is True).
            store_password: Whether to persist the actual password text.
                Defaults to False to avoid unnecessarily exposing sensitive
                data in the history file.

        Returns:
            The entry dictionary that was added.
        """
        entries = self._read_raw()

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "length": length,
            "strength": strength,
        }
        if store_password and password is not None:
            entry["password"] = password

        entries.append(entry)

        # Trim to the configured maximum, keeping the most recent entries.
        if len(entries) > config.MAX_HISTORY_ENTRIES:
            entries = entries[-config.MAX_HISTORY_ENTRIES :]

        self._write_raw(entries)
        log_history_event("entry added")
        return entry

    def get_history(self) -> list:
        """
        Retrieve all password history entries.

        Returns:
            A list of history entry dictionaries, most recent last.
        """
        entries = self._read_raw()
        log_history_event("history viewed")
        return entries

    def clear_history(self) -> None:
        """Clear all entries from the password history file."""
        self._write_raw([])
        log_history_event("history cleared")

    def count(self) -> int:
        """Return the number of entries currently stored in history."""
        return len(self._read_raw())
