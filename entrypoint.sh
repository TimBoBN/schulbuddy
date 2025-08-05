#!/bin/bash
set -e

echo "Starting SchulBuddy container..."

# Verzeichnisse erstellen
mkdir -p /app/data
mkdir -p /app/static/uploads

# Debug: Zeige aktuellen Status
echo "Current directory permissions:"
ls -la /app/

echo "Environment variables:"
echo "DOCKER_ENV: $DOCKER_ENV"
echo "DATABASE_URL: $DATABASE_URL"
echo "PORT: $PORT"

# Debug: Teste welche DB-URI verwendet wird
echo "Testing database configuration..."
python3 -c "
import os
import sys
sys.path.insert(0, '/app')
print('DOCKER_ENV value:', repr(os.environ.get('DOCKER_ENV')))
print('DOCKER_ENV truthy test:', bool(os.environ.get('DOCKER_ENV')))
try:
    from config import Config
    print('Config.SQLALCHEMY_DATABASE_URI:', Config.SQLALCHEMY_DATABASE_URI)
    print('Expected for Docker: sqlite:////app/data/schulbuddy.db')
except Exception as e:
    print('Config import error:', str(e))
"

# Datenbank initialisieren falls nötig
if [ ! -f "/app/data/schulbuddy.db" ]; then
    echo "📋 Initializing database..."
    python /app/init_db.py
fi

# Erstelle eine Test-SQLite-Datei um Berechtigungen zu prüfen
echo "Testing SQLite creation in /app/data..."
touch /app/data/test.db
ls -la /app/data/
echo "SQLite file creation test successful"

echo "🎓 Starting SchulBuddy application..."
exec python /app/app.py
