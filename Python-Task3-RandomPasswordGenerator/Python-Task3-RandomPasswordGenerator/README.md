# Random Password Generator

**OASIS INFOBYTE Python Programming Internship — Task 3**

A professional, secure, and well-tested Random Password Generator built in
Python. It provides both a command-line interface (CLI) and a graphical
user interface (GUI), with password strength analysis, optional history
tracking, and clipboard support — all built on cryptographically secure
randomness via Python's `secrets` module.

---

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Dependency Installation](#dependency-installation)
- [CLI Usage](#cli-usage)
- [GUI Usage](#gui-usage)
- [Testing](#testing)
- [Example Commands](#example-commands)
- [Security Considerations](#security-considerations)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Project Description

This project was developed as **Task 3** of the OASIS INFOBYTE Python
Programming Internship (OIBSIP). It implements a Random Password Generator
that lets users generate one or more strong, customizable passwords, review
their strength, optionally save generation metadata to a local history
file, and copy generated passwords to the clipboard — through either a
terminal-based CLI or a Tkinter desktop GUI.

The project emphasizes modular design, input validation, graceful error
handling, and security best practices suitable for a GitHub portfolio and
internship evaluation.

## Features

- **Secure password generation** using Python's `secrets` module (never
  `random`), with user-defined length and character-set selection
  (uppercase, lowercase, numbers, special characters).
- **Guaranteed character diversity** — generated passwords always include
  at least one character from every selected character set.
- **Password strength analysis** rating passwords as `Weak`, `Moderate`,
  `Strong`, or `Very Strong`, with actionable feedback for improvement.
- **Password history** stored in JSON, recording generation timestamp,
  password length, and strength — **not** the password itself, unless
  explicitly requested — with safe handling of missing or corrupted
  history files.
- **Clipboard support** via `pyperclip`, fully isolated from core password
  logic, with graceful handling of systems that have no clipboard backend.
- **Command-line interface** with rich options and clear `--help` output.
- **Tkinter GUI** with length input, character-type checkboxes, strength
  indicator, copy button, history viewer, and clear-history option.
- **Centralized configuration** (`config.py`) — no hardcoded constants
  scattered across modules.
- **Structured logging** of application events, generation metadata, and
  errors — **passwords are never written to the log file**.
- **Automated test suite** (39 tests) covering generation, strength
  analysis, history, clipboard, configuration, and error handling.

## Technologies

- Python 3.10+
- `secrets` — cryptographically secure password generation
- `tkinter` / `ttk` — graphical user interface
- `argparse` — command-line interface
- `json` — password history persistence
- `logging` — application and audit logging
- `pyperclip` — clipboard integration
- `unittest` — automated testing

## Project Structure

```
Python-Task3-RandomPasswordGenerator/
│
├── main.py                    # CLI entry point
├── password_generator.py      # Secure password generation logic
├── password_strength.py       # Password strength analysis
├── password_history.py        # JSON-based history management
├── clipboard_manager.py       # Clipboard support (isolated from core logic)
├── config.py                  # Centralized configuration/constants
├── logger.py                  # Application logging setup
├── gui.py                     # Tkinter GUI
├── tests.py                   # Automated test suite
├── requirements.txt           # External dependencies
├── README.md                  # Project documentation
│
├── data/
│   └── password_history.json  # Generated at runtime (not password text)
│
├── logs/
│   └── password_generator.log # Generated at runtime
│
└── screenshots/                # GUI/CLI screenshots for documentation
```

## Installation

Clone the repository (or copy the project folder) and navigate into it:

```bash
git clone https://github.com/<your-username>/OIBSIP.git
cd OIBSIP/Python-Task3-RandomPasswordGenerator
```

## Virtual Environment Setup

It is recommended to use a virtual environment:

```bash
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

## Dependency Installation

```bash
pip install -r requirements.txt
```

> **Note:** `tkinter` ships with most standard Python installations. On
> some Linux distributions it must be installed separately, e.g.:
> `sudo apt-get install python3-tk`

## CLI Usage

Run `main.py` with the desired options:

```bash
python main.py [OPTIONS]
```

| Option              | Description                                             |
|---------------------|-----------------------------------------------------------|
| `--length N`        | Password length (default: 12)                             |
| `--count N`         | Number of passwords to generate (default: 1)               |
| `--no-uppercase`    | Exclude uppercase letters                                  |
| `--no-lowercase`    | Exclude lowercase letters                                  |
| `--no-numbers`      | Exclude numbers                                             |
| `--no-special`      | Exclude special characters                                  |
| `--strength`        | Show strength analysis for each generated password          |
| `--copy`            | Copy the generated password to the clipboard (single password only) |
| `--save-history`    | Save generation metadata (not the password) to history       |
| `--history`         | View saved password history                                 |
| `--clear-history`   | Clear all saved password history                            |
| `--gui`             | Launch the graphical interface instead of the CLI            |
| `-h`, `--help`      | Show help information                                       |

View full help at any time:

```bash
python main.py --help
```

## GUI Usage

Launch the graphical interface:

```bash
python main.py --gui
```

In the GUI you can:
1. Set the password length and number of passwords.
2. Choose which character types to include via checkboxes.
3. Click **Generate** to create a password.
4. View the live **strength indicator** (color-coded).
5. Click **Copy to Clipboard** to copy the result.
6. Click **View History** to see previously generated password metadata.
7. Click **Clear History** to permanently erase saved history (with confirmation).
8. Click **Clear** to reset the display.

## Testing

Run the full automated test suite:

```bash
python tests.py
```

The suite reports a clear pass/fail summary, including total tests run,
number passed, and number failed, using Python's built-in `unittest`
framework.

## Example Commands

```bash
# Generate 3 passwords of length 16
python main.py --length 16 --count 3

# Generate a 20-character password without special characters, with strength info
python main.py --length 20 --no-special --strength

# Generate a password and copy it to the clipboard
python main.py --length 18 --copy

# Generate and save metadata to history
python main.py --length 14 --save-history

# View password history
python main.py --history

# Clear password history
python main.py --clear-history

# Launch the GUI
python main.py --gui
```

## Security Considerations

- Passwords are generated exclusively using Python's `secrets` module,
  which is designed for cryptographic use, **not** the `random` module.
- Generated passwords are shuffled using a `secrets`-based Fisher-Yates
  shuffle to avoid predictable character positioning.
- Passwords are **never written to the log file** — only non-sensitive
  metadata (length, count, strength rating) is logged.
- Password history stores metadata only by default; raw password text is
  only persisted if a caller explicitly opts in (`store_password=True`),
  which the CLI and GUI do not do by default.
- A missing or corrupted history file is handled gracefully and never
  crashes the application or exposes a stack trace to the end user.
- Clipboard operations are isolated in their own module and fail safely
  (returning `False`/showing a warning) rather than raising unhandled
  exceptions when no clipboard backend is available.
- All user input (length, count, character-set selection) is validated
  before use, with clear, specific error messages.

## Screenshots

Screenshots of the CLI and GUI in action are provided in the
[`screenshots/`](./screenshots) directory.

## Future Improvements

- Add password expiration reminders.
- Add an option to exclude ambiguous characters (e.g. `l`, `1`, `O`, `0`).
- Add passphrase-style generation (word-based passwords).
- Add encrypted history storage (e.g. via a master password).
- Package the project for distribution via `pip`/PyPI.
- Add dark mode theming to the GUI.

## Author

Developed as part of the **OASIS INFOBYTE Python Programming Internship**
(OIBSIP) — Task 3: Random Password Generator.
