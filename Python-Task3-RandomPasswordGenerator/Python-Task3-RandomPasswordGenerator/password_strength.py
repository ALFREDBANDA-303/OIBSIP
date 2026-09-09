"""
password_strength.py
---------------------
Password strength analysis module.

Evaluates a password's length and character diversity to produce a
strength rating (Weak, Moderate, Strong, Very Strong) along with actionable
feedback for improving weak passwords. This module performs analysis only
and never persists or logs the password it evaluates.
"""

import re
from dataclasses import dataclass, field

import config


@dataclass
class StrengthResult:
    """
    Represents the result of a password strength analysis.

    Attributes:
        score: Numeric score from 0-6 representing the criteria met.
        rating: One of "Weak", "Moderate", "Strong", "Very Strong".
        feedback: A list of human-readable suggestions for improvement.
        details: A dictionary of individual criteria checks (booleans).
    """

    score: int
    rating: str
    feedback: list = field(default_factory=list)
    details: dict = field(default_factory=dict)


class PasswordStrengthAnalyzer:
    """Analyzes password strength based on length and character diversity."""

    @staticmethod
    def analyze(password: str) -> StrengthResult:
        """
        Analyze the given password and return a StrengthResult.

        Args:
            password: The password string to evaluate.

        Returns:
            A StrengthResult describing the password's strength.

        Raises:
            ValueError: If the password is empty or not a string.
        """
        if not isinstance(password, str) or len(password) == 0:
            raise ValueError("Password must be a non-empty string.")

        length = len(password)
        has_lower = bool(re.search(r"[a-z]", password))
        has_upper = bool(re.search(r"[A-Z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[^A-Za-z0-9]", password))

        details = {
            "length": length,
            "has_lowercase": has_lower,
            "has_uppercase": has_upper,
            "has_numbers": has_digit,
            "has_special_characters": has_special,
            "meets_minimum_length": length >= config.MIN_PASSWORD_LENGTH,
        }

        # Base score: one point per character-type criterion satisfied.
        diversity_score = sum([has_lower, has_upper, has_digit, has_special])

        # Length bonus points.
        length_score = 0
        if length >= config.MIN_PASSWORD_LENGTH:
            length_score += 1
        if length >= config.STRONG_LENGTH_THRESHOLD:
            length_score += 1
        if length >= config.VERY_STRONG_LENGTH_THRESHOLD:
            length_score += 1

        total_score = diversity_score + length_score  # max 4 + 3 = 7

        rating = PasswordStrengthAnalyzer._score_to_rating(total_score, length, diversity_score)
        feedback = PasswordStrengthAnalyzer._build_feedback(details)

        return StrengthResult(
            score=total_score, rating=rating, feedback=feedback, details=details
        )

    @staticmethod
    def _score_to_rating(total_score: int, length: int, diversity_score: int) -> str:
        """
        Map a numeric score to a strength rating category.

        Very short passwords or those using only a single character type are
        always capped at "Weak" regardless of score, to avoid misleadingly
        rating short/simple passwords as stronger than they are.
        """
        if length < config.MIN_PASSWORD_LENGTH or diversity_score <= 1:
            return "Weak"

        if total_score <= 3:
            return "Weak"
        elif total_score <= 5:
            return "Moderate"
        elif total_score == 6:
            return "Strong"
        else:
            return "Very Strong"

    @staticmethod
    def _build_feedback(details: dict) -> list:
        """
        Build a list of human-readable suggestions based on missing
        criteria.

        Args:
            details: The details dictionary produced by analyze().

        Returns:
            A list of suggestion strings. Empty if no improvements needed.
        """
        feedback = []

        if not details["meets_minimum_length"]:
            feedback.append(
                f"Increase length to at least {config.MIN_PASSWORD_LENGTH} characters."
            )
        elif details["length"] < config.STRONG_LENGTH_THRESHOLD:
            feedback.append(
                f"Consider using at least {config.STRONG_LENGTH_THRESHOLD} characters "
                "for stronger security."
            )

        if not details["has_lowercase"]:
            feedback.append("Add lowercase letters.")
        if not details["has_uppercase"]:
            feedback.append("Add uppercase letters.")
        if not details["has_numbers"]:
            feedback.append("Add numbers.")
        if not details["has_special_characters"]:
            feedback.append("Add special characters (e.g. !@#$%).")

        if not feedback:
            feedback.append("Great password! No improvements needed.")

        return feedback
