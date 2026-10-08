import unittest

from app.services.errors import ValidationError
from tests.helpers import TestContext


class OperationServiceTest(unittest.TestCase):
    def setUp(self):
        self.context = TestContext()
        self.service = self.context.operation_service
        self.member_id = self.context.member_service.add("Иванов Пётр", "Папа")
        self.salary_id = self.context.category_id("Зарплата")
        self.food_id = self.context.category_id("Продукты")

    def tearDown(self):
        self.context.close()

    def test_add_operation(self):
        operation_id = self.service.add("01.10.2025", "1500,50", self.food_id, self.member_id, " Хлеб ")
        operation = self.service.get_by_id(operation_id)
        self.assertEqual(operation.amount, 1500.5)
        self.assertEqual(operation.comment, "Хлеб")
        self.assertEqual(operation.category_kind, "Расход")

    def test_operation_without_category_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add("01.10.2025", "100", None, self.member_id, "")

    def test_operation_without_member_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add("01.10.2025", "100", self.food_id, None, "")

    def test_too_long_comment_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add("01.10.2025", "100", self.food_id, self.member_id, "а" * 201)

    def test_filter_by_kind(self):
        self.service.add("01.10.2025", "50000", self.salary_id, self.member_id, "")
        self.service.add("02.10.2025", "700", self.food_id, self.member_id, "")
        expenses = self.service.find("Расход")
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category_name, "Продукты")

    def test_search_ignores_letter_case(self):
        self.service.add("02.10.2025", "700", self.food_id, self.member_id, "Молоко и хлеб")
        self.assertEqual(len(self.service.find(None, "МОЛОКО")), 1)
        self.assertEqual(len(self.service.find(None, "сыр")), 0)

    def test_update_operation(self):
        operation_id = self.service.add("01.10.2025", "100", self.food_id, self.member_id, "")
        self.service.update(operation_id, "03.10.2025", "250", self.food_id, self.member_id, "Фрукты")
        operation = self.service.get_by_id(operation_id)
        self.assertEqual(operation.amount, 250)
        self.assertEqual(operation.comment, "Фрукты")

    def test_delete_operation(self):
        operation_id = self.service.add("01.10.2025", "100", self.food_id, self.member_id, "")
        self.service.delete(operation_id)
        self.assertIsNone(self.service.get_by_id(operation_id))

    def test_expense_above_balance_is_detected(self):
        self.service.add("01.10.2025", "1000", self.salary_id, self.member_id, "")
        self.assertTrue(self.service.is_expense_above_balance("1500", self.food_id))
        self.assertFalse(self.service.is_expense_above_balance("500", self.food_id))
        self.assertFalse(self.service.is_expense_above_balance("5000", self.salary_id))


if __name__ == "__main__":
    unittest.main()
