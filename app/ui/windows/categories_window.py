"""Окно «Категории»: статьи доходов и расходов."""
from typing import Optional

from app.models.category import CATEGORY_KINDS
from app.services.category_service import CategoryService
from app.services.errors import BusinessRuleError, ValidationError
from app.ui.components.data_table import DataTable
from app.ui.components.form_panel import FormPanel
from app.ui.messages import ask_confirmation, show_error, show_info, show_warning
from app.ui.windows.base_window import BaseWindow


class CategoriesWindow(BaseWindow):
    def __init__(self, parent, category_service: CategoryService, on_close=None):
        super().__init__(parent, "Категории доходов и расходов", on_close)
        self.category_service = category_service
        self.selected_category_id: Optional[int] = None
        self._create_widgets()
        self.add_footer()
        self.refresh_table()

    def _create_widgets(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.table = DataTable(self.content, [("name", "Название", 300), ("kind", "Тип", 150)])
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.table.on_select(self.on_row_selected)

        form = FormPanel(self.content, "Данные категории")
        form.grid(row=0, column=1, sticky="ns")
        self.name_var = form.add_entry("Название *", "От 2 до 40 символов, названия не повторяются")
        self.kind_combobox = form.add_combobox("Тип *", "Доход — деньги приходят, расход — уходят")
        self.kind_combobox["values"] = CATEGORY_KINDS
        form.add_buttons([
            ("Добавить", self.add_category),
            ("Сохранить", self.update_category),
            ("Удалить", self.delete_category),
            ("Очистить", self.clear_form),
        ])

    def refresh_table(self) -> None:
        categories = self.category_service.get_all()
        rows = [(category.category_id, (category.name, category.kind)) for category in categories]
        self.table.set_rows(rows)

    def on_row_selected(self) -> None:
        category_id = self.table.get_selected_id()
        if category_id is None:
            return
        category = self.category_service.get_by_id(category_id)
        self.selected_category_id = category_id
        self.name_var.set(category.name)
        self.kind_combobox.set(category.kind)

    def add_category(self) -> None:
        try:
            self.category_service.add(self.name_var.get(), self.kind_combobox.get())
        except ValidationError as error:
            show_error(self, str(error))
            return
        except BusinessRuleError as error:
            show_warning(self, str(error))
            return
        show_info(self, "Категория успешно добавлена.")
        self.clear_form()
        self.refresh_table()

    def update_category(self) -> None:
        if self.selected_category_id is None:
            show_warning(self, "Сначала выберите в таблице категорию, которую нужно изменить.")
            return
        try:
            self.category_service.update(
                self.selected_category_id, self.name_var.get(), self.kind_combobox.get()
            )
        except ValidationError as error:
            show_error(self, str(error))
            return
        except BusinessRuleError as error:
            show_warning(self, str(error))
            return
        show_info(self, "Изменения сохранены.")
        self.refresh_table()

    def delete_category(self) -> None:
        if self.selected_category_id is None:
            show_warning(self, "Сначала выберите в таблице категорию, которую нужно удалить.")
            return
        category = self.category_service.get_by_id(self.selected_category_id)
        question = f"Удалить категорию «{category.name}»?\nЭто действие нельзя отменить."
        if not ask_confirmation(self, question):
            return
        try:
            self.category_service.delete(self.selected_category_id)
        except BusinessRuleError as error:
            show_warning(self, str(error))
            return
        self.clear_form()
        self.refresh_table()

    def clear_form(self) -> None:
        self.selected_category_id = None
        self.name_var.set("")
        self.kind_combobox.set("")
        self.table.clear_selection()
