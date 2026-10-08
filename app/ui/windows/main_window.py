"""Главное окно: логотип, итоги бюджета и меню разделов."""
import tkinter as tk
from tkinter import ttk

from app.config import APP_NAME, LOGO_PATH
from app.services.category_service import CategoryService
from app.services.member_service import MemberService
from app.services.operation_service import OperationService
from app.services.report_service import ReportService
from app.ui.formatting import format_money
from app.ui.messages import ask_confirmation
from app.ui.styles import COLOR_BACKGROUND, apply_styles, set_application_icon
from app.ui.windows.categories_window import CategoriesWindow
from app.ui.windows.members_window import MembersWindow
from app.ui.windows.operations_window import OperationsWindow
from app.ui.windows.report_window import ReportWindow


class MainWindow(tk.Tk):
    def __init__(self, member_service: MemberService, category_service: CategoryService,
                 operation_service: OperationService, report_service: ReportService):
        super().__init__()
        self.member_service = member_service
        self.category_service = category_service
        self.operation_service = operation_service
        self.report_service = report_service

        self.title(f"{APP_NAME} — главное меню")
        self.configure(background=COLOR_BACKGROUND)
        self.minsize(640, 440)
        self.geometry("700x450")
        apply_styles(self)
        set_application_icon(self)
        self.protocol("WM_DELETE_WINDOW", self.exit_application)

        self._create_header()
        self._create_summary()
        self._create_menu()
        self.refresh_summary()

    def _create_header(self) -> None:
        header = ttk.Frame(self, padding=(20, 15, 20, 5))
        header.pack(fill="x")
        if LOGO_PATH.exists():
            self.logo_image = tk.PhotoImage(file=str(LOGO_PATH))
            ttk.Label(header, image=self.logo_image).pack(side="left", padx=(0, 15))
        titles = ttk.Frame(header)
        titles.pack(side="left")
        ttk.Label(titles, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(titles, text="Учёт доходов и расходов семьи", style="Hint.TLabel").pack(anchor="w")

    def _create_summary(self) -> None:
        summary = ttk.Frame(self, padding=(20, 10))
        summary.pack(fill="x")
        self.income_label = self._create_card(summary, "Все доходы", "Income.TLabel", 0)
        self.expense_label = self._create_card(summary, "Все расходы", "Expense.TLabel", 1)
        self.balance_label = self._create_card(summary, "Баланс семьи", "Balance.TLabel", 2)

    @staticmethod
    def _create_card(parent, caption: str, value_style: str, column: int) -> ttk.Label:
        parent.columnconfigure(column, weight=1, uniform="cards")
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=0, column=column, sticky="ew", padx=5)
        ttk.Label(card, text=caption, style="CardCaption.TLabel").pack(anchor="w")
        value_label = ttk.Label(card, text="", style=value_style)
        value_label.pack(anchor="w")
        return value_label

    def _create_menu(self) -> None:
        menu = ttk.Frame(self, padding=(25, 10, 25, 20))
        menu.pack(fill="both", expand=True)
        buttons = (
            ("Операции (доходы и расходы)", self.open_operations),
            ("Категории", self.open_categories),
            ("Члены семьи", self.open_members),
            ("Отчёт по категориям", self.open_report),
            ("Выход", self.exit_application),
        )
        for text, command in buttons:
            style = "TButton" if text == "Выход" else "Primary.TButton"
            ttk.Button(menu, text=text, command=command, style=style).pack(fill="x", pady=4)

    def refresh_summary(self) -> None:
        summary = self.report_service.get_summary()
        self.income_label.configure(text=format_money(summary.total_income))
        self.expense_label.configure(text=format_money(summary.total_expense))
        self.balance_label.configure(text=format_money(summary.balance))

    def open_operations(self) -> None:
        OperationsWindow(self, self.operation_service, self.category_service,
                         self.member_service, on_close=self.refresh_summary)

    def open_categories(self) -> None:
        CategoriesWindow(self, self.category_service, on_close=self.refresh_summary)

    def open_members(self) -> None:
        MembersWindow(self, self.member_service, on_close=self.refresh_summary)

    def open_report(self) -> None:
        ReportWindow(self, self.report_service, on_close=self.refresh_summary)

    def exit_application(self) -> None:
        if ask_confirmation(self, "Вы действительно хотите выйти из программы?"):
            self.destroy()
