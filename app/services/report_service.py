"""Бизнес-логика итогов и отчётов."""
import csv
from pathlib import Path

from app.database.operation_repository import OperationRepository
from app.models.category import KIND_EXPENSE, KIND_INCOME
from app.models.report import BudgetSummary, CategoryReportRow
from app.services.errors import ValidationError
from app.services.validators import parse_date


class ReportService:
    def __init__(self, operation_repository: OperationRepository):
        self.operation_repository = operation_repository

    def get_summary(self) -> BudgetSummary:
        return self.operation_repository.get_summary()

    def build_category_report(self, date_from_text: str, date_to_text: str) -> list[CategoryReportRow]:
        date_from = parse_date(date_from_text, "Период с")
        date_to = parse_date(date_to_text, "Период по")
        if date_from > date_to:
            raise ValidationError(
                "Начало периода позже его окончания. Проверьте даты «с» и «по»."
            )
        return self.operation_repository.get_report_by_categories(date_from, date_to)

    @staticmethod
    def calculate_totals(rows: list[CategoryReportRow]) -> BudgetSummary:
        income = sum(row.total_amount for row in rows if row.category_kind == KIND_INCOME)
        expense = sum(row.total_amount for row in rows if row.category_kind == KIND_EXPENSE)
        return BudgetSummary(income, expense)

    @staticmethod
    def export_to_csv(rows: list[CategoryReportRow], file_path: str) -> None:
        # Кодировка utf-8-sig и разделитель «;» нужны, чтобы файл
        # правильно открывался в Microsoft Excel с русскими буквами
        with Path(file_path).open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["Категория", "Тип", "Количество операций", "Сумма, руб."])
            for row in rows:
                amount_text = f"{row.total_amount:.2f}".replace(".", ",")
                writer.writerow([row.category_name, row.category_kind, row.operations_count, amount_text])
