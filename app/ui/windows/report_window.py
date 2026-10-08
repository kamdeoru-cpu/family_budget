"""Окно «Отчёт по категориям» за выбранный период."""
from tkinter import filedialog, ttk

from app.services.errors import ValidationError
from app.services.report_service import ReportService
from app.ui.components.data_table import DataTable
from app.ui.formatting import first_day_of_month_text, format_money, today_text
from app.ui.messages import show_error, show_info, show_warning
from app.ui.windows.base_window import BaseWindow


class ReportWindow(BaseWindow):
    def __init__(self, parent, report_service: ReportService, on_close=None):
        super().__init__(parent, "Отчёт по категориям", on_close)
        self.report_service = report_service
        self.report_rows = []
        self._create_widgets()
        self.add_footer()
        self.build_report(notify_if_empty=False)

    def _create_widgets(self) -> None:
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(1, weight=1)

        period = ttk.LabelFrame(self.content, text="Период отчёта", padding=10)
        period.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(period, text="с").pack(side="left")
        self.date_from_entry = ttk.Entry(period, width=12)
        self.date_from_entry.insert(0, first_day_of_month_text())
        self.date_from_entry.pack(side="left", padx=5)
        ttk.Label(period, text="по").pack(side="left")
        self.date_to_entry = ttk.Entry(period, width=12)
        self.date_to_entry.insert(0, today_text())
        self.date_to_entry.pack(side="left", padx=5)
        ttk.Label(period, text="(ДД.ММ.ГГГГ)", style="Hint.TLabel").pack(side="left", padx=(0, 15))
        ttk.Button(period, text="Сформировать", style="Primary.TButton", command=self.build_report).pack(side="left")
        ttk.Button(period, text="Сохранить в CSV", command=self.export_report).pack(side="left", padx=5)

        self.table = DataTable(self.content, [
            ("category", "Категория", 260),
            ("kind", "Тип", 100),
            ("count", "Кол-во операций", 130),
            ("total", "Сумма", 150),
        ])
        self.table.grid(row=1, column=0, sticky="nsew")

        self.totals_label = ttk.Label(self.content, text="", style="Subtitle.TLabel")
        self.totals_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def build_report(self, notify_if_empty: bool = True) -> None:
        try:
            rows = self.report_service.build_category_report(
                self.date_from_entry.get(), self.date_to_entry.get()
            )
        except ValidationError as error:
            show_error(self, str(error))
            return
        self.report_rows = rows
        table_rows = []
        for index, row in enumerate(rows):
            values = (row.category_name, row.category_kind, row.operations_count, format_money(row.total_amount))
            table_rows.append((index, values))
        self.table.set_rows(table_rows)
        totals = self.report_service.calculate_totals(rows)
        self.totals_label.configure(
            text=f"Доходы: {format_money(totals.total_income)}    "
                 f"Расходы: {format_money(totals.total_expense)}    "
                 f"Итог за период: {format_money(totals.balance)}"
        )
        if not rows and notify_if_empty:
            show_info(self, "За выбранный период операций нет. Выберите другой период.")

    def export_report(self) -> None:
        if not self.report_rows:
            show_warning(self, "Отчёт пуст. Сначала сформируйте отчёт за период, в котором есть операции.")
            return
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Сохранение отчёта",
            defaultextension=".csv",
            initialfile="otchet_po_kategoriyam.csv",
            filetypes=[("Таблица CSV", "*.csv")],
        )
        if not file_path:
            return
        try:
            self.report_service.export_to_csv(self.report_rows, file_path)
        except OSError:
            show_error(self, "Не удалось сохранить файл. Проверьте, что он не открыт в другой программе, "
                             "или выберите другую папку.", title="Ошибка сохранения")
            return
        show_info(self, f"Отчёт сохранён в файл:\n{file_path}")
