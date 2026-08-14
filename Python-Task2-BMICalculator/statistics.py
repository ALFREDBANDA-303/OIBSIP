"""
statistics.py

Computes summary statistics over a collection of BMI records:
count, average, lowest, highest, and latest BMI.

Named `statistics.py` per the project spec; imports the standard
library `statistics` module under a different name internally to
avoid a naming collision (this file shadows it for any code that
does `import statistics` at the project root, so we avoid relying
on the stdlib module here).
"""

from typing import List, Dict, Any, Optional


def calculate_statistics(records: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Calculate BMI statistics for a list of records.

    :param records: list of record dicts, each containing a "bmi" key
    :return: dict with count, average, lowest, highest, latest,
             or None if records is empty.
    """
    if not records:
        return None

    bmi_values = [record["bmi"] for record in records]

    count = len(bmi_values)
    average = sum(bmi_values) / count
    lowest = min(bmi_values)
    highest = max(bmi_values)
    latest = bmi_values[-1]

    return {
        "count": count,
        "average": round(average, 2),
        "lowest": round(lowest, 2),
        "highest": round(highest, 2),
        "latest": round(latest, 2),
    }


def compare_bmi(current_bmi: float, previous_bmi: float) -> str:
    """
    Compare two BMI values and describe the change.

    :return: "increased", "decreased", or "unchanged"
    """
    if current_bmi > previous_bmi:
        return "increased"
    elif current_bmi < previous_bmi:
        return "decreased"
    return "unchanged"


def target_difference(current_bmi: float, target_bmi: float) -> float:
    """
    Return the signed difference between the current BMI and a target
    BMI (positive means the user is above target, negative means below).
    """
    return round(current_bmi - target_bmi, 2)
