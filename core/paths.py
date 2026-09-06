import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
    DATA_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
LOGS_DIR = DATA_DIR / "logs"
