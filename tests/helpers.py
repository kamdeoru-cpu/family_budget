"""Общая подготовка для тестов: база данных в оперативной памяти."""
from app.database.category_repository import CategoryRepository
from app.database.database import IN_MEMORY, Database
from app.database.member_repository import MemberRepository
from app.database.operation_repository import OperationRepository
from app.services.category_service import CategoryService
from app.services.member_service import MemberService
from app.services.operation_service import OperationService
from app.services.report_service import ReportService


class TestContext:
    """Создаёт чистую базу и все сервисы. Файл на диске не создаётся."""

    def __init__(self):
        self.database = Database(IN_MEMORY)
        member_repository = MemberRepository(self.database)
        self.category_repository = CategoryRepository(self.database)
        operation_repository = OperationRepository(self.database)
        self.member_service = MemberService(member_repository, operation_repository)
        self.category_service = CategoryService(self.category_repository, operation_repository)
        self.operation_service = OperationService(operation_repository, self.category_repository, member_repository)
        self.report_service = ReportService(operation_repository)

    def category_id(self, name: str) -> int:
        return self.category_repository.find_by_name(name).category_id

    def close(self) -> None:
        self.database.close()
