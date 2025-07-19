#!/bin/bash
# Ultimatives Container-Startskript für SchulBuddy

set -e

echo "🚀 SchulBuddy startet..."
echo "Benutzer: $(whoami)"
echo "Arbeitsverzeichnis: $(pwd)"
echo "Berechtigungen: $(ls -la /app/)"

# Warten auf Dateisystem
sleep 2

# Stelle sicher, dass alle Verzeichnisse existieren
echo "📁 Erstelle Verzeichnisse..."
mkdir -p /app/instance /app/static/uploads /app/data

# Versuche Berechtigungen zu setzen (ignoriere Fehler)
echo "🔧 Setze Berechtigungen..."
chmod 755 /app/instance /app/static/uploads /app/data 2>/dev/null || true
chmod 666 /app/instance/*.db 2>/dev/null || true

# Database URL aus Environment oder Standard
DB_URL="${DATABASE_URL:-sqlite:///instance/schulbuddy.db}"
DB_FILE="/app/instance/schulbuddy.db"

echo "📊 Datenbank-Setup..."
echo "Database URL: $DB_URL"

# Erstelle leere Datenbankdatei falls sie nicht existiert
if [[ "$DB_URL" == sqlite* ]] && [[ ! -f "$DB_FILE" ]]; then
    echo "Erstelle leere Datenbank-Datei..."
    touch "$DB_FILE" 2>/dev/null || echo "⚠️ Konnte Datenbankdatei nicht erstellen"
    chmod 666 "$DB_FILE" 2>/dev/null || echo "⚠️ Konnte Datenbankberechtigungen nicht setzen"
fi

# Teste ob wir in die Datenbank schreiben können
if [[ "$DB_URL" == sqlite* ]]; then
    if sqlite3 "$DB_FILE" "CREATE TABLE IF NOT EXISTS test_table (id INTEGER);" 2>/dev/null; then
        sqlite3 "$DB_FILE" "DROP TABLE IF EXISTS test_table;" 2>/dev/null
        echo "✅ Datenbankzugriff funktioniert"
    else
        echo "❌ Datenbankzugriff fehlgeschlagen"
        echo "Versuche alternative Datenbankpfade..."
        
        # Versuche alternative Pfade
        for alt_path in "/tmp/schulbuddy.db" "/app/schulbuddy.db" ":memory:"; do
            echo "Teste: $alt_path"
            export DATABASE_URL="sqlite:///$alt_path"
            if [[ "$alt_path" != ":memory:" ]] && sqlite3 "$alt_path" "CREATE TABLE IF NOT EXISTS test_table (id INTEGER);" 2>/dev/null; then
                sqlite3 "$alt_path" "DROP TABLE IF EXISTS test_table;" 2>/dev/null
                echo "✅ Alternative Datenbank funktioniert: $alt_path"
                break
            elif [[ "$alt_path" == ":memory:" ]]; then
                echo "✅ Verwende In-Memory-Datenbank"
                break
            fi
        done
    fi
fi

echo "🌐 Starte Flask-Server..."
echo "Environment: $FLASK_ENV"
echo "Database URL: $DATABASE_URL"

# Starte die Anwendung mit Fehlerbehandlung
if python3 -m flask run --host=0.0.0.0 --port=5000; then
    echo "✅ Flask gestartet"
else
    echo "❌ Flask-Start fehlgeschlagen, versuche direkten Start..."
    exec python3 app.py
fi
