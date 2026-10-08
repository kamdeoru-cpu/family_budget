"""Точка входа: создаёт базу данных, сервисы и главное окно."""
import logging
import sqlite3
import sys
import traceback
from tkinter import messagebox

from app.config import DATA_DIR, LOG_PATH
from app.database.category_repository import CategoryRepository
from app.database.database import Database
from app.database.member_repository import MemberRepository
from app.database.operation_repository import OperationRepository
from app.services.category_service import CategoryService
from app.services.member_service import MemberService
from app.services.operation_service import OperationService
from app.services.report_service import ReportService
from app.ui.windows.main_window import MainWindow

UNEXPECTED_ERROR_TEXT = (
    "Произошла непредвиденная ошибка, но программа продолжает работу.\n\n"
    "Повторите действие. Если ошибка повторяется, перезапустите программу.\n"
    "Подробности записаны в файл data/errors.log."
)


def setup_logging() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def handle_unexpected_error(exc_type, exc_value, exc_traceback) -> None:
    """Перехватывает любые необработанные ошибки в окнах, чтобы программа не «вылетала»."""
    details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Необработанная ошибка:\n%s", details)
    messagebox.showerror("Непредвиденная ошибка", UNEXPECTED_ERROR_TEXT)


def create_main_window(database: Database) -> MainWindow:
    member_repository = MemberRepository(database)
    category_repository = CategoryRepository(database)
    operation_repository = OperationRepository(database)
    return MainWindow(
        member_service=MemberService(member_repository, operation_repository),
        category_service=CategoryService(category_repository, operation_repository),
        operation_service=OperationService(operation_repository, category_repository, member_repository),
        report_service=ReportService(operation_repository),
    )


def main() -> None:
    setup_logging()
    try:
        database = Database()
    except (sqlite3.Error, OSError) as error:
        logging.error("Не удалось открыть базу данных: %s", error)
        messagebox.showerror(
            "Ошибка запуска",
            "Не удалось открыть файл базы данных.\n"
            "Проверьте, что папка программы доступна для записи, и запустите программу снова.",
        )
        sys.exit(1)

    window = create_main_window(database)
    window.report_callback_exception = handle_unexpected_error
    window.mainloop()
    database.close()


if __name__ == "__main__":
    main()
