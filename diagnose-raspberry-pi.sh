#!/bin/bash
# SchulBuddy Raspberry Pi Troubleshooting Script

echo "🔍 SchulBuddy Diagnose gestartet..."
echo "=================================="

# System-Info
echo "🍓 Raspberry Pi Info:"
echo "Modell: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unbekannt')"
echo "Architektur: $(uname -m)"
echo "Kernel: $(uname -r)"
echo ""

# Docker-Status
echo "🐳 Docker Status:"
if command -v docker &> /dev/null; then
    echo "✅ Docker installiert: $(docker --version)"
    echo "Docker läuft: $(sudo systemctl is-active docker)"
else
    echo "❌ Docker nicht installiert"
fi

if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose installiert: $(docker-compose --version)"
else
    echo "❌ Docker Compose nicht installiert"
fi
echo ""

# Verzeichnis-Status
echo "📁 Verzeichnis Status:"
echo "Aktuelles Verzeichnis: $(pwd)"
echo "Dateien im Verzeichnis:"
ls -la

echo ""
echo "📊 SchulBuddy Verzeichnisse:"
for dir in instance static/uploads data; do
    if [ -d "$dir" ]; then
        echo "✅ $dir existiert ($(ls -ld $dir | awk '{print $1, $3, $4}'))"
    else
        echo "❌ $dir fehlt"
    fi
done

echo ""
if [ -f "instance/schulbuddy.db" ]; then
    echo "✅ Datenbank existiert ($(ls -lh instance/schulbuddy.db | awk '{print $5, $6, $7, $8}'))"
else
    echo "❌ Datenbank fehlt"
fi

echo ""
echo "🐳 Docker Container Status:"
sudo docker-compose ps 2>/dev/null || echo "Keine Container gefunden"

echo ""
echo "📋 Neueste Docker Logs:"
sudo docker-compose logs --tail=20 schulbuddy 2>/dev/null || echo "Keine Logs verfügbar"

echo ""
echo "💾 Speicherplatz:"
df -h .

echo ""
echo "🔧 Lösungsvorschläge:"
echo "1. Setup ausführen: ./setup-raspberry-pi.sh"
echo "2. Container neu bauen: sudo docker-compose build --no-cache"
echo "3. Container starten: sudo docker-compose up -d"
echo "4. Logs verfolgen: sudo docker-compose logs -f"
