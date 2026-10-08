import csv
import tempfile
import unittest
from pathlib import Path

from app.services.errors import ValidationError
from tests.helpers import TestContext


class ReportServiceTest(unittest.TestCase):
    def setUp(self):
        self.context = TestContext()
        self.service = self.context.report_service
        operation_service = self.context.operation_service
        member_id = self.context.member_service.add("Иванов Пётр", "Папа")
        salary_id = self.context.category_id("Зарплата")
        food_id = self.context.category_id("Продукты")
        operation_service.add("01.09.2025", "50000", salary_id, member_id, "")
        operation_service.add("05.09.2025", "1200", food_id, member_id, "")
        operation_service.add("10.09.2025", "800", food_id, member_id, "")
        operation_service.add("01.10.2025", "3000", food_id, member_id, "")

    def tearDown(self):
        self.context.close()

    def test_summary_for_all_time(self):
        summary = self.service.get_summary()
        self.assertEqual(summary.total_income, 50000)
        self.assertEqual(summary.total_expense, 5000)
        self.assertEqual(summary.balance, 45000)

    def test_report_groups_by_category_within_period(self):
        rows = self.service.build_category_report("01.09.2025", "30.09.2025")
        food_row = next(row for row in rows if row.category_name == "Продукты")
        self.assertEqual(food_row.operations_count, 2)
        self.assertEqual(food_row.total_amount, 2000)

    def test_report_totals(self):
        rows = self.service.build_category_report("01.09.2025", "30.09.2025")
        totals = self.service.calculate_totals(rows)
        self.assertEqual(totals.balance, 48000)

    def test_empty_period(self):
        self.assertEqual(self.service.build_category_report("01.01.2024", "31.01.2024"), [])

    def test_wrong_period_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.service.build_category_report("30.09.2025", "01.09.2025")

    def test_export_to_csv(self):
        rows = self.service.build_category_report("01.09.2025", "30.09.2025")
        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / "report.csv"
            self.service.export_to_csv(rows, str(file_path))
            with file_path.open(encoding="utf-8-sig") as file:
                lines = list(csv.reader(file, delimiter=";"))
        self.assertEqual(lines[0][0], "Категория")
        self.assertEqual(len(lines), len(rows) + 1)


if __name__ == "__main__":
    unittest.main()
