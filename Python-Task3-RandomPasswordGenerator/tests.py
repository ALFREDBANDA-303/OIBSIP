"""
tests.py
--------
Automated test suite for the Random Password Generator project.

Run with:
    python tests.py

Uses Python's built-in `unittest` framework. Covers:
    - Password length correctness
    - Character-set requirements
    - Password uniqueness
    - Strength calculation
    - Invalid length handling
    - Invalid character-set selection handling
    - History saving / loading / clearing
    - Corrupted history file handling
    - Clipboard handling (success and failure paths, mocked)
    - Configuration constants
    - General error handling
"""

import os
import shutil
import string
import tempfile
import unittest
from unittest.mock import patch

import config
from password_generator import PasswordGenerator, PasswordGenerationError
from password_strength import PasswordStrengthAnalyzer
from password_history import PasswordHistoryManager
import clipboard_manager


class TestConfig(unittest.TestCase):
    """Tests for config.py constants and helper functions."""

    def test_length_bounds_are_sane(self):
        self.assertLess(config.MIN_PASSWORD_LENGTH, config.MAX_PASSWORD_LENGTH)
        self.assertGreaterEqual(
            config.DEFAULT_PASSWORD_LENGTH, config.MIN_PASSWORD_LENGTH
        )
        self.assertLessEqual(config.DEFAULT_PASSWORD_LENGTH, config.MAX_PASSWORD_LENGTH)

    def test_character_sets_defined(self):
        self.assertTrue(config.LOWERCASE_CHARS)
        self.assertTrue(config.UPPERCASE_CHARS)
        self.assertTrue(config.NUMBER_CHARS)
        self.assertTrue(config.SPECIAL_CHARS)

    def test_ensure_directories_creates_paths(self):
        config.ensure_directories()
        self.assertTrue(os.path.isdir(config.DATA_DIR))
        self.assertTrue(os.path.isdir(config.LOGS_DIR))


class TestPasswordGenerator(unittest.TestCase):
    """Tests for password_generator.py."""

    def test_default_generation_length(self):
        gen = PasswordGenerator(length=12)
        pw = gen.generate()
        self.assertEqual(len(pw), 12)

    def test_custom_length(self):
        for length in (4, 8, 16, 32, 64):
            gen = PasswordGenerator(length=length)
            pw = gen.generate()
            self.assertEqual(len(pw), length)

    def test_character_requirements_all_sets(self):
        gen = PasswordGenerator(
            length=32,
            use_uppercase=True,
            use_lowercase=True,
            use_numbers=True,
            use_special=True,
        )
        pw = gen.generate()
        self.assertTrue(any(c in string.ascii_uppercase for c in pw))
        self.assertTrue(any(c in string.ascii_lowercase for c in pw))
        self.assertTrue(any(c in string.digits for c in pw))
        self.assertTrue(any(c in config.SPECIAL_CHARS for c in pw))

    def test_character_requirements_single_set(self):
        gen = PasswordGenerator(
            length=20,
            use_uppercase=False,
            use_lowercase=True,
            use_numbers=False,
            use_special=False,
        )
        pw = gen.generate()
        self.assertTrue(all(c in string.ascii_lowercase for c in pw))

    def test_password_uniqueness(self):
        gen = PasswordGenerator(length=16)
        passwords = gen.generate_multiple(20)
        self.assertEqual(len(passwords), len(set(passwords)))

    def test_invalid_length_too_short(self):
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(length=config.MIN_PASSWORD_LENGTH - 1)

    def test_invalid_length_too_long(self):
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(length=config.MAX_PASSWORD_LENGTH + 1)

    def test_invalid_length_non_integer(self):
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(length="16")

    def test_invalid_no_charset_selected(self):
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(
                length=10,
                use_uppercase=False,
                use_lowercase=False,
                use_numbers=False,
                use_special=False,
            )

    def test_invalid_length_shorter_than_required_sets(self):
        # 4 character sets selected but length of 2 cannot satisfy all of them.
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(
                length=2,
                use_uppercase=True,
                use_lowercase=True,
                use_numbers=True,
                use_special=True,
            )

    def test_generate_multiple_invalid_count(self):
        gen = PasswordGenerator(length=10)
        with self.assertRaises(PasswordGenerationError):
            gen.generate_multiple(0)
        with self.assertRaises(PasswordGenerationError):
            gen.generate_multiple(-5)
        with self.assertRaises(PasswordGenerationError):
            gen.generate_multiple(config.MAX_COUNT + 1)


class TestPasswordStrength(unittest.TestCase):
    """Tests for password_strength.py."""

    def test_weak_password(self):
        result = PasswordStrengthAnalyzer.analyze("abc")
        self.assertEqual(result.rating, "Weak")
        self.assertTrue(len(result.feedback) > 0)

    def test_moderate_password(self):
        result = PasswordStrengthAnalyzer.analyze("abcdefgh1")
        self.assertIn(result.rating, ("Weak", "Moderate"))

    def test_strong_password(self):
        result = PasswordStrengthAnalyzer.analyze("Abcdefgh123!")
        self.assertIn(result.rating, ("Strong", "Very Strong"))

    def test_very_strong_password(self):
        result = PasswordStrengthAnalyzer.analyze("Abcdefghijklmno123!@#")
        self.assertEqual(result.rating, "Very Strong")

    def test_empty_password_raises(self):
        with self.assertRaises(ValueError):
            PasswordStrengthAnalyzer.analyze("")

    def test_non_string_password_raises(self):
        with self.assertRaises(ValueError):
            PasswordStrengthAnalyzer.analyze(12345)

    def test_feedback_present_for_weak_password(self):
        result = PasswordStrengthAnalyzer.analyze("aaaa")
        self.assertTrue(any("Add" in tip or "length" in tip.lower() for tip in result.feedback))

    def test_details_dict_contains_expected_keys(self):
        result = PasswordStrengthAnalyzer.analyze("Password123!")
        expected_keys = {
            "length",
            "has_lowercase",
            "has_uppercase",
            "has_numbers",
            "has_special_characters",
            "meets_minimum_length",
        }
        self.assertTrue(expected_keys.issubset(result.details.keys()))


class TestPasswordHistory(unittest.TestCase):
    """Tests for password_history.py."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.tmp_dir, "test_history.json")
        self.manager = PasswordHistoryManager(history_file=self.history_file)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_add_and_get_entry(self):
        self.manager.add_entry(length=16, strength="Strong")
        history = self.manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["length"], 16)
        self.assertEqual(history[0]["strength"], "Strong")

    def test_password_not_stored_by_default(self):
        self.manager.add_entry(length=12, strength="Moderate", password="secret123")
        history = self.manager.get_history()
        self.assertNotIn("password", history[0])

    def test_password_stored_when_opted_in(self):
        self.manager.add_entry(
            length=12, strength="Moderate", password="secret123", store_password=True
        )
        history = self.manager.get_history()
        self.assertIn("password", history[0])

    def test_clear_history(self):
        self.manager.add_entry(length=10, strength="Weak")
        self.manager.add_entry(length=12, strength="Strong")
        self.manager.clear_history()
        self.assertEqual(self.manager.count(), 0)

    def test_missing_history_file_returns_empty(self):
        # File does not exist yet at this point.
        history = self.manager.get_history()
        self.assertEqual(history, [])

    def test_corrupted_history_file_handled_gracefully(self):
        with open(self.history_file, "w", encoding="utf-8") as f:
            f.write("{ this is not valid json ]")
        history = self.manager.get_history()
        self.assertEqual(history, [])

    def test_history_trimmed_to_max_entries(self):
        original_max = config.MAX_HISTORY_ENTRIES
        try:
            config.MAX_HISTORY_ENTRIES = 3
            for i in range(5):
                self.manager.add_entry(length=8 + i, strength="Weak")
            history = self.manager.get_history()
            self.assertEqual(len(history), 3)
        finally:
            config.MAX_HISTORY_ENTRIES = original_max

    def test_history_entry_has_timestamp(self):
        self.manager.add_entry(length=10, strength="Weak")
        history = self.manager.get_history()
        self.assertIn("timestamp", history[0])
        self.assertTrue(len(history[0]["timestamp"]) > 0)


class TestClipboardManager(unittest.TestCase):
    """Tests for clipboard_manager.py, using mocks to avoid depending on a
    real system clipboard backend being present in the test environment."""

    def test_copy_success(self):
        with patch.object(clipboard_manager, "_PYPERCLIP_AVAILABLE", True), patch.object(
            clipboard_manager, "pyperclip"
        ) as mock_pyperclip:
            mock_pyperclip.copy.return_value = None
            result = clipboard_manager.copy_to_clipboard("MyP@ssw0rd")
            self.assertTrue(result)
            mock_pyperclip.copy.assert_called_once_with("MyP@ssw0rd")

    def test_copy_failure_handled_gracefully(self):
        with patch.object(clipboard_manager, "_PYPERCLIP_AVAILABLE", True), patch.object(
            clipboard_manager, "pyperclip"
        ) as mock_pyperclip:
            mock_pyperclip.copy.side_effect = Exception("No clipboard backend")
            result = clipboard_manager.copy_to_clipboard("MyP@ssw0rd")
            self.assertFalse(result)

    def test_copy_empty_string_rejected(self):
        result = clipboard_manager.copy_to_clipboard("")
        self.assertFalse(result)

    def test_copy_when_pyperclip_unavailable(self):
        with patch.object(clipboard_manager, "_PYPERCLIP_AVAILABLE", False):
            result = clipboard_manager.copy_to_clipboard("password")
            self.assertFalse(result)

    def test_is_clipboard_available_false_when_no_backend(self):
        with patch.object(clipboard_manager, "_PYPERCLIP_AVAILABLE", True), patch.object(
            clipboard_manager, "pyperclip"
        ) as mock_pyperclip:
            mock_pyperclip.paste.side_effect = Exception("No backend")
            self.assertFalse(clipboard_manager.is_clipboard_available())

    def test_is_clipboard_available_true_when_backend_present(self):
        with patch.object(clipboard_manager, "_PYPERCLIP_AVAILABLE", True), patch.object(
            clipboard_manager, "pyperclip"
        ) as mock_pyperclip:
            mock_pyperclip.paste.return_value = ""
            self.assertTrue(clipboard_manager.is_clipboard_available())


class TestErrorHandling(unittest.TestCase):
    """General cross-module error handling tests."""

    def test_generator_raises_specific_exception_type(self):
        with self.assertRaises(PasswordGenerationError):
            PasswordGenerator(length=0)

    def test_strength_analyzer_raises_value_error(self):
        with self.assertRaises(ValueError):
            PasswordStrengthAnalyzer.analyze(None)

    def test_history_manager_survives_bad_file_permissions_simulation(self):
        # Simulate a read failure by pointing at a directory instead of a file.
        tmp_dir = tempfile.mkdtemp()
        try:
            bad_path = os.path.join(tmp_dir, "as_a_dir.json")
            os.makedirs(bad_path)
            manager = PasswordHistoryManager(history_file=bad_path)
            # Reading should not raise; it should safely return an empty list.
            history = manager.get_history()
            self.assertEqual(history, [])
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)


def run_tests() -> int:
    """
    Run the full test suite and print a clear summary.

    Returns:
        0 if all tests passed, 1 otherwise (suitable as a process exit code).
    """
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__("__main__"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed
    print(f"Total tests run : {total}")
    print(f"Passed          : {passed}")
    print(f"Failed          : {failed}")
    if result.failures:
        print("\nFailures:")
        for test, _ in result.failures:
            print(f"  - {test}")
    if result.errors:
        print("\nErrors:")
        for test, _ in result.errors:
            print(f"  - {test}")
    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import sys

    sys.exit(run_tests())
