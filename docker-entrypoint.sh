#!/bin/bash
# Container-Startskript für SchulBuddy

set -e

echo "🚀 SchulBuddy startet..."

# Warten auf Dateisystem
sleep 2

# Stelle sicher, dass alle Verzeichnisse existieren
mkdir -p /app/instance
mkdir -p /app/static/uploads
mkdir -p /app/data

# Setze Berechtigungen für den aktuellen User
chmod 755 /app/instance /app/static/uploads /app/data

# Wenn Datenbank nicht existiert, erstelle sie
if [ ! -f "/app/instance/schulbuddy.db" ]; then
    echo "📊 Erstelle neue Datenbank..."
    python3 -c "
from app import create_app
from models import init_db

try:
    app = create_app()
    with app.app_context():
        init_db(app)
    print('✅ Datenbank erfolgreich erstellt!')
except Exception as e:
    print(f'❌ Fehler beim Erstellen der Datenbank: {e}')
    exit(1)
"
fi

echo "🌐 Starte Flask-Server..."

# Starte die Anwendung
exec python3 -m flask run --host=0.0.0.0 --port=5000
