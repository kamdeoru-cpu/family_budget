"""Общая основа для всех окон разделов: заголовок, кнопка «Назад», размеры."""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from app.config import APP_NAME
from app.ui.styles import COLOR_BACKGROUND


class BaseWindow(tk.Toplevel):
    MIN_WIDTH = 960
    MIN_HEIGHT = 600

    def __init__(self, parent: tk.Tk, title: str, on_close: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.parent_window = parent
        self.on_close = on_close
        self.title(f"{title} — {APP_NAME}")
        self.configure(background=COLOR_BACKGROUND)
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.geometry(f"{self.MIN_WIDTH + 100}x{self.MIN_HEIGHT + 60}")
        # Закрытие окна крестиком работает так же, как кнопка «Назад»
        self.protocol("WM_DELETE_WINDOW", self.go_back)
        self.bind("<Escape>", lambda event: self.go_back())
        parent.withdraw()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Label(self, text=title, style="Title.TLabel", padding=(15, 10))
        header.grid(row=0, column=0, sticky="w")
        self.content = ttk.Frame(self, padding=(15, 0, 15, 5))
        self.content.grid(row=1, column=0, sticky="nsew")

    def add_footer(self) -> None:
        """Вызывается последним, чтобы кнопка «Назад» была последней при переходе по Tab."""
        footer = ttk.Frame(self, padding=(15, 5, 15, 12))
        footer.grid(row=2, column=0, sticky="ew")
        back_button = ttk.Button(footer, text="← Назад в главное меню", command=self.go_back)
        back_button.pack(side="left")
        hint = ttk.Label(footer, text="Esc — вернуться назад", style="Hint.TLabel")
        hint.pack(side="right")

    def go_back(self) -> None:
        self.destroy()
        self.parent_window.deiconify()
        if self.on_close:
            self.on_close()
