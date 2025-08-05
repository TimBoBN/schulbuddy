#!/bin/bash
set -e

echo "Starting SchulBuddy container..."

# Verzeichnisse erstellen
mkdir -p /app/data
mkdir -p /app/static/uploads

# Berechtigungen für appuser setzen (läuft als root)
chown -R appuser:appuser /app/data /app/static/uploads
chmod -R 755 /app/data /app/static/uploads

echo "✅ Set correct permissions for appuser"

# Debug: Zeige aktuellen Status
echo "Directory permissions:"
ls -la /app/ | grep -E "(data|static)"

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

# Datenbank initialisieren falls nötig (als appuser)
if [ ! -f "/app/data/schulbuddy.db" ]; then
    echo "📋 Initializing database as appuser..."
    su appuser -c "cd /app && python /app/init_db.py"
fi

# Erstelle eine Test-SQLite-Datei um Berechtigungen zu prüfen (als appuser)
echo "Testing SQLite creation in /app/data as appuser..."
su appuser -c "touch /app/data/test.db"
ls -la /app/data/
echo "SQLite file creation test successful"

# Erkenne Architektur und setze entsprechende Gunicorn-Konfiguration
ARCH=$(uname -m)
if [[ "$ARCH" == "arm"* || "$ARCH" == "aarch"* ]]; then
    echo "🎓 Starting SchulBuddy with Gunicorn on ARM architecture (port ${PORT:-5000})..."
    export GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}  # ARM: weniger Worker für bessere Stabilität
else
    echo "🎓 Starting SchulBuddy with Gunicorn on AMD64 architecture (port ${PORT:-5000})..."
    export GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}  # AMD64: mehr Worker für bessere Performance
fi

echo "Using $GUNICORN_WORKERS Gunicorn workers for $ARCH architecture"

# Starte mit Gunicorn als appuser
echo "Starting application as appuser..."
exec su appuser -c "cd /app && gunicorn --config gunicorn.conf.py wsgi:application"
