"""Цвета и шрифты приложения по руководству по стилю (docs/style_guide.md)."""
import tkinter as tk
from tkinter import ttk

from app.config import ICON_PATH

COLOR_PRIMARY = "#2E7D32"
COLOR_PRIMARY_DARK = "#1B5E20"
COLOR_ACCENT = "#FFD54F"
COLOR_BACKGROUND = "#F4F7F4"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#212121"
COLOR_TEXT_SECONDARY = "#616161"
COLOR_INCOME = "#2E7D32"
COLOR_EXPENSE = "#C62828"

FONT_FAMILY = "Segoe UI"
FONT_NORMAL = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_HINT = (FONT_FAMILY, 8, "italic")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_AMOUNT = (FONT_FAMILY, 18, "bold")


def apply_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=FONT_NORMAL, background=COLOR_BACKGROUND, foreground=COLOR_TEXT)
    style.configure("TFrame", background=COLOR_BACKGROUND)
    style.configure("Card.TFrame", background=COLOR_SURFACE, relief="solid", borderwidth=1)
    style.configure("TLabel", background=COLOR_BACKGROUND, foreground=COLOR_TEXT)
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLOR_PRIMARY_DARK)
    style.configure("Subtitle.TLabel", font=FONT_SUBTITLE, foreground=COLOR_TEXT)
    style.configure("Hint.TLabel", font=FONT_HINT, foreground=COLOR_TEXT_SECONDARY)
    style.configure("CardCaption.TLabel", background=COLOR_SURFACE, foreground=COLOR_TEXT_SECONDARY)
    style.configure("Income.TLabel", background=COLOR_SURFACE, foreground=COLOR_INCOME, font=FONT_AMOUNT)
    style.configure("Expense.TLabel", background=COLOR_SURFACE, foreground=COLOR_EXPENSE, font=FONT_AMOUNT)
    style.configure("Balance.TLabel", background=COLOR_SURFACE, foreground=COLOR_TEXT, font=FONT_AMOUNT)
    style.configure("TLabelframe", background=COLOR_BACKGROUND)
    style.configure("TLabelframe.Label", font=FONT_BOLD, foreground=COLOR_PRIMARY_DARK, background=COLOR_BACKGROUND)
    style.configure("TButton", padding=(10, 5))
    style.configure("Primary.TButton", background=COLOR_PRIMARY, foreground=COLOR_SURFACE, font=FONT_BOLD)
    style.map("Primary.TButton", background=[("active", COLOR_PRIMARY_DARK)])
    style.configure("Treeview", rowheight=26, background=COLOR_SURFACE, fieldbackground=COLOR_SURFACE)
    style.configure("Treeview.Heading", font=FONT_BOLD, background=COLOR_PRIMARY, foreground=COLOR_SURFACE)
    style.map("Treeview.Heading", background=[("active", COLOR_PRIMARY_DARK)])
    style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", COLOR_TEXT)])


def set_application_icon(root: tk.Tk) -> None:
    # Если файл иконки удалён, программа продолжит работу со стандартной иконкой
    if not ICON_PATH.exists():
        return
    icon = tk.PhotoImage(file=str(ICON_PATH))
    root.iconphoto(True, icon)
    root.application_icon = icon
