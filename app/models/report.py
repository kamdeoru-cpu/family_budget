"""Структуры данных для итогов и отчётов."""
from dataclasses import dataclass


@dataclass
class BudgetSummary:
    total_income: float
    total_expense: float

    @property
    def balance(self) -> float:
        return self.total_income - self.total_expense


@dataclass
class CategoryReportRow:
    category_name: str
    category_kind: str
    operations_count: int
    total_amount: float
