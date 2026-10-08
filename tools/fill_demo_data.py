"""Заполняет базу примерами, чтобы показать работу программы на защите.

Запуск из папки проекта:  python tools/fill_demo_data.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

# Добавляем папку проекта в путь поиска модулей, чтобы работал импорт app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.category_repository import CategoryRepository  # noqa: E402
from app.database.database import Database  # noqa: E402
from app.database.member_repository import MemberRepository  # noqa: E402
from app.database.operation_repository import OperationRepository  # noqa: E402
from app.services.member_service import MemberService  # noqa: E402
from app.services.operation_service import OperationService  # noqa: E402

DEMO_MEMBERS = (
    ("Петров Андрей Сергеевич", "Папа"),
    ("Петрова Ольга Викторовна", "Мама"),
    ("Петров Максим Андреевич", "Сын"),
)

# (сколько дней назад, сумма, категория, номер члена семьи, комментарий)
DEMO_OPERATIONS = (
    (40, "85000", "Зарплата", 0, "Зарплата за прошлый месяц"),
    (38, "62000", "Зарплата", 1, "Зарплата за прошлый месяц"),
    (36, "7840,50", "Коммунальные услуги", 1, "Квартплата и электричество"),
    (33, "5320", "Продукты", 1, "Закупка в гипермаркете"),
    (30, "1500", "Транспорт", 2, "Пополнение проездного"),
    (27, "2400", "Развлечения", 0, "Кино всей семьёй"),
    (24, "4150,90", "Продукты", 0, "Продукты на неделю"),
    (20, "12000", "Подработка", 2, "Летняя подработка"),
    (15, "85000", "Зарплата", 0, "Зарплата"),
    (14, "62000", "Зарплата", 1, "Зарплата"),
    (12, "8120", "Коммунальные услуги", 1, "Квартплата"),
    (9, "6230,40", "Продукты", 1, "Продукты и бытовая химия"),
    (7, "1500", "Транспорт", 2, "Проездной"),
    (5, "3600", "Развлечения", 2, "Концерт"),
    (3, "2890", "Продукты", 0, "Рынок"),
    (1, "950", "Транспорт", 0, "Такси"),
)


def main() -> None:
    database = Database()
    member_repository = MemberRepository(database)
    category_repository = CategoryRepository(database)
    operation_repository = OperationRepository(database)
    member_service = MemberService(member_repository, operation_repository)
    operation_service = OperationService(operation_repository, category_repository, member_repository)

    if member_service.get_all():
        print("В базе уже есть данные — демонстрационные данные не добавлены.")
        return

    member_ids = [member_service.add(name, role) for name, role in DEMO_MEMBERS]
    for days_ago, amount, category_name, member_index, comment in DEMO_OPERATIONS:
        operation_date = (date.today() - timedelta(days=days_ago)).strftime("%d.%m.%Y")
        category = category_repository.find_by_name(category_name)
        operation_service.add(operation_date, amount, category.category_id, member_ids[member_index], comment)
    print(f"Добавлено членов семьи: {len(DEMO_MEMBERS)}, операций: {len(DEMO_OPERATIONS)}.")
    database.close()


if __name__ == "__main__":
    main()
