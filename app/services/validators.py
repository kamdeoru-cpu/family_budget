"""Проверка и преобразование значений, введённых пользователем."""
import re
from datetime import date, datetime

from app.config import DATE_FORMAT, MAX_AMOUNT, MIN_YEAR
from app.services.errors import ValidationError

NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё\- ]+$")
AMOUNT_PATTERN = re.compile(r"^\d+([.,]\d{1,2})?$")


def check_text(value: str, field_name: str, min_length: int, max_length: int) -> str:
    text = value.strip()
    if not text:
        raise ValidationError(f"Поле «{field_name}» не заполнено. Введите значение.")
    if len(text) < min_length or len(text) > max_length:
        raise ValidationError(
            f"Поле «{field_name}» должно содержать от {min_length} до {max_length} символов. "
            f"Сейчас символов: {len(text)}."
        )
    return text


def check_person_name(value: str, field_name: str) -> str:
    text = check_text(value, field_name, 2, 50)
    if not NAME_PATTERN.match(text):
        raise ValidationError(
            f"Поле «{field_name}» может содержать только буквы, пробел и дефис. "
            "Уберите цифры и другие символы."
        )
    return text


def parse_amount(value: str) -> float:
    # Разрешаем ввод «1 500,50»: убираем пробелы и меняем запятую на точку
    text = value.replace(" ", "").strip()
    if not text:
        raise ValidationError("Поле «Сумма» не заполнено. Введите сумму, например 1500 или 249,90.")
    if not AMOUNT_PATTERN.match(text):
        raise ValidationError(
            "Сумма введена неверно. Используйте только цифры и не более двух знаков "
            "после запятой, например 1500 или 249,90."
        )
    amount = float(text.replace(",", "."))
    if amount <= 0:
        raise ValidationError("Сумма должна быть больше нуля.")
    if amount > MAX_AMOUNT:
        raise ValidationError(f"Сумма одной операции не может превышать {MAX_AMOUNT:,} руб.".replace(",", " "))
    return round(amount, 2)


def parse_date(value: str, field_name: str = "Дата") -> date:
    text = value.strip()
    try:
        parsed = datetime.strptime(text, DATE_FORMAT).date()
    except ValueError:
        raise ValidationError(
            f"Поле «{field_name}» заполнено неверно. Введите дату в формате ДД.ММ.ГГГГ, "
            "например 05.10.2026."
        ) from None
    if parsed.year < MIN_YEAR:
        raise ValidationError(f"Поле «{field_name}»: дата не может быть раньше {MIN_YEAR} года.")
    if parsed > date.today():
        raise ValidationError(f"Поле «{field_name}»: дата не может быть в будущем.")
    return parsed
