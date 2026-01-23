# app/config.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../mysite/app -> .../mysite
INSTANCE_DIR = BASE_DIR / "instance"

# Make sure instance dir exists (harmless if it already exists)
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    # SQLite database file: instance/hrs.db
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'hrs.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key (can still come from env if you want)
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # You can keep these for later if you ever go back to MySQL
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

