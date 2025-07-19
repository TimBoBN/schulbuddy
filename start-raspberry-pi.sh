#!/bin/bash
# Einfaches Start-Skript für SchulBuddy auf Raspberry Pi

echo "🍓 Starte SchulBuddy auf Raspberry Pi..."

# Überprüfe ob wir im richtigen Verzeichnis sind
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml nicht gefunden!"
    echo "Bitte ins SchulBuddy-Verzeichnis wechseln."
    exit 1
fi

# Prüfe .env Datei
if [ ! -f ".env" ]; then
    echo "⚠️  .env Datei nicht gefunden, erstelle eine..."
    cp .env.example .env 2>/dev/null || echo "Keine .env.example gefunden"
fi

# Lade Port aus .env (falls gesetzt)
if [ -f ".env" ]; then
    CONFIGURED_PORT=$(grep "^PORT=" .env | cut -d= -f2)
    if [ -n "$CONFIGURED_PORT" ]; then
        echo "📡 Verwende konfigurierten Port: $CONFIGURED_PORT"
        DISPLAY_PORT=$CONFIGURED_PORT
    else
        echo "📡 Verwende Standard-Port: 5000"
        DISPLAY_PORT=5000
    fi
else
    DISPLAY_PORT=5000
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
echo "   http://$(hostname -I | awk '{print $1}'):$DISPLAY_PORT"
echo ""
echo "📋 Logs anzeigen: sudo docker-compose logs -f"
echo "🛑 Stoppen: sudo docker-compose down"
