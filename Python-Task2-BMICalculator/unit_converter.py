"""
unit_converter.py

Handles conversion between imperial and metric measurement units.
All BMI calculations elsewhere in the application work in metric
(kilograms and centimeters); this module is the single place that
knows the conversion formulas.
"""

# Standard, widely accepted conversion factors
KG_PER_POUND = 0.45359237
CM_PER_INCH = 2.54


def pounds_to_kg(pounds: float) -> float:
    """Convert a weight in pounds to kilograms."""
    if pounds < 0:
        raise ValueError("Weight in pounds cannot be negative.")
    return pounds * KG_PER_POUND


def inches_to_cm(inches: float) -> float:
    """Convert a height in inches to centimeters."""
    if inches < 0:
        raise ValueError("Height in inches cannot be negative.")
    return inches * CM_PER_INCH


def kg_to_pounds(kg: float) -> float:
    """Convert a weight in kilograms to pounds."""
    if kg < 0:
        raise ValueError("Weight in kilograms cannot be negative.")
    return kg / KG_PER_POUND


def cm_to_inches(cm: float) -> float:
    """Convert a height in centimeters to inches."""
    if cm < 0:
        raise ValueError("Height in centimeters cannot be negative.")
    return cm / CM_PER_INCH


def to_metric(weight: float, height: float, units: str) -> tuple:
    """
    Convert a (weight, height) pair to metric (kg, cm) based on the
    given unit system.

    :param weight: weight value as entered by the user
    :param height: height value as entered by the user
    :param units: "metric" (kg/cm) or "imperial" (lb/in)
    :return: (weight_kg, height_cm) tuple
    :raises ValueError: if units is not a recognized unit system
    """
    if units == "metric":
        return weight, height
    elif units == "imperial":
        return pounds_to_kg(weight), inches_to_cm(height)
    else:
        raise ValueError(f"Unsupported unit system: {units}")
