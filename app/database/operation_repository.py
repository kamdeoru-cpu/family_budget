"""SQL-запросы к таблице операций."""
from datetime import date
from typing import Optional

from app.database.database import Database
from app.models.operation import Operation
from app.models.report import BudgetSummary, CategoryReportRow

SELECT_OPERATIONS = """
SELECT o.id, o.operation_date, o.amount, o.category_id, o.member_id, o.comment,
       c.name AS category_name, c.kind AS category_kind,
       m.full_name AS member_name
FROM operations o
JOIN categories c ON c.id = o.category_id
JOIN family_members m ON m.id = o.member_id
"""


class OperationRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_all(self, kind: Optional[str] = None) -> list[Operation]:
        sql = SELECT_OPERATIONS
        params = ()
        if kind:
            sql += " WHERE c.kind = ?"
            params = (kind,)
        sql += " ORDER BY o.operation_date DESC, o.id DESC"
        rows = self.database.fetch_all(sql, params)
        return [self._to_operation(row) for row in rows]

    def get_by_id(self, operation_id: int) -> Optional[Operation]:
        row = self.database.fetch_one(SELECT_OPERATIONS + " WHERE o.id = ?", (operation_id,))
        if row is None:
            return None
        return self._to_operation(row)

    def add(self, operation: Operation) -> int:
        cursor = self.database.execute(
            "INSERT INTO operations (operation_date, amount, category_id, member_id, comment) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                operation.operation_date.isoformat(),
                operation.amount,
                operation.category_id,
                operation.member_id,
                operation.comment,
            ),
        )
        return cursor.lastrowid

    def update(self, operation: Operation) -> None:
        self.database.execute(
            "UPDATE operations SET operation_date = ?, amount = ?, category_id = ?, "
            "member_id = ?, comment = ? WHERE id = ?",
            (
                operation.operation_date.isoformat(),
                operation.amount,
                operation.category_id,
                operation.member_id,
                operation.comment,
                operation.operation_id,
            ),
        )

    def delete(self, operation_id: int) -> None:
        self.database.execute("DELETE FROM operations WHERE id = ?", (operation_id,))

    def count_by_category(self, category_id: int) -> int:
        row = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM operations WHERE category_id = ?",
            (category_id,),
        )
        return row["total"]

    def count_by_member(self, member_id: int) -> int:
        row = self.database.fetch_one(
            "SELECT COUNT(*) AS total FROM operations WHERE member_id = ?",
            (member_id,),
        )
        return row["total"]

    def get_summary(self) -> BudgetSummary:
        row = self.database.fetch_one(
            """
            SELECT
                COALESCE(SUM(CASE WHEN c.kind = 'Доход' THEN o.amount END), 0) AS income,
                COALESCE(SUM(CASE WHEN c.kind = 'Расход' THEN o.amount END), 0) AS expense
            FROM operations o
            JOIN categories c ON c.id = o.category_id
            """
        )
        return BudgetSummary(row["income"], row["expense"])

    def get_report_by_categories(self, date_from: date, date_to: date) -> list[CategoryReportRow]:
        rows = self.database.fetch_all(
            """
            SELECT c.name, c.kind, COUNT(o.id) AS operations_count, SUM(o.amount) AS total
            FROM operations o
            JOIN categories c ON c.id = o.category_id
            WHERE o.operation_date BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY c.kind, total DESC
            """,
            (date_from.isoformat(), date_to.isoformat()),
        )
        return [
            CategoryReportRow(row["name"], row["kind"], row["operations_count"], row["total"])
            for row in rows
        ]

    @staticmethod
    def _to_operation(row) -> Operation:
        return Operation(
            operation_id=row["id"],
            operation_date=date.fromisoformat(row["operation_date"]),
            amount=row["amount"],
            category_id=row["category_id"],
            member_id=row["member_id"],
            comment=row["comment"],
            category_name=row["category_name"],
            category_kind=row["category_kind"],
            member_name=row["member_name"],
        )
