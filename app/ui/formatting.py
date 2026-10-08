"""Форматирование чисел и дат для показа пользователю."""
from datetime import date

from app.config import DATE_FORMAT


def format_money(amount: float) -> str:
    # 12345.5 -> «12 345,50 ₽»
    text = f"{amount:,.2f}".replace(",", " ").replace(".", ",")
    return f"{text} ₽"


def format_date(value: date) -> str:
    return value.strftime(DATE_FORMAT)


def today_text() -> str:
    return format_date(date.today())


def first_day_of_month_text() -> str:
    return format_date(date.today().replace(day=1))
