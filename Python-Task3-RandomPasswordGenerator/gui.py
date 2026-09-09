"""
gui.py
------
Tkinter-based graphical user interface for the Random Password Generator.

This module is purely presentational: it delegates all business logic
(password generation, strength analysis, history, clipboard) to the
respective core modules. No password generation or validation logic lives
here, keeping the GUI cleanly separated from the application's core logic.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import config
from password_generator import PasswordGenerator, PasswordGenerationError
from password_strength import PasswordStrengthAnalyzer
from password_history import PasswordHistoryManager
from clipboard_manager import copy_to_clipboard, is_clipboard_available
from logger import log_startup, log_shutdown, log_password_generated, log_error


class PasswordGeneratorGUI:
    """Main application window for the Random Password Generator GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("480x560")
        self.root.resizable(False, False)

        self.history_manager = PasswordHistoryManager()
        self._last_password = None

        self._build_widgets()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_widgets(self) -> None:
        """Build and lay out all widgets in the main window."""
        padding = {"padx": 12, "pady": 6}

        title_label = ttk.Label(
            self.root, text="Random Password Generator", font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(16, 8))

        # --- Length input ---
        length_frame = ttk.Frame(self.root)
        length_frame.pack(fill="x", **padding)

        ttk.Label(length_frame, text="Password Length:").pack(side="left")
        self.length_var = tk.IntVar(value=config.DEFAULT_PASSWORD_LENGTH)
        length_spin = ttk.Spinbox(
            length_frame,
            from_=config.MIN_PASSWORD_LENGTH,
            to=config.MAX_PASSWORD_LENGTH,
            textvariable=self.length_var,
            width=6,
        )
        length_spin.pack(side="right")

        # --- Count input ---
        count_frame = ttk.Frame(self.root)
        count_frame.pack(fill="x", **padding)

        ttk.Label(count_frame, text="Number of Passwords:").pack(side="left")
        self.count_var = tk.IntVar(value=1)
        count_spin = ttk.Spinbox(
            count_frame, from_=1, to=config.MAX_COUNT, textvariable=self.count_var, width=6
        )
        count_spin.pack(side="right")

        # --- Character type checkboxes ---
        options_frame = ttk.LabelFrame(self.root, text="Character Types")
        options_frame.pack(fill="x", **padding)

        self.use_uppercase = tk.BooleanVar(value=config.DEFAULT_USE_UPPERCASE)
        self.use_lowercase = tk.BooleanVar(value=config.DEFAULT_USE_LOWERCASE)
        self.use_numbers = tk.BooleanVar(value=config.DEFAULT_USE_NUMBERS)
        self.use_special = tk.BooleanVar(value=config.DEFAULT_USE_SPECIAL)

        ttk.Checkbutton(
            options_frame, text="Uppercase (A-Z)", variable=self.use_uppercase
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Checkbutton(
            options_frame, text="Lowercase (a-z)", variable=self.use_lowercase
        ).pack(anchor="w", padx=8, pady=2)
        ttk.Checkbutton(options_frame, text="Numbers (0-9)", variable=self.use_numbers).pack(
            anchor="w", padx=8, pady=2
        )
        ttk.Checkbutton(
            options_frame, text="Special Characters (!@#$...)", variable=self.use_special
        ).pack(anchor="w", padx=8, pady=2)

        # --- Buttons: Generate / Clear ---
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", **padding)

        ttk.Button(button_frame, text="Generate", command=self.on_generate).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(button_frame, text="Clear", command=self.on_clear).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        # --- Password display ---
        display_frame = ttk.LabelFrame(self.root, text="Generated Password")
        display_frame.pack(fill="x", **padding)

        self.password_var = tk.StringVar(value="")
        password_entry = ttk.Entry(
            display_frame, textvariable=self.password_var, font=("Consolas", 12), state="readonly"
        )
        password_entry.pack(fill="x", padx=8, pady=8)

        # --- Strength indicator ---
        self.strength_var = tk.StringVar(value="Strength: N/A")
        self.strength_label = ttk.Label(
            self.root, textvariable=self.strength_var, font=("Segoe UI", 11, "bold")
        )
        self.strength_label.pack(**padding)

        # --- Copy / History buttons ---
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", **padding)

        ttk.Button(action_frame, text="Copy to Clipboard", command=self.on_copy).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(action_frame, text="View History", command=self.on_view_history).pack(
            side="left", expand=True, fill="x", padx=(4, 0)
        )

        ttk.Button(self.root, text="Clear History", command=self.on_clear_history).pack(
            fill="x", padx=12, pady=(0, 10)
        )

        # --- Status bar for error messages / confirmations ---
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief="sunken", anchor="w"
        )
        status_bar.pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def on_generate(self) -> None:
        """Handle the Generate button click: create a new password."""
        try:
            length = self.length_var.get()
        except tk.TclError:
            self._show_error("Password length must be a valid integer.")
            return

        try:
            generator = PasswordGenerator(
                length=length,
                use_uppercase=self.use_uppercase.get(),
                use_lowercase=self.use_lowercase.get(),
                use_numbers=self.use_numbers.get(),
                use_special=self.use_special.get(),
            )
            password = generator.generate()
        except PasswordGenerationError as exc:
            self._show_error(str(exc))
            return
        except Exception as exc:  # unexpected failure safety net
            log_error(f"Unexpected GUI generation error: {exc}")
            self._show_error("An unexpected error occurred while generating the password.")
            return

        self._last_password = password
        self.password_var.set(password)

        result = PasswordStrengthAnalyzer.analyze(password)
        self.strength_var.set(f"Strength: {result.rating} (score {result.score}/7)")
        self._set_strength_color(result.rating)

        self.history_manager.add_entry(length=len(password), strength=result.rating)
        log_password_generated(length=length, count=1, strength=result.rating)

        self.status_var.set("Password generated successfully.")

    def on_clear(self) -> None:
        """Handle the Clear button click: reset the password display."""
        self._last_password = None
        self.password_var.set("")
        self.strength_var.set("Strength: N/A")
        self.strength_label.configure(foreground="black")
        self.status_var.set("Cleared.")

    def on_copy(self) -> None:
        """Handle the Copy to Clipboard button click."""
        if not self._last_password:
            self._show_error("No password to copy. Generate one first.")
            return

        if not is_clipboard_available():
            self._show_error("No clipboard mechanism is available on this system.")
            return

        success = copy_to_clipboard(self._last_password)
        if success:
            self.status_var.set("Password copied to clipboard.")
        else:
            self._show_error("Failed to copy password to clipboard.")

    def on_view_history(self) -> None:
        """Open a new window displaying stored password history."""
        entries = self.history_manager.get_history()

        history_window = tk.Toplevel(self.root)
        history_window.title("Password History")
        history_window.geometry("420x360")

        if not entries:
            ttk.Label(history_window, text="No password history found.").pack(pady=20)
            return

        columns = ("timestamp", "length", "strength")
        tree = ttk.Treeview(history_window, columns=columns, show="headings")
        tree.heading("timestamp", text="Timestamp")
        tree.heading("length", text="Length")
        tree.heading("strength", text="Strength")
        tree.column("timestamp", width=190)
        tree.column("length", width=60, anchor="center")
        tree.column("strength", width=110, anchor="center")

        for entry in entries:
            tree.insert(
                "",
                "end",
                values=(
                    entry.get("timestamp", "unknown"),
                    entry.get("length", "?"),
                    entry.get("strength", "?"),
                ),
            )
        tree.pack(fill="both", expand=True, padx=8, pady=8)

    def on_clear_history(self) -> None:
        """Handle the Clear History button click, with confirmation."""
        confirmed = messagebox.askyesno(
            "Confirm Clear History",
            "Are you sure you want to permanently clear all password history?",
        )
        if confirmed:
            self.history_manager.clear_history()
            self.status_var.set("Password history cleared.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _show_error(self, message: str) -> None:
        """Display an error message to the user and update the status bar."""
        self.status_var.set(f"Error: {message}")
        messagebox.showerror("Error", message)

    def _set_strength_color(self, rating: str) -> None:
        """Set the strength label's text color based on the rating."""
        colors = {
            "Weak": "#c0392b",
            "Moderate": "#d68910",
            "Strong": "#27ae60",
            "Very Strong": "#1e8449",
        }
        self.strength_label.configure(foreground=colors.get(rating, "black"))


def launch_gui() -> None:
    """Create the Tk root window and start the GUI main loop."""
    log_startup()
    root = tk.Tk()
    app = PasswordGeneratorGUI(root)
    try:
        root.mainloop()
    finally:
        log_shutdown()


if __name__ == "__main__":
    launch_gui()
