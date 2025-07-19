#!/bin/bash
# SchulBuddy Raspberry Pi Setup Script

echo "🍓 SchulBuddy Raspberry Pi Setup gestartet..."

# Stoppe alle laufenden Container
echo "Stoppe laufende Container..."
sudo docker-compose down 2>/dev/null || true

# Erstelle notwendige Verzeichnisse
echo "Erstelle notwendige Verzeichnisse..."
mkdir -p instance
mkdir -p static/uploads
mkdir -p data

# Setze Berechtigungen (wichtig für Raspberry Pi)
echo "Setze Berechtigungen..."
sudo chown -R $USER:$USER instance static data
chmod -R 755 instance static data

# Erstelle eine leere Datenbank-Datei falls sie nicht existiert
if [ ! -f "instance/schulbuddy.db" ]; then
    echo "Erstelle Datenbank-Datei..."
    touch instance/schulbuddy.db
    chmod 666 instance/schulbuddy.db
fi

# Mache alle Shell-Skripte ausführbar
echo "Mache Skripte ausführbar..."
find . -name "*.sh" -type f -exec chmod +x {} \;

# Überprüfe Docker Installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ist nicht installiert!"
    echo "Installiere Docker mit: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose ist nicht installiert!"
    echo "Installiere Docker Compose mit: sudo apt update && sudo apt install docker-compose-plugin"
    exit 1
fi

# Baue Container für ARM64 (Raspberry Pi)
echo "Baue Docker Container für Raspberry Pi..."
sudo docker-compose build --no-cache

# Initialisiere Datenbank im Container
echo "Initialisiere Datenbank..."
sudo docker-compose run --rm schulbuddy python3 -c "
from app import create_app
from models import init_db

app = create_app()
with app.app_context():
    init_db(app)
    print('Datenbank erfolgreich initialisiert!')
"

echo "✅ Setup abgeschlossen!"
echo ""
echo "Starte SchulBuddy mit:"
echo "  sudo docker-compose up -d"
echo ""
echo "Öffne im Browser:"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Logs anzeigen:"
echo "  sudo docker-compose logs -f"
