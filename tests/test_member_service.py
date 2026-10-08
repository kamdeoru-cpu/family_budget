import unittest

from app.services.errors import BusinessRuleError, ValidationError
from tests.helpers import TestContext


class MemberServiceTest(unittest.TestCase):
    def setUp(self):
        self.context = TestContext()
        self.service = self.context.member_service

    def tearDown(self):
        self.context.close()

    def test_add_member(self):
        member_id = self.service.add("Иванова Мария", "Мама")
        member = self.service.get_by_id(member_id)
        self.assertEqual(member.full_name, "Иванова Мария")
        self.assertEqual(member.role, "Мама")

    def test_add_member_with_empty_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.add("   ", "Мама")
        self.assertEqual(self.service.get_all(), [])

    def test_update_member(self):
        member_id = self.service.add("Иванов Пётр", "Сын")
        self.service.update(member_id, "Иванов Пётр Иванович", "Старший сын")
        self.assertEqual(self.service.get_by_id(member_id).role, "Старший сын")

    def test_delete_member_without_operations(self):
        member_id = self.service.add("Иванов Пётр", "Сын")
        self.service.delete(member_id)
        self.assertIsNone(self.service.get_by_id(member_id))

    def test_delete_member_with_operations_is_forbidden(self):
        member_id = self.service.add("Иванов Пётр", "Сын")
        category_id = self.context.category_id("Транспорт")
        self.context.operation_service.add("01.10.2025", "500", category_id, member_id, "")
        with self.assertRaises(BusinessRuleError):
            self.service.delete(member_id)


if __name__ == "__main__":
    unittest.main()
