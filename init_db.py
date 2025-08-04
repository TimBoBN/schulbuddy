#!/usr/bin/env python3
"""
Datenbankinitialisierungsskript für SchulBuddy
"""
from app import create_app
from models import Task, Grade, db
import os


def init_database():
    """Initialisiert die Datenbank mit allen Tabellen"""
    app = create_app()
    with app.app_context():
        print(f"Current directory: {os.getcwd()}")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"Instance path: {app.instance_path}")

        # Lösche alle bestehenden Tabellen
        db.drop_all()
        print("Alte Tabellen gelöscht")

        # Erstelle neue Tabellen
        db.create_all()
        print("Neue Tabellen erstellt")

        # Überprüfe, ob die Tabellen existieren
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Vorhandene Tabellen: {tables}")

        # Keine Testdaten mehr einfügen, um eine saubere DB zu haben
        try:
            from datetime import datetime
            print("Datenbank erfolgreich initialisiert.")

        except Exception as e:
            print(f"Fehler beim Hinzufügen der Testdaten: {e}")
            db.session.rollback()


if __name__ == "__main__":
    init_database()
