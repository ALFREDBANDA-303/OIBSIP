# Python-Task2-BMICalculator

## Internship Information

- **Program:** Oasis Infobyte Python Programming Internship
- **Level:** 3
- **Task:** Task 2 — BMI Calculator
- **Repository:** `OIBSIP/Python-Task2-BMICalculator`

## Project Description

A complete, terminal-based BMI (Body Mass Index) management application
written in Python. Rather than a one-off formula script, this project
calculates BMI, classifies the result, stores a history of records per
user, tracks progress over time, supports both metric and imperial
units, validates all user input, computes summary statistics, exports
data to CSV, and ships with an automated test suite and logging.

## Objectives

- Calculate BMI accurately from weight and height.
- Classify BMI into standard health categories.
- Persist a history of every calculation, per user.
- Track how a user's BMI changes over time.
- Support both metric and imperial measurements.
- Validate all input defensively so the program never crashes.
- Provide statistics (average, lowest, highest, latest BMI).
- Export stored history to CSV.
- Log key events and errors to a file.
- Cover core logic with automated, non-interactive tests.

## Features

- **Interactive terminal menu** with 8 options (calculate, view history,
  view progress, view statistics, export, units info, clear history, exit).
- **BMI calculation** to 2 decimal places.
- **BMI classification** into Underweight / Normal weight / Overweight / Obesity.
- **Input validation**: rejects empty input, non-numeric input, zero,
  and negative values, and re-prompts the user instead of crashing.
- **Named user profiles**: every record is tied to a name.
- **Persistent JSON history** (`data/bmi_history.json`), loaded on startup.
- **History viewer** showing name, date, weight, height, BMI, and category.
- **Clear history** option with a yes/no confirmation prompt.
- **Metric and imperial unit support** (kg/cm and lb/in), converted
  through a dedicated `unit_converter.py` module.
- **BMI comparison**: reports whether the latest BMI increased,
  decreased, or stayed the same compared to the user's previous result.
- **Progress tracking**: shows the trend across all of a user's saved
  records.
- **Target BMI**: optionally enter a target BMI and see the difference
  from your current result.
- **Statistics**: record count, average, lowest, highest, and latest BMI.
- **CSV export** (`exports/bmi_history.csv`) of the full history.
- **Logging** of application events and errors to
  `logs/bmi_calculator.log` (no sensitive data is logged unnecessarily).
- **Robust error handling** for missing files, corrupted JSON, invalid
  input, and export failures — the application keeps running.
- **Automated test suite** (`tests.py`, 40 tests, `unittest`-based, no
  manual interaction required).

## BMI Formula

```
BMI = weight (kg) / (height (m) ** 2)
```

Imperial input (pounds and inches) is converted to kilograms and
centimeters before this formula is applied.

## BMI Categories

| BMI Range        | Category       |
|-------------------|----------------|
| Below 18.5         | Underweight    |
| 18.5 – 24.9         | Normal weight  |
| 25.0 – 29.9         | Overweight     |
| 30.0 and above      | Obesity        |

## Supported Units

- **Metric:** kilograms (kg) and centimeters (cm)
- **Imperial:** pounds (lb) and inches (in)

Conversions use standard factors (1 lb = 0.45359237 kg, 1 in = 2.54 cm)
and live in `unit_converter.py`.

## Project Structure

```
Python-Task2-BMICalculator/
│
├── bmi_calculator.py     # Main application: menu, calculation, validated input
├── bmi_history.py        # JSON history storage, retrieval, and CSV export
├── unit_converter.py     # Metric <-> imperial conversion logic
├── statistics.py         # BMI statistics (count, average, min, max, latest)
├── config.py             # Paths and application settings
├── logger.py             # Centralized logging configuration
├── tests.py              # Automated, non-interactive test suite
├── README.md
├── requirements.txt
│
├── data/
│   └── bmi_history.json  # Persisted BMI records (created automatically)
│
├── exports/
│   └── bmi_history.csv   # CSV export output (created on export)
│
└── logs/
    └── bmi_calculator.log  # Application log (created automatically)
```

## Installation

1. Ensure Python 3.8+ is installed.
2. Clone or download the `OIBSIP` repository and navigate into this project:

```bash
git clone https://github.com/<your-username>/OIBSIP.git
cd OIBSIP/Python-Task2-BMICalculator
```

### Virtual Environment (recommended)

```bash
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

No external packages are required (see `requirements.txt`), but the
virtual environment keeps the project isolated.

## How to Run the Program

```bash
python bmi_calculator.py
```

You will see the main menu:

```
========== BMI CALCULATOR ==========
1. Calculate BMI
2. View BMI History
3. View Progress
4. View Statistics
5. Export History
6. Change Units
7. Clear History
8. Exit
=====================================
```

Select an option by typing its number and pressing Enter. After each
operation, the menu is shown again so you can perform multiple actions
without restarting the program.

## How to Run Tests

```bash
python tests.py
```

or, equivalently:

```bash
python -m unittest tests.py -v
```

The suite includes 40 tests covering BMI calculation, classification,
zero/negative/invalid input handling, unit conversion, history storage
and retrieval, statistics, and CSV export. All tests run without any
manual interaction and use temporary files so your real
`data/bmi_history.json` is never touched by the test run.

## Example Commands

```bash
python bmi_calculator.py    # run the application
python tests.py             # run the automated test suite
```

## Example Output

```
--- Calculate BMI ---
Enter your name: Alfred
  1. Metric (kilograms, centimeters)
  2. Imperial (pounds, inches)
  Select units [1-2]: 1
Enter weight (kg): 70
Enter height (cm): 175

========================================
BMI CALCULATION

Name: Alfred
Weight: 70.0 kg
Height: 175.0 cm
BMI: 22.86
Category: Normal weight
========================================
Would you like to set/compare a target BMI? [y/n]: n
```

## Data Storage

Every calculated record — name, weight, height, units, converted
metric values, BMI, category, date, and time — is appended to
`data/bmi_history.json` as a JSON list. The file is loaded
automatically when the program starts, so history persists between
sessions. If the file is missing, the app starts with an empty
history; if the file is corrupted or unreadable, the error is logged
and the app safely falls back to an empty history instead of crashing.

## CSV Export

Selecting **Export History** writes every stored record to
`exports/bmi_history.csv` with columns: name, weight, height, units,
weight_kg, height_cm, bmi, category, date, time. If there is no
history yet, the export is skipped and the user is informed.

## Logging

`logger.py` configures a file logger that writes timestamped
INFO/WARNING/ERROR events to `logs/bmi_calculator.log` — application
start/stop, records saved or cleared, exports, and any errors
encountered. Exact weight/height/BMI values are not written to the
log; only operational events and error messages are recorded.

## Error Handling

The application is designed to stay stable when:

- Required files (data or log files) are missing — they are created
  automatically, or the app falls back to sensible defaults.
- The JSON history file is corrupted — the error is logged and the
  app continues with an empty history instead of crashing.
- The user enters invalid input (empty, non-numeric, zero, negative)
  — the app re-prompts instead of raising an unhandled exception.
- CSV export fails (e.g. no records, or a file/permission error) —
  the failure is reported to the user and logged, without crashing.
- A calculation would be invalid (zero/negative weight or height) —
  a `ValueError` is raised internally and caught, with a clear message
  shown to the user.
- Any unexpected exception occurs at the top level — it is caught,
  logged with a full traceback, and reported to the user gracefully.

## Future Improvements

- Add a graphical (GUI) or web front end.
- Support additional unit systems (e.g. stones).
- Add BMI trend charts using a plotting library.
- Support multiple simultaneous user profiles with authentication.
- Add configurable BMI category thresholds (e.g. age/region-specific).

## Author

Developed as part of the Oasis Infobyte Python Programming Internship
(Level 3, Task 2).
