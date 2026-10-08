"""Панель формы: подписи, поля ввода, подсказки и кнопки в одном стиле."""
import tkinter as tk
from tkinter import ttk
from typing import Callable


class FormPanel(ttk.LabelFrame):
    def __init__(self, parent, title: str):
        super().__init__(parent, text=title, padding=12)
        self.columnconfigure(0, weight=1)
        self._next_row = 0

    def add_entry(self, label_text: str, hint_text: str = "") -> tk.StringVar:
        variable = tk.StringVar()
        self._add_label(label_text)
        entry = ttk.Entry(self, textvariable=variable, width=32)
        self._place(entry)
        self._add_hint(hint_text)
        return variable

    def add_combobox(self, label_text: str, hint_text: str = "") -> ttk.Combobox:
        self._add_label(label_text)
        # readonly — пользователь может только выбрать значение из списка
        combobox = ttk.Combobox(self, state="readonly", width=30)
        self._place(combobox)
        self._add_hint(hint_text)
        return combobox

    def add_buttons(self, buttons: list[tuple[str, Callable[[], None]]]) -> None:
        """Кнопки располагаются сеткой по две в ряд, первая выделяется цветом."""
        frame = ttk.Frame(self)
        frame.grid(row=self._next_row, column=0, sticky="ew", pady=(12, 0))
        frame.columnconfigure((0, 1), weight=1, uniform="buttons")
        self._next_row += 1
        for index, (text, command) in enumerate(buttons):
            style = "Primary.TButton" if index == 0 else "TButton"
            button = ttk.Button(frame, text=text, command=command, style=style)
            button.grid(row=index // 2, column=index % 2, sticky="ew", padx=2, pady=2)

    def _add_label(self, text: str) -> None:
        label = ttk.Label(self, text=text)
        label.grid(row=self._next_row, column=0, sticky="w", pady=(6, 1))
        self._next_row += 1

    def _add_hint(self, text: str) -> None:
        if not text:
            return
        hint = ttk.Label(self, text=text, style="Hint.TLabel", wraplength=300)
        hint.grid(row=self._next_row, column=0, sticky="w")
        self._next_row += 1

    def _place(self, widget) -> None:
        widget.grid(row=self._next_row, column=0, sticky="ew")
        self._next_row += 1
