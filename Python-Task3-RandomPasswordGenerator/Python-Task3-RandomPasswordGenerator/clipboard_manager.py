"""
clipboard_manager.py
---------------------
Clipboard support for copying generated passwords.

This module is intentionally kept separate from password generation logic
so that clipboard functionality (and its potential failure modes, e.g. no
clipboard available in headless / CI environments) never affects the core
password generation or strength analysis features.

Uses pyperclip where available. If pyperclip is not installed or the
system has no accessible clipboard mechanism, failures are handled
gracefully and reported back to the caller instead of raising unhandled
exceptions.
"""

from logger import log_clipboard_event, log_error

try:
    import pyperclip

    _PYPERCLIP_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when dependency missing
    _PYPERCLIP_AVAILABLE = False


class ClipboardError(Exception):
    """Raised when a clipboard operation fails."""


def copy_to_clipboard(text: str) -> bool:
    """
    Copy the given text to the system clipboard.

    Args:
        text: The text (typically a generated password) to copy.

    Returns:
        True if the copy succeeded, False otherwise. Never raises for
        expected clipboard failure modes; those are logged and reported
        via the return value instead.
    """
    if not isinstance(text, str) or text == "":
        log_error("Attempted to copy an empty or invalid value to clipboard.")
        return False

    if not _PYPERCLIP_AVAILABLE:
        log_clipboard_event("copy", success=False)
        log_error("pyperclip is not installed; clipboard copy unavailable.")
        return False

    try:
        pyperclip.copy(text)
        log_clipboard_event("copy", success=True)
        return True
    except Exception as exc:  # pyperclip raises varied backend-specific errors
        log_clipboard_event("copy", success=False)
        log_error(f"Clipboard copy failed: {exc}")
        return False


def clear_clipboard() -> bool:
    """
    Clear the system clipboard by copying an empty string to it.

    Returns:
        True if the clear succeeded, False otherwise.
    """
    if not _PYPERCLIP_AVAILABLE:
        log_clipboard_event("clear", success=False)
        return False

    try:
        pyperclip.copy("")
        log_clipboard_event("clear", success=True)
        return True
    except Exception as exc:
        log_clipboard_event("clear", success=False)
        log_error(f"Clipboard clear failed: {exc}")
        return False


def is_clipboard_available() -> bool:
    """
    Check whether clipboard functionality is available on this system.

    Returns:
        True if pyperclip is installed and a working clipboard backend was
        detected, False otherwise.
    """
    if not _PYPERCLIP_AVAILABLE:
        return False
    try:
        # paste() will raise if no backend is available (e.g. headless
        # Linux without xclip/xsel installed).
        pyperclip.paste()
        return True
    except Exception:
        return False
