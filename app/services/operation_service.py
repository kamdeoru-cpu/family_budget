"""Бизнес-логика работы с операциями (доходами и расходами)."""
from typing import Optional

from app.config import MAX_COMMENT_LENGTH
from app.database.category_repository import CategoryRepository
from app.database.member_repository import MemberRepository
from app.database.operation_repository import OperationRepository
from app.models.operation import Operation
from app.services.errors import ValidationError
from app.services.validators import parse_amount, parse_date


class OperationService:
    def __init__(
        self,
        operation_repository: OperationRepository,
        category_repository: CategoryRepository,
        member_repository: MemberRepository,
    ):
        self.operation_repository = operation_repository
        self.category_repository = category_repository
        self.member_repository = member_repository

    def find(self, kind: Optional[str] = None, search_text: str = "") -> list[Operation]:
        operations = self.operation_repository.get_all(kind)
        query = search_text.strip().lower()
        if not query:
            return operations
        # Поиск делаем в Python: так он не зависит от регистра русских букв
        return [
            operation
            for operation in operations
            if query in operation.comment.lower()
            or query in operation.category_name.lower()
            or query in operation.member_name.lower()
        ]

    def get_by_id(self, operation_id: int) -> Optional[Operation]:
        return self.operation_repository.get_by_id(operation_id)

    def add(self, date_text: str, amount_text: str, category_id: Optional[int],
            member_id: Optional[int], comment: str) -> int:
        operation = self._build_operation(None, date_text, amount_text, category_id, member_id, comment)
        return self.operation_repository.add(operation)

    def update(self, operation_id: int, date_text: str, amount_text: str,
               category_id: Optional[int], member_id: Optional[int], comment: str) -> None:
        operation = self._build_operation(
            operation_id, date_text, amount_text, category_id, member_id, comment
        )
        self.operation_repository.update(operation)

    def delete(self, operation_id: int) -> None:
        self.operation_repository.delete(operation_id)

    def is_expense_above_balance(self, amount_text: str, category_id: Optional[int]) -> bool:
        """Проверяет, уйдёт ли баланс в минус после добавления расхода."""
        if category_id is None:
            return False
        category = self.category_repository.get_by_id(category_id)
        if category is None or not category.is_expense:
            return False
        try:
            amount = parse_amount(amount_text)
        except ValidationError:
            return False
        balance = self.operation_repository.get_summary().balance
        return amount > balance

    def _build_operation(self, operation_id: Optional[int], date_text: str, amount_text: str,
                         category_id: Optional[int], member_id: Optional[int],
                         comment: str) -> Operation:
        operation_date = parse_date(date_text, "Дата")
        amount = parse_amount(amount_text)
        if category_id is None or self.category_repository.get_by_id(category_id) is None:
            raise ValidationError("Выберите категорию из выпадающего списка.")
        if member_id is None or self.member_repository.get_by_id(member_id) is None:
            raise ValidationError(
                "Выберите члена семьи из выпадающего списка. Если список пуст, "
                "сначала добавьте членов семьи в разделе «Члены семьи»."
            )
        clean_comment = comment.strip()
        if len(clean_comment) > MAX_COMMENT_LENGTH:
            raise ValidationError(
                f"Комментарий слишком длинный: {len(clean_comment)} символов. "
                f"Максимум — {MAX_COMMENT_LENGTH}."
            )
        return Operation(operation_id, operation_date, amount, category_id, member_id, clean_comment)
