"""
tests.py

Automated tests for the BMI Calculator application. Runs without any
manual user interaction.

Covers:
    - BMI calculation
    - BMI classification
    - Zero / negative / invalid input handling
    - Unit conversion
    - History storage and retrieval
    - Statistics
    - CSV export

Run with:
    python tests.py
or:
    python -m unittest tests.py
"""

import csv
import json
import os
import shutil
import tempfile
import unittest

import unit_converter
import statistics as bmi_statistics
from bmi_calculator import BMICalculator
from bmi_history import BMIHistory


class TestBMICalculation(unittest.TestCase):
    """Tests for BMI calculation."""

    def test_calculate_bmi_normal_case(self):
        # 70 kg, 175 cm -> BMI ~22.86
        bmi = BMICalculator.calculate_bmi(70, 175)
        self.assertAlmostEqual(bmi, 22.86, places=2)

    def test_calculate_bmi_rounding(self):
        bmi = BMICalculator.calculate_bmi(60, 160)
        self.assertEqual(bmi, round(60 / (1.6 ** 2), 2))

    def test_calculate_bmi_zero_weight_raises(self):
        with self.assertRaises(ValueError):
            BMICalculator.calculate_bmi(0, 175)

    def test_calculate_bmi_zero_height_raises(self):
        with self.assertRaises(ValueError):
            BMICalculator.calculate_bmi(70, 0)

    def test_calculate_bmi_negative_weight_raises(self):
        with self.assertRaises(ValueError):
            BMICalculator.calculate_bmi(-70, 175)

    def test_calculate_bmi_negative_height_raises(self):
        with self.assertRaises(ValueError):
            BMICalculator.calculate_bmi(70, -175)


class TestBMIClassification(unittest.TestCase):
    """Tests for BMI category classification."""

    def test_underweight(self):
        self.assertEqual(BMICalculator.classify_bmi(17.0), "Underweight")

    def test_normal_weight_lower_bound(self):
        self.assertEqual(BMICalculator.classify_bmi(18.5), "Normal weight")

    def test_normal_weight(self):
        self.assertEqual(BMICalculator.classify_bmi(22.0), "Normal weight")

    def test_overweight_lower_bound(self):
        self.assertEqual(BMICalculator.classify_bmi(25.0), "Overweight")

    def test_overweight(self):
        self.assertEqual(BMICalculator.classify_bmi(27.5), "Overweight")

    def test_obesity_lower_bound(self):
        self.assertEqual(BMICalculator.classify_bmi(30.0), "Obesity")

    def test_obesity(self):
        self.assertEqual(BMICalculator.classify_bmi(40.0), "Obesity")


class TestUnitConversion(unittest.TestCase):
    """Tests for unit_converter.py."""

    def test_pounds_to_kg(self):
        self.assertAlmostEqual(unit_converter.pounds_to_kg(154.324), 70.0, places=1)

    def test_inches_to_cm(self):
        self.assertAlmostEqual(unit_converter.inches_to_cm(68.9), 175.0, places=0)

    def test_kg_to_pounds_round_trip(self):
        kg = 70.0
        pounds = unit_converter.kg_to_pounds(kg)
        back_to_kg = unit_converter.pounds_to_kg(pounds)
        self.assertAlmostEqual(kg, back_to_kg, places=6)

    def test_cm_to_inches_round_trip(self):
        cm = 175.0
        inches = unit_converter.cm_to_inches(cm)
        back_to_cm = unit_converter.inches_to_cm(inches)
        self.assertAlmostEqual(cm, back_to_cm, places=6)

    def test_to_metric_metric_units_unchanged(self):
        weight_kg, height_cm = unit_converter.to_metric(70, 175, "metric")
        self.assertEqual((weight_kg, height_cm), (70, 175))

    def test_to_metric_imperial_units_converted(self):
        weight_kg, height_cm = unit_converter.to_metric(154.324, 68.9, "imperial")
        self.assertAlmostEqual(weight_kg, 70.0, places=1)
        self.assertAlmostEqual(height_cm, 175.0, places=0)

    def test_to_metric_invalid_units_raises(self):
        with self.assertRaises(ValueError):
            unit_converter.to_metric(70, 175, "stones")

    def test_negative_pounds_raises(self):
        with self.assertRaises(ValueError):
            unit_converter.pounds_to_kg(-10)

    def test_negative_inches_raises(self):
        with self.assertRaises(ValueError):
            unit_converter.inches_to_cm(-10)


class TestBMIHistory(unittest.TestCase):
    """Tests for bmi_history.py: storage, retrieval, corrupted files."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "bmi_history.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _sample_record(self, name="Alfred", bmi=22.86):
        return {
            "name": name,
            "weight": 70,
            "height": 175,
            "units": "metric",
            "weight_kg": 70,
            "height_cm": 175,
            "bmi": bmi,
            "category": "Normal weight",
            "date": "2024-01-01",
            "time": "12:00:00",
        }

    def test_load_missing_file_starts_empty(self):
        history = BMIHistory(self.data_file)
        self.assertEqual(history.get_all(), [])

    def test_add_and_retrieve_record(self):
        history = BMIHistory(self.data_file)
        history.add_record(self._sample_record())
        self.assertEqual(len(history.get_all()), 1)
        self.assertEqual(history.get_all()[0]["name"], "Alfred")

    def test_records_persist_across_instances(self):
        history = BMIHistory(self.data_file)
        history.add_record(self._sample_record())

        reloaded = BMIHistory(self.data_file)
        self.assertEqual(len(reloaded.get_all()), 1)

    def test_get_last_by_name(self):
        history = BMIHistory(self.data_file)
        history.add_record(self._sample_record(name="Alfred", bmi=20.0))
        history.add_record(self._sample_record(name="Alfred", bmi=21.0))
        history.add_record(self._sample_record(name="Bruce", bmi=25.0))

        last_alfred = history.get_last("Alfred")
        self.assertEqual(last_alfred["bmi"], 21.0)

    def test_get_by_name_filters_correctly(self):
        history = BMIHistory(self.data_file)
        history.add_record(self._sample_record(name="Alfred"))
        history.add_record(self._sample_record(name="Bruce"))

        alfred_records = history.get_by_name("Alfred")
        self.assertEqual(len(alfred_records), 1)
        self.assertEqual(alfred_records[0]["name"], "Alfred")

    def test_clear_history(self):
        history = BMIHistory(self.data_file)
        history.add_record(self._sample_record())
        self.assertEqual(len(history.get_all()), 1)

        history.clear()
        self.assertEqual(history.get_all(), [])

    def test_corrupted_json_file_does_not_crash(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            f.write("{ this is not valid json ]")

        history = BMIHistory(self.data_file)  # should not raise
        self.assertEqual(history.get_all(), [])

    def test_empty_file_treated_as_empty_history(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            f.write("")

        history = BMIHistory(self.data_file)
        self.assertEqual(history.get_all(), [])


class TestStatistics(unittest.TestCase):
    """Tests for statistics.py."""

    def test_calculate_statistics_empty_returns_none(self):
        self.assertIsNone(bmi_statistics.calculate_statistics([]))

    def test_calculate_statistics_values(self):
        records = [
            {"bmi": 20.0},
            {"bmi": 22.0},
            {"bmi": 24.0},
        ]
        stats = bmi_statistics.calculate_statistics(records)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["average"], 22.0)
        self.assertEqual(stats["lowest"], 20.0)
        self.assertEqual(stats["highest"], 24.0)
        self.assertEqual(stats["latest"], 24.0)

    def test_compare_bmi_increased(self):
        self.assertEqual(bmi_statistics.compare_bmi(25.0, 22.0), "increased")

    def test_compare_bmi_decreased(self):
        self.assertEqual(bmi_statistics.compare_bmi(20.0, 22.0), "decreased")

    def test_compare_bmi_unchanged(self):
        self.assertEqual(bmi_statistics.compare_bmi(22.0, 22.0), "unchanged")

    def test_target_difference_above(self):
        self.assertEqual(bmi_statistics.target_difference(25.0, 22.0), 3.0)

    def test_target_difference_below(self):
        self.assertEqual(bmi_statistics.target_difference(20.0, 22.0), -2.0)


class TestCSVExport(unittest.TestCase):
    """Tests for CSV export functionality."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "bmi_history.json")
        self.export_file = os.path.join(self.temp_dir, "exports", "bmi_history.csv")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_with_no_records_returns_false(self):
        history = BMIHistory(self.data_file)
        result = history.export_to_csv(self.export_file)
        self.assertFalse(result)
        self.assertFalse(os.path.exists(self.export_file))

    def test_export_creates_csv_with_correct_rows(self):
        history = BMIHistory(self.data_file)
        history.add_record({
            "name": "Alfred", "weight": 70, "height": 175, "units": "metric",
            "weight_kg": 70, "height_cm": 175, "bmi": 22.86,
            "category": "Normal weight", "date": "2024-01-01", "time": "12:00:00",
        })

        result = history.export_to_csv(self.export_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.export_file))

        with open(self.export_file, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Alfred")
        self.assertEqual(rows[0]["bmi"], "22.86")


class TestJSONDataIntegrity(unittest.TestCase):
    """Extra check that saved JSON is valid and round-trips correctly."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "bmi_history.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_saved_file_is_valid_json(self):
        history = BMIHistory(self.data_file)
        history.add_record({
            "name": "Alfred", "weight": 70, "height": 175, "units": "metric",
            "weight_kg": 70, "height_cm": 175, "bmi": 22.86,
            "category": "Normal weight", "date": "2024-01-01", "time": "12:00:00",
        })

        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # should not raise

        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
