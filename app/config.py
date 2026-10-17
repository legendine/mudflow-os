import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

REPORTS_DIR = DATA_DIR / "reports_pdf"
REPORTS_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "mudflow.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

APP_TITLE = "MudFlow OS - Drilling Mud Engineering & Hydraulics Suite"
APP_VERSION = "2.5.0-PROD"
