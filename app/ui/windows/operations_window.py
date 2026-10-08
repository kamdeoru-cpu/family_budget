"""Окно «Операции»: журнал доходов и расходов с фильтром и поиском."""
from tkinter import ttk
from typing import Optional

from app.models.category import CATEGORY_KINDS
from app.services.category_service import CategoryService
from app.services.errors import ValidationError
from app.services.member_service import MemberService
from app.services.operation_service import OperationService
from app.ui.components.data_table import DataTable
from app.ui.components.form_panel import FormPanel
from app.ui.formatting import format_date, format_money, today_text
from app.ui.messages import ask_confirmation, show_error, show_info, show_warning
from app.ui.windows.base_window import BaseWindow

ALL_KINDS = "Все"


class OperationsWindow(BaseWindow):
    def __init__(self, parent, operation_service: OperationService, category_service: CategoryService,
                 member_service: MemberService, on_close=None):
        super().__init__(parent, "Операции: доходы и расходы", on_close)
        self.operation_service = operation_service
        self.category_service = category_service
        self.member_service = member_service
        self.selected_operation_id: Optional[int] = None
        self.categories = []
        self.members = []
        self._create_filter_panel()
        self._create_widgets()
        self.add_footer()
        self.load_reference_lists()
        self.refresh_table()

    def _create_filter_panel(self) -> None:
        panel = ttk.Frame(self.content)
        panel.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(panel, text="Тип:").pack(side="left")
        self.kind_filter = ttk.Combobox(panel, state="readonly", width=10, values=(ALL_KINDS,) + CATEGORY_KINDS)
        self.kind_filter.set(ALL_KINDS)
        self.kind_filter.pack(side="left", padx=(5, 15))
        self.kind_filter.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        ttk.Label(panel, text="Поиск:").pack(side="left")
        self.search_entry = ttk.Entry(panel, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search())
        ttk.Button(panel, text="Найти", command=self.search).pack(side="left", padx=(0, 5))
        ttk.Button(panel, text="Сбросить", command=self.reset_filter).pack(side="left")
        self.count_label = ttk.Label(panel, text="", style="Hint.TLabel")
        self.count_label.pack(side="right")

    def _create_widgets(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        self.table = DataTable(self.content, [
            ("date", "Дата", 85),
            ("kind", "Тип", 65),
            ("category", "Категория", 140),
            ("amount", "Сумма", 105),
            ("member", "Член семьи", 170),
            ("comment", "Комментарий", 160),
        ])
        self.table.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.table.on_select(self.on_row_selected)

        form = FormPanel(self.content, "Данные операции")
        form.grid(row=1, column=1, sticky="ns")
        self.date_var = form.add_entry("Дата *", "Формат ДД.ММ.ГГГГ, не позже сегодняшнего дня")
        self.amount_var = form.add_entry("Сумма, руб. *", "Например: 1500 или 249,90")
        self.category_combobox = form.add_combobox("Категория *")
        self.member_combobox = form.add_combobox("Член семьи *")
        self.comment_var = form.add_entry("Комментарий", "Необязательно, до 200 символов")
        form.add_buttons([
            ("Добавить", self.add_operation),
            ("Сохранить", self.update_operation),
            ("Удалить", self.delete_operation),
            ("Очистить", self.clear_form),
        ])
        self.date_var.set(today_text())

    def load_reference_lists(self) -> None:
        """Заполняет выпадающие списки категориями и членами семьи из базы."""
        self.categories = self.category_service.get_all()
        self.members = self.member_service.get_all()
        self.category_combobox["values"] = [category.display_name for category in self.categories]
        self.member_combobox["values"] = [member.full_name for member in self.members]

    def refresh_table(self) -> list:
        kind = self.kind_filter.get()
        selected_kind = None if kind == ALL_KINDS else kind
        operations = self.operation_service.find(selected_kind, self.search_entry.get())
        rows = []
        for operation in operations:
            values = (
                format_date(operation.operation_date),
                operation.category_kind,
                operation.category_name,
                format_money(operation.amount),
                operation.member_name,
                operation.comment,
            )
            rows.append((operation.operation_id, values))
        self.table.set_rows(rows)
        self.count_label.configure(text=f"Показано операций: {len(rows)}")
        return operations

    def search(self) -> None:
        operations = self.refresh_table()
        if not operations:
            show_info(self, "По вашему запросу ничего не найдено. Измените текст поиска или тип операции.")

    def reset_filter(self) -> None:
        self.kind_filter.set(ALL_KINDS)
        self.search_entry.delete(0, "end")
        self.refresh_table()

    def on_row_selected(self) -> None:
        operation_id = self.table.get_selected_id()
        if operation_id is None:
            return
        operation = self.operation_service.get_by_id(operation_id)
        self.selected_operation_id = operation_id
        self.date_var.set(format_date(operation.operation_date))
        self.amount_var.set(f"{operation.amount:.2f}".replace(".", ","))
        self.comment_var.set(operation.comment)
        self._select_in_combobox(self.category_combobox, self._category_ids(), operation.category_id)
        self._select_in_combobox(self.member_combobox, self._member_ids(), operation.member_id)

    def add_operation(self) -> None:
        category_id = self._selected_category_id()
        amount_text = self.amount_var.get()
        if self.operation_service.is_expense_above_balance(amount_text, category_id):
            question = ("Сумма расхода больше текущего баланса семьи, баланс станет отрицательным.\n"
                        "Всё равно добавить операцию?")
            if not ask_confirmation(self, question):
                return
        try:
            self.operation_service.add(
                self.date_var.get(), amount_text, category_id,
                self._selected_member_id(), self.comment_var.get(),
            )
        except ValidationError as error:
            show_error(self, str(error))
            return
        show_info(self, "Операция успешно добавлена.")
        self.clear_form()
        self.refresh_table()

    def update_operation(self) -> None:
        if self.selected_operation_id is None:
            show_warning(self, "Сначала выберите в таблице операцию, которую нужно изменить.")
            return
        try:
            self.operation_service.update(
                self.selected_operation_id, self.date_var.get(), self.amount_var.get(),
                self._selected_category_id(), self._selected_member_id(), self.comment_var.get(),
            )
        except ValidationError as error:
            show_error(self, str(error))
            return
        show_info(self, "Изменения сохранены.")
        self.refresh_table()

    def delete_operation(self) -> None:
        if self.selected_operation_id is None:
            show_warning(self, "Сначала выберите в таблице операцию, которую нужно удалить.")
            return
        operation = self.operation_service.get_by_id(self.selected_operation_id)
        question = (f"Удалить операцию «{operation.category_name}» на сумму "
                    f"{format_money(operation.amount)} от {format_date(operation.operation_date)}?\n"
                    "Это действие нельзя отменить.")
        if not ask_confirmation(self, question):
            return
        self.operation_service.delete(self.selected_operation_id)
        self.clear_form()
        self.refresh_table()

    def clear_form(self) -> None:
        self.selected_operation_id = None
        self.date_var.set(today_text())
        self.amount_var.set("")
        self.comment_var.set("")
        self.category_combobox.set("")
        self.member_combobox.set("")
        self.table.clear_selection()

    def _category_ids(self) -> list[int]:
        return [category.category_id for category in self.categories]

    def _member_ids(self) -> list[int]:
        return [member.member_id for member in self.members]

    def _selected_category_id(self) -> Optional[int]:
        index = self.category_combobox.current()
        if index < 0:
            return None
        return self.categories[index].category_id

    def _selected_member_id(self) -> Optional[int]:
        index = self.member_combobox.current()
        if index < 0:
            return None
        return self.members[index].member_id

    @staticmethod
    def _select_in_combobox(combobox: ttk.Combobox, ids: list[int], selected_id: int) -> None:
        if selected_id in ids:
            combobox.current(ids.index(selected_id))
