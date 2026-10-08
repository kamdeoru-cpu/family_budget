"""Подключение к базе данных SQLite и создание таблиц."""
import sqlite3
from pathlib import Path
from typing import Union

from app.config import DATABASE_PATH

IN_MEMORY = ":memory:"

SCHEMA = """
CREATE TABLE IF NOT EXISTS family_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('Доход', 'Расход'))
);

CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    category_id INTEGER NOT NULL REFERENCES categories (id),
    member_id INTEGER NOT NULL REFERENCES family_members (id),
    comment TEXT NOT NULL DEFAULT ''
);
"""

DEFAULT_CATEGORIES = (
    ("Зарплата", "Доход"),
    ("Подработка", "Доход"),
    ("Продукты", "Расход"),
    ("Коммунальные услуги", "Расход"),
    ("Транспорт", "Расход"),
    ("Развлечения", "Расход"),
)


class Database:
    """Хранит одно соединение с базой и выполняет SQL-запросы."""

    def __init__(self, path: Union[str, Path] = DATABASE_PATH):
        if str(path) != IN_MEMORY:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        # По умолчанию SQLite не проверяет внешние ключи — включаем явно
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)
        self._fill_default_categories()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cursor = self.connection.execute(sql, params)
        self.connection.commit()
        return cursor

    def fetch_all(self, sql: str, params: tuple = ()) -> list:
        return self.connection.execute(sql, params).fetchall()

    def fetch_one(self, sql: str, params: tuple = ()):
        return self.connection.execute(sql, params).fetchone()

    def close(self) -> None:
        self.connection.close()

    def _fill_default_categories(self) -> None:
        row = self.fetch_one("SELECT COUNT(*) AS total FROM categories")
        if row["total"] > 0:
            return
        self.connection.executemany(
            "INSERT INTO categories (name, kind) VALUES (?, ?)",
            DEFAULT_CATEGORIES,
        )
        self.connection.commit()
