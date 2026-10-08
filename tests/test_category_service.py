import unittest

from app.services.errors import BusinessRuleError, ValidationError
from tests.helpers import TestContext


class CategoryServiceTest(unittest.TestCase):
    def setUp(self):
        self.context = TestContext()
        self.service = self.context.category_service

    def tearDown(self):
        self.context.close()

    def test_default_categories_are_created(self):
        names = [category.name for category in self.service.get_all()]
        self.assertIn("Зарплата", names)
        self.assertIn("Продукты", names)

    def test_add_category(self):
        category_id = self.service.add("Здоровье", "Расход")
        self.assertEqual(self.service.get_by_id(category_id).kind, "Расход")

    def test_duplicate_name_is_rejected_ignoring_case(self):
        with self.assertRaises(BusinessRuleError):
            self.service.add("продукты", "Расход")

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add("Подарки", "Кредит")

    def test_rename_category_to_same_name(self):
        category_id = self.context.category_id("Транспорт")
        self.service.update(category_id, "Транспорт", "Расход")
        self.assertEqual(self.service.get_by_id(category_id).name, "Транспорт")

    def test_delete_unused_category(self):
        category_id = self.service.add("Здоровье", "Расход")
        self.service.delete(category_id)
        self.assertIsNone(self.service.get_by_id(category_id))

    def test_delete_used_category_is_forbidden(self):
        member_id = self.context.member_service.add("Иванов Пётр", "Сын")
        category_id = self.context.category_id("Транспорт")
        self.context.operation_service.add("01.10.2025", "500", category_id, member_id, "")
        with self.assertRaises(BusinessRuleError):
            self.service.delete(category_id)

    def test_change_kind_of_used_category_is_forbidden(self):
        member_id = self.context.member_service.add("Иванов Пётр", "Сын")
        category_id = self.context.category_id("Транспорт")
        self.context.operation_service.add("01.10.2025", "500", category_id, member_id, "")
        with self.assertRaises(BusinessRuleError):
            self.service.update(category_id, "Транспорт", "Доход")


if __name__ == "__main__":
    unittest.main()
