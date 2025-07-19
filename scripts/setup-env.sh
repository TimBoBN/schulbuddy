#!/bin/bash

# SchulBuddy Docker Setup Script
echo "🚀 SchulBuddy Docker Setup wird gestartet..."

# Prüfe ob .env existiert
if [ -f ".env" ]; then
    echo "⚠️  .env-Datei existiert bereits!"
    read -p "Möchten Sie sie überschreiben? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Setup abgebrochen. Bestehende .env-Datei beibehalten."
        exit 0
    fi
fi

# Erstelle .env von Template
if [ -f ".env.template" ]; then
    echo "📋 Erstelle .env-Datei von .env.template..."
    cp .env.template .env
    echo "✅ .env-Datei erfolgreich erstellt!"
elif [ -f ".env.example" ]; then
    echo "📋 Erstelle .env-Datei von .env.example..."
    cp .env.example .env
    echo "✅ .env-Datei erfolgreich erstellt!"
else
    echo "❌ Keine Vorlage gefunden! .env.template oder .env.example fehlt."
    exit 1
fi

# Frage nach Port-Konfiguration
echo ""
echo "🔧 Port-Konfiguration:"
read -p "Welchen Port möchten Sie verwenden? (Standard: 5000): " port
port=${port:-5000}

# Update .env mit gewähltem Port
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # macOS/Linux
    sed -i.bak "s/PORT=5000/PORT=$port/" .env
    sed -i.bak "s/EXTERNAL_PORT=5000/EXTERNAL_PORT=$port/" .env
    rm .env.bak
else
    # Für andere Systeme (Windows mit Git Bash)
    sed -i "s/PORT=5000/PORT=$port/" .env
    sed -i "s/EXTERNAL_PORT=5000/EXTERNAL_PORT=$port/" .env
fi

echo "✅ Port auf $port gesetzt!"

# Frage nach Secret Key
echo ""
echo "🔐 Sicherheit:"
read -p "Möchten Sie einen neuen SECRET_KEY generieren? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # Generiere neuen Secret Key
    if command -v openssl > /dev/null; then
        new_secret=$(openssl rand -base64 32)
        if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=$new_secret/" .env
            rm .env.bak
        else
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$new_secret/" .env
        fi
        echo "✅ Neuer SECRET_KEY generiert!"
    else
        echo "⚠️  OpenSSL nicht verfügbar. Bitte SECRET_KEY manuell ändern!"
    fi
fi

echo ""
echo "🎯 Setup abgeschlossen!"
echo ""
echo "📋 Nächste Schritte:"
echo "   1. Prüfen Sie die .env-Datei: nano .env"
echo "   2. Starten Sie die Anwendung: docker-compose up -d"
echo "   3. Öffnen Sie: http://localhost:$port"
echo ""
echo "📚 Weitere Hilfe: cat PORT_CONFIG.md"
