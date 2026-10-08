"""Сущность «Категория» (статья дохода или расхода)."""
from dataclasses import dataclass
from typing import Optional

KIND_INCOME = "Доход"
KIND_EXPENSE = "Расход"
CATEGORY_KINDS = (KIND_INCOME, KIND_EXPENSE)


@dataclass
class Category:
    category_id: Optional[int]
    name: str
    kind: str

    @property
    def display_name(self) -> str:
        return f"{self.name} ({self.kind.lower()})"

    @property
    def is_expense(self) -> bool:
        return self.kind == KIND_EXPENSE
