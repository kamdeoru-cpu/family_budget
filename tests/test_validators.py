import unittest
from datetime import date, timedelta

from app.services.errors import ValidationError
from app.services.validators import check_person_name, check_text, parse_amount, parse_date


class ParseAmountTest(unittest.TestCase):
    def test_integer_amount(self):
        self.assertEqual(parse_amount("1500"), 1500.0)

    def test_amount_with_comma_and_spaces(self):
        self.assertEqual(parse_amount(" 1 500,50 "), 1500.5)

    def test_empty_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("")

    def test_letters_are_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("сто")

    def test_zero_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("0")

    def test_negative_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("-100")

    def test_three_decimal_places_are_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("10,123")

    def test_too_big_amount_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_amount("10000001")


class ParseDateTest(unittest.TestCase):
    def test_correct_date(self):
        self.assertEqual(parse_date("05.10.2025"), date(2025, 10, 5))

    def test_wrong_format_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_date("2025-10-05")

    def test_impossible_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_date("31.02.2025")

    def test_future_date_is_rejected(self):
        tomorrow = (date.today() + timedelta(days=1)).strftime("%d.%m.%Y")
        with self.assertRaises(ValidationError):
            parse_date(tomorrow)

    def test_too_old_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            parse_date("31.12.1999")


class CheckTextTest(unittest.TestCase):
    def test_text_is_trimmed(self):
        self.assertEqual(check_text("  Продукты ", "Название", 2, 40), "Продукты")

    def test_too_short_text_is_rejected(self):
        with self.assertRaises(ValidationError):
            check_text("А", "Название", 2, 40)

    def test_name_with_digits_is_rejected(self):
        with self.assertRaises(ValidationError):
            check_person_name("Иван2", "ФИО")

    def test_double_name_with_hyphen_is_allowed(self):
        self.assertEqual(check_person_name("Анна-Мария", "ФИО"), "Анна-Мария")


if __name__ == "__main__":
    unittest.main()
