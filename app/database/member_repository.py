"""SQL-запросы к таблице членов семьи."""
from typing import Optional

from app.database.database import Database
from app.models.family_member import FamilyMember


class MemberRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_all(self) -> list[FamilyMember]:
        rows = self.database.fetch_all(
            "SELECT id, full_name, role FROM family_members ORDER BY full_name"
        )
        return [self._to_member(row) for row in rows]

    def get_by_id(self, member_id: int) -> Optional[FamilyMember]:
        row = self.database.fetch_one(
            "SELECT id, full_name, role FROM family_members WHERE id = ?",
            (member_id,),
        )
        if row is None:
            return None
        return self._to_member(row)

    def add(self, member: FamilyMember) -> int:
        cursor = self.database.execute(
            "INSERT INTO family_members (full_name, role) VALUES (?, ?)",
            (member.full_name, member.role),
        )
        return cursor.lastrowid

    def update(self, member: FamilyMember) -> None:
        self.database.execute(
            "UPDATE family_members SET full_name = ?, role = ? WHERE id = ?",
            (member.full_name, member.role, member.member_id),
        )

    def delete(self, member_id: int) -> None:
        self.database.execute("DELETE FROM family_members WHERE id = ?", (member_id,))

    @staticmethod
    def _to_member(row) -> FamilyMember:
        return FamilyMember(row["id"], row["full_name"], row["role"])
