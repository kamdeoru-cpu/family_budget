"""Таблица с прокруткой, которая растягивается вместе с окном."""
from tkinter import ttk
from typing import Callable, Optional


class DataTable(ttk.Frame):
    def __init__(self, parent, columns: list[tuple[str, str, int]]):
        """columns — список (ключ, заголовок, ширина) для каждого столбца."""
        super().__init__(parent)
        keys = [column[0] for column in columns]
        self.tree = ttk.Treeview(self, columns=keys, show="headings", selectmode="browse")
        for key, heading, width in columns:
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=width, minwidth=60)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def set_rows(self, rows: list[tuple[int, tuple]]) -> None:
        """rows — список (идентификатор записи, значения столбцов)."""
        self.tree.delete(*self.tree.get_children())
        for row_id, values in rows:
            self.tree.insert("", "end", iid=str(row_id), values=values)

    def get_selected_id(self) -> Optional[int]:
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def clear_selection(self) -> None:
        self.tree.selection_remove(self.tree.selection())

    def on_select(self, callback: Callable[[], None]) -> None:
        self.tree.bind("<<TreeviewSelect>>", lambda event: callback())
