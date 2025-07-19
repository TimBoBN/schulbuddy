#!/bin/bash
# Schnelle Datenbank-Bereinigung (ohne Nachfragen)

echo "🚀 Schnelle Datenbank-Bereinigung..."

# Container stoppen
echo "Stoppe Container..."
sudo docker-compose down 2>/dev/null || true

# Backup erstellen
if [ -f "instance/schulbuddy.db" ]; then
    backup_name="auto_backup_$(date +%Y%m%d_%H%M%S).db"
    cp instance/schulbuddy.db "$backup_name"
    echo "✅ Backup erstellt: $backup_name"
fi

# Datenbank löschen
echo "Lösche alte Datenbank..."
rm -f instance/schulbuddy.db*
rm -f instance/*.db

# Verzeichnisse bereinigen und neu erstellen
echo "Bereinige Verzeichnisse..."
rm -rf __pycache__/ 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
rm -f *.log 2>/dev/null || true

mkdir -p instance static/uploads
chmod 755 instance static/uploads

# Container neu starten
echo "Starte Container neu..."
sudo docker-compose up -d

echo "✅ Datenbank bereinigt und Container neu gestartet!"
echo ""
echo "Zugang: http://localhost:5000"
echo "Logs: sudo docker-compose logs -f"
