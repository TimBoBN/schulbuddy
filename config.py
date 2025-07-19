import os
from datetime import timedelta


class Config:
    """Konfiguration für SchulBuddy"""

    # Pfade
    DATA_PATH = "data"
    UPLOAD_FOLDER = "static/uploads"

    # Flask Settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "schulbuddy-secret-key"
    DEBUG = True

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///instance/schulbuddy.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session-Konfiguration
    SESSION_TIMEOUT_MINUTES = int(
        os.environ.get("SESSION_TIMEOUT_MINUTES", "120")
    )  # 2 Stunden Standard
    SESSION_COOKIE_SECURE = (
        os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

    # Login-Konfiguration
    REMEMBER_COOKIE_DURATION = timedelta(
        days=int(os.environ.get("REMEMBER_COOKIE_DAYS", "30"))
    )
    LOGIN_TIMEOUT_MINUTES = int(
        os.environ.get("LOGIN_TIMEOUT_MINUTES", "60")
    )  # 1 Stunde Standard
    MAX_LOGIN_ATTEMPTS = int(os.environ.get("MAX_LOGIN_ATTEMPTS", "5"))
    LOGIN_ATTEMPT_TIMEOUT_MINUTES = int(
        os.environ.get("LOGIN_ATTEMPT_TIMEOUT_MINUTES", "15")
    )  # 15 Minuten Sperre

    # 2FA-Konfiguration
    TWO_FACTOR_TIMEOUT_MINUTES = int(
        os.environ.get("TWO_FACTOR_TIMEOUT_MINUTES", "5")
    )  # 5 Minuten für 2FA

    # Schuljahr und Halbjahr
    CURRENT_SCHOOL_YEAR = os.environ.get("CURRENT_SCHOOL_YEAR", "2024/25")
    CURRENT_SEMESTER = int(os.environ.get("CURRENT_SEMESTER", "1"))

    # Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "doc", "docx"}

    # Fächer und Farben
    SUBJECTS = {
        "Mathematik": "#ff6b6b",
        "Deutsch": "#4ecdc4",
        "Englisch": "#45b7d1",
        "Französisch": "#f9ca24",
        "Spanisch": "#f0932b",
        "Latein": "#eb4d4b",
        "Geschichte": "#6c5ce7",
        "Erdkunde": "#a29bfe",
        "Politik": "#fd79a8",
        "Wirtschaft": "#fdcb6e",
        "Biologie": "#00b894",
        "Chemie": "#00cec9",
        "Physik": "#74b9ff",
        "Informatik": "#2d3436",
        "Kunst": "#e17055",
        "Musik": "#81ecec",
        "Sport": "#55a3ff",
        "Religion": "#ffeaa7",
        "Ethik": "#dda0dd",
        "Philosophie": "#636e72",
    }

    @staticmethod
    def init_app(app):
        """Initialisiere die Flask App mit dieser Konfiguration"""
        # Erstelle notwendige Verzeichnisse
        os.makedirs(Config.DATA_PATH, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
