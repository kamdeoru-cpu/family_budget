"""Окна сообщений с правильными заголовками и значками."""
from tkinter import messagebox


def show_error(parent, text: str, title: str = "Ошибка ввода") -> None:
    messagebox.showerror(title, text, parent=parent)


def show_warning(parent, text: str) -> None:
    messagebox.showwarning("Предупреждение", text, parent=parent)


def show_info(parent, text: str) -> None:
    messagebox.showinfo("Информация", text, parent=parent)


def ask_confirmation(parent, text: str) -> bool:
    return messagebox.askyesno("Подтверждение", text, icon="warning", parent=parent)
