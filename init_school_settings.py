#!/usr/bin/env python3
"""
Setze Standardwerte für Schuljahr-Einstellungen
"""

from app import app, db
from models import AppSettings

def set_default_school_settings():
    with app.app_context():
        # Setze Standardwerte falls sie noch nicht existieren
        if not AppSettings.get_setting('current_school_year'):
            AppSettings.set_setting('current_school_year', '2025/26', 'Aktuelles Schuljahr')
            print("✅ Schuljahr auf 2025/26 gesetzt")
        
        if not AppSettings.get_setting('current_semester'):
            AppSettings.set_setting('current_semester', '1', 'Aktuelles Halbjahr (1 oder 2)')
            print("✅ Halbjahr auf 1 gesetzt")
        
        print("🎓 Schuljahr-Einstellungen initialisiert!")

if __name__ == "__main__":
    set_default_school_settings()
