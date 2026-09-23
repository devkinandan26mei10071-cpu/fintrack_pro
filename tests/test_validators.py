"""
Unit tests for input validation, regex parsing, and bounds checking.
"""

import unittest
from fintrack.utils.validators import (
    validate_amount,
    validate_date,
    validate_category_name,
    validate_description,
    validate_month_year,
    ValidationError,
)


class TestValidators(unittest.TestCase):

    def test_validate_amount_valid(self):
        self.assertEqual(validate_amount(100), 100.0)
        self.assertEqual(validate_amount("250.75"), 250.75)
        self.assertEqual(validate_amount(15.999), 16.0)

    def test_validate_amount_invalid(self):
        with self.assertRaises(ValidationError):
            validate_amount(-10.0)
        with self.assertRaises(ValidationError):
            validate_amount("abc")
        with self.assertRaises(ValidationError):
            validate_amount(0.0)
        with self.assertRaises(ValidationError):
            validate_amount(999_999_999.0)

    def test_validate_date_valid(self):
        self.assertEqual(validate_date("2026-09-23"), "2026-09-23")
        self.assertEqual(validate_date("2024-02-29"), "2024-02-29")  # Leap year check

    def test_validate_date_invalid(self):
        with self.assertRaises(ValidationError):
            validate_date("23-09-2026")
        with self.assertRaises(ValidationError):
            validate_date("2023-02-29")  # Not a leap year
        with self.assertRaises(ValidationError):
            validate_date("2026/09/23")
        with self.assertRaises(ValidationError):
            validate_date("not-a-date")

    def test_validate_category_name(self):
        self.assertEqual(validate_category_name("Groceries & Food"), "Groceries & Food")
        with self.assertRaises(ValidationError):
            validate_category_name("A")  # Too short
        with self.assertRaises(ValidationError):
            validate_category_name("Invalid<Script>")

    def test_validate_month_year(self):
        self.assertEqual(validate_month_year("2026-09"), "2026-09")
        with self.assertRaises(ValidationError):
            validate_month_year("2026-13")
        with self.assertRaises(ValidationError):
            validate_month_year("2026/09")


if __name__ == "__main__":
    unittest.main()
