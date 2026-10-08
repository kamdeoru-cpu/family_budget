"""SQL-запросы к таблице категорий."""
from typing import Optional

from app.database.database import Database
from app.models.category import Category


class CategoryRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_all(self) -> list[Category]:
        rows = self.database.fetch_all(
            "SELECT id, name, kind FROM categories ORDER BY kind, name"
        )
        return [self._to_category(row) for row in rows]

    def get_by_id(self, category_id: int) -> Optional[Category]:
        row = self.database.fetch_one(
            "SELECT id, name, kind FROM categories WHERE id = ?",
            (category_id,),
        )
        if row is None:
            return None
        return self._to_category(row)

    def find_by_name(self, name: str) -> Optional[Category]:
        # Сравнение без учёта регистра, чтобы не было «Продукты» и «продукты»
        rows = self.database.fetch_all("SELECT id, name, kind FROM categories")
        for row in rows:
            if row["name"].lower() == name.lower():
                return self._to_category(row)
        return None

    def add(self, category: Category) -> int:
        cursor = self.database.execute(
            "INSERT INTO categories (name, kind) VALUES (?, ?)",
            (category.name, category.kind),
        )
        return cursor.lastrowid

    def update(self, category: Category) -> None:
        self.database.execute(
            "UPDATE categories SET name = ?, kind = ? WHERE id = ?",
            (category.name, category.kind, category.category_id),
        )

    def delete(self, category_id: int) -> None:
        self.database.execute("DELETE FROM categories WHERE id = ?", (category_id,))

    @staticmethod
    def _to_category(row) -> Category:
        return Category(row["id"], row["name"], row["kind"])
