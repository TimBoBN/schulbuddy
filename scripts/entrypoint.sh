#!/bin/bash
set -e

echo "Starting container as root to handle permissions..."

# Verzeichnisse erstellen
mkdir -p /app/instance
mkdir -p /app/static/uploads

# Debug: Zeige aktuellen Status
echo "Current directory permissions:"
ls -la /app/

echo "Environment variables:"
echo "DOCKER_ENV: $DOCKER_ENV"

# Debug: Teste welche DB-URI verwendet wird
echo "Testing database configuration..."
python3 -c "
import os
import sys
sys.path.insert(0, '/app')
print('DOCKER_ENV value:', repr(os.environ.get('DOCKER_ENV')))
print('DOCKER_ENV truthy test:', bool(os.environ.get('DOCKER_ENV')))
from config import Config
print('Config.SQLALCHEMY_DATABASE_URI:', Config.SQLALCHEMY_DATABASE_URI)
print('Expected for Docker: sqlite:////app/data/schulbuddy.db')
print('Expected for Local: sqlite:///instance/schulbuddy.db')
"

# Erstelle eine Test-SQLite-Datei
echo "Testing SQLite creation in /app/data..."
touch /app/data/test.db
ls -la /app/data/
echo "SQLite file creation test successful"

# Da SQLite schreibrechte braucht, führe die App als root aus
echo "Starting application..."
exec python /app/app.py
