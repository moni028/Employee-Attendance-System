import os
from datetime import time

from dotenv import load_dotenv

load_dotenv()


def _database_url():
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/employee_attendance")
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Kolkata")
    OFFICE_START_TIME = time.fromisoformat(os.getenv("OFFICE_START_TIME", "09:30"))
    OFFICE_END_TIME = time.fromisoformat(os.getenv("OFFICE_END_TIME", "18:00"))
    STANDARD_WORKING_HOURS = float(os.getenv("STANDARD_WORKING_HOURS", "8"))
    LATE_THRESHOLD_MINUTES = int(os.getenv("LATE_THRESHOLD_MINUTES", "0"))
    HALF_DAY_THRESHOLD_HOURS = float(os.getenv("HALF_DAY_THRESHOLD_HOURS", "4"))
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
