"""Сущность «Операция» — одно поступление или трата денег."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Operation:
    operation_id: Optional[int]
    operation_date: date
    amount: float
    category_id: int
    member_id: int
    comment: str = ""
    # Поля ниже заполняются только при чтении из базы (для показа в таблице)
    category_name: str = ""
    category_kind: str = ""
    member_name: str = ""
