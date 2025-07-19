#!/bin/bash
# Einfaches Start-Skript für SchulBuddy auf Raspberry Pi

echo "🍓 Starte SchulBuddy auf Raspberry Pi..."

# Überprüfe ob wir im richtigen Verzeichnis sind
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml nicht gefunden!"
    echo "Bitte ins SchulBuddy-Verzeichnis wechseln."
    exit 1
fi

# Erstelle Verzeichnisse falls sie nicht existieren
mkdir -p instance static/uploads data

# Stoppe eventuell laufende Container
echo "Stoppe alte Container..."
sudo docker-compose down

# Starte Container
echo "Starte SchulBuddy..."
sudo docker-compose up -d

# Warte einen Moment
sleep 5

# Zeige Status
echo ""
echo "📊 Container Status:"
sudo docker-compose ps

echo ""
echo "🌐 SchulBuddy sollte jetzt verfügbar sein unter:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📋 Logs anzeigen: sudo docker-compose logs -f"
echo "🛑 Stoppen: sudo docker-compose down"
