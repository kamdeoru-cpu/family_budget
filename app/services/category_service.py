"""Бизнес-логика работы с категориями доходов и расходов."""
from typing import Optional

from app.database.category_repository import CategoryRepository
from app.database.operation_repository import OperationRepository
from app.models.category import CATEGORY_KINDS, Category
from app.services.errors import BusinessRuleError, ValidationError
from app.services.validators import check_text


class CategoryService:
    def __init__(self, category_repository: CategoryRepository, operation_repository: OperationRepository):
        self.category_repository = category_repository
        self.operation_repository = operation_repository

    def get_all(self) -> list[Category]:
        return self.category_repository.get_all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.category_repository.get_by_id(category_id)

    def add(self, name: str, kind: str) -> int:
        category = self._build_category(None, name, kind)
        return self.category_repository.add(category)

    def update(self, category_id: int, name: str, kind: str) -> None:
        category = self._build_category(category_id, name, kind)
        old_category = self.category_repository.get_by_id(category_id)
        used_count = self.operation_repository.count_by_category(category_id)
        # Если поменять тип у используемой категории, «переедут» все её операции
        # и баланс семьи станет неверным, поэтому такое запрещено.
        if old_category and old_category.kind != category.kind and used_count > 0:
            raise BusinessRuleError(
                "Нельзя изменить тип категории, по которой уже есть операции "
                f"(операций: {used_count}). Создайте новую категорию нужного типа."
            )
        self.category_repository.update(category)

    def delete(self, category_id: int) -> None:
        used_count = self.operation_repository.count_by_category(category_id)
        if used_count > 0:
            raise BusinessRuleError(
                f"Нельзя удалить категорию: по ней есть операции — {used_count}. "
                "Сначала удалите эти операции или перенесите их в другую категорию."
            )
        self.category_repository.delete(category_id)

    def _build_category(self, category_id: Optional[int], name: str, kind: str) -> Category:
        checked_name = check_text(name, "Название", 2, 40)
        if kind not in CATEGORY_KINDS:
            raise ValidationError("Выберите тип категории из списка: «Доход» или «Расход».")
        same_name = self.category_repository.find_by_name(checked_name)
        if same_name and same_name.category_id != category_id:
            raise BusinessRuleError(
                f"Категория «{same_name.name}» уже существует. Введите другое название."
            )
        return Category(category_id, checked_name, kind)
