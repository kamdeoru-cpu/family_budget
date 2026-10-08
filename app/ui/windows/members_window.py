"""Окно «Члены семьи»: просмотр, добавление, изменение и удаление."""
from typing import Optional

from app.services.errors import BusinessRuleError, ValidationError
from app.services.member_service import MemberService
from app.ui.components.data_table import DataTable
from app.ui.components.form_panel import FormPanel
from app.ui.messages import ask_confirmation, show_error, show_info, show_warning
from app.ui.windows.base_window import BaseWindow


class MembersWindow(BaseWindow):
    def __init__(self, parent, member_service: MemberService, on_close=None):
        super().__init__(parent, "Члены семьи", on_close)
        self.member_service = member_service
        self.selected_member_id: Optional[int] = None
        self._create_widgets()
        self.add_footer()
        self.refresh_table()

    def _create_widgets(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.table = DataTable(self.content, [("full_name", "ФИО", 300), ("role", "Роль в семье", 180)])
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.table.on_select(self.on_row_selected)

        form = FormPanel(self.content, "Данные члена семьи")
        form.grid(row=0, column=1, sticky="ns")
        self.full_name_var = form.add_entry("ФИО *", "Только буквы, пробел и дефис, от 2 до 50 символов")
        self.role_var = form.add_entry("Роль в семье *", "Например: мама, папа, сын, бабушка")
        form.add_buttons([
            ("Добавить", self.add_member),
            ("Сохранить", self.update_member),
            ("Удалить", self.delete_member),
            ("Очистить", self.clear_form),
        ])

    def refresh_table(self) -> None:
        members = self.member_service.get_all()
        self.table.set_rows([(member.member_id, (member.full_name, member.role)) for member in members])

    def on_row_selected(self) -> None:
        member_id = self.table.get_selected_id()
        if member_id is None:
            return
        member = self.member_service.get_by_id(member_id)
        self.selected_member_id = member_id
        self.full_name_var.set(member.full_name)
        self.role_var.set(member.role)

    def add_member(self) -> None:
        try:
            self.member_service.add(self.full_name_var.get(), self.role_var.get())
        except ValidationError as error:
            show_error(self, str(error))
            return
        show_info(self, "Член семьи успешно добавлен.")
        self.clear_form()
        self.refresh_table()

    def update_member(self) -> None:
        if self.selected_member_id is None:
            show_warning(self, "Сначала выберите в таблице члена семьи, которого нужно изменить.")
            return
        try:
            self.member_service.update(self.selected_member_id, self.full_name_var.get(), self.role_var.get())
        except ValidationError as error:
            show_error(self, str(error))
            return
        show_info(self, "Изменения сохранены.")
        self.refresh_table()

    def delete_member(self) -> None:
        if self.selected_member_id is None:
            show_warning(self, "Сначала выберите в таблице члена семьи, которого нужно удалить.")
            return
        member = self.member_service.get_by_id(self.selected_member_id)
        question = f"Удалить члена семьи «{member.full_name}»?\nЭто действие нельзя отменить."
        if not ask_confirmation(self, question):
            return
        try:
            self.member_service.delete(self.selected_member_id)
        except BusinessRuleError as error:
            show_warning(self, str(error))
            return
        self.clear_form()
        self.refresh_table()

    def clear_form(self) -> None:
        self.selected_member_id = None
        self.full_name_var.set("")
        self.role_var.set("")
        self.table.clear_selection()
