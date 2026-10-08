"""Бизнес-логика работы с членами семьи."""
from typing import Optional

from app.database.member_repository import MemberRepository
from app.database.operation_repository import OperationRepository
from app.models.family_member import FamilyMember
from app.services.errors import BusinessRuleError
from app.services.validators import check_person_name, check_text


class MemberService:
    def __init__(self, member_repository: MemberRepository, operation_repository: OperationRepository):
        self.member_repository = member_repository
        self.operation_repository = operation_repository

    def get_all(self) -> list[FamilyMember]:
        return self.member_repository.get_all()

    def get_by_id(self, member_id: int) -> Optional[FamilyMember]:
        return self.member_repository.get_by_id(member_id)

    def add(self, full_name: str, role: str) -> int:
        member = self._build_member(None, full_name, role)
        return self.member_repository.add(member)

    def update(self, member_id: int, full_name: str, role: str) -> None:
        member = self._build_member(member_id, full_name, role)
        self.member_repository.update(member)

    def delete(self, member_id: int) -> None:
        operations_count = self.operation_repository.count_by_member(member_id)
        if operations_count > 0:
            raise BusinessRuleError(
                f"Нельзя удалить члена семьи: за ним записано операций — {operations_count}. "
                "Сначала удалите или переназначьте эти операции."
            )
        self.member_repository.delete(member_id)

    @staticmethod
    def _build_member(member_id: Optional[int], full_name: str, role: str) -> FamilyMember:
        checked_name = check_person_name(full_name, "ФИО")
        checked_role = check_text(role, "Роль в семье", 2, 30)
        return FamilyMember(member_id, checked_name, checked_role)
