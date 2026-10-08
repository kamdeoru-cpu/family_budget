"""Общие настройки приложения: пути к файлам и ограничения на данные."""
import sys
from pathlib import Path

# Все пути строятся относительно папки программы, а не текущей папки
# пользователя. Поэтому приложение работает, даже если его папку
# перенести в другое место или запустить собранный .exe-файл.
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    RESOURCES_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR)) / "resources"
else:
    APP_DIR = Path(__file__).resolve().parent.parent
    RESOURCES_DIR = APP_DIR / "resources"

DATA_DIR = APP_DIR / "data"
DATABASE_PATH = DATA_DIR / "family_budget.db"
LOG_PATH = DATA_DIR / "errors.log"
LOGO_PATH = RESOURCES_DIR / "logo.png"
ICON_PATH = RESOURCES_DIR / "icon.png"

APP_NAME = "Семейный бюджет"
DATE_FORMAT = "%d.%m.%Y"

MIN_YEAR = 2000
MAX_AMOUNT = 10_000_000
MAX_COMMENT_LENGTH = 200
