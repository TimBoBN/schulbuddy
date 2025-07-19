#!/bin/bash
# Ultimate Raspberry Pi Fix Script for SchulBuddy

echo "🍓 Ultimate Raspberry Pi Fix für SchulBuddy"
echo "==========================================="

# Funktion für farbige Ausgabe
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

# Check if we're on Raspberry Pi
if [[ $(uname -m) == "aarch64" ]] || [[ $(uname -m) == "armv7l" ]]; then
    green "✅ Raspberry Pi erkannt: $(uname -m)"
else
    yellow "⚠️  Nicht auf Raspberry Pi, aber versuche es trotzdem..."
fi

# Stop any running containers
blue "🛑 Stoppe alle Container..."
sudo docker-compose down 2>/dev/null || true
sudo docker-compose -f docker-compose.raspberry-pi.yml down 2>/dev/null || true

# Clean up
blue "🧹 Bereinige alte Daten..."
sudo rm -rf instance/schulbuddy.db* 2>/dev/null || true
sudo docker system prune -f 2>/dev/null || true

# Create directories with correct permissions
blue "📁 Erstelle Verzeichnisse..."
mkdir -p instance static/uploads data
sudo chown -R $USER:$USER instance static data
chmod -R 755 instance static data

# Create empty database file
blue "📊 Erstelle leere Datenbank..."
touch instance/schulbuddy.db
chmod 666 instance/schulbuddy.db

# Method 1: Try with Raspberry Pi specific compose
blue "🚀 Methode 1: Raspberry Pi spezifische Konfiguration..."
if sudo docker-compose -f docker-compose.raspberry-pi.yml build --no-cache; then
    green "✅ Build erfolgreich"
    if sudo docker-compose -f docker-compose.raspberry-pi.yml up -d; then
        sleep 10
        if curl -f http://localhost:5000/health 2>/dev/null; then
            green "🎉 ERFOLG! SchulBuddy läuft mit Raspberry Pi Konfiguration!"
            echo ""
            blue "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
            blue "Logs: sudo docker-compose -f docker-compose.raspberry-pi.yml logs -f"
            blue "Stoppen: sudo docker-compose -f docker-compose.raspberry-pi.yml down"
            exit 0
        fi
    fi
fi

red "❌ Methode 1 fehlgeschlagen, versuche Methode 2..."

# Method 2: Override approach
blue "🚀 Methode 2: Standard-Setup mit Override..."
sudo docker-compose down 2>/dev/null || true

# Create override file
cat > docker-compose.override.yml << 'EOF'
version: '3.8'
services:
  schulbuddy:
    user: "1000:1000"
    environment:
      - DATABASE_URL=sqlite:///instance/schulbuddy.db
      - SECRET_KEY=raspberry-pi-test-key-$(date +%s)
    volumes:
      - ./instance:/app/instance:rw
      - ./static/uploads:/app/static/uploads:rw
    command: >
      bash -c "
        echo 'Starting SchulBuddy on Raspberry Pi...';
        mkdir -p /app/instance /app/static/uploads;
        chmod 755 /app/instance /app/static/uploads;
        if [ ! -f /app/instance/schulbuddy.db ]; then
          echo 'Creating database...';
          touch /app/instance/schulbuddy.db;
          chmod 666 /app/instance/schulbuddy.db;
          python3 -c 'from app import create_app; from models import init_db; app = create_app(); app.config[\"SQLALCHEMY_DATABASE_URI\"] = \"sqlite:///instance/schulbuddy.db\"; with app.app_context(): init_db(app); print(\"Database initialized!\")' || echo 'Database init failed, continuing...';
        fi;
        echo 'Starting Flask...';
        python3 -m flask run --host=0.0.0.0 --port=5000
      "
EOF

if sudo docker-compose build --no-cache && sudo docker-compose up -d; then
    sleep 15
    if curl -f http://localhost:5000/health 2>/dev/null; then
        green "🎉 ERFOLG! SchulBuddy läuft mit Override-Konfiguration!"
        echo ""
        blue "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
        blue "Logs: sudo docker-compose logs -f"
        blue "Stoppen: sudo docker-compose down"
        yellow "⚠️ Denke daran: rm docker-compose.override.yml zum Aufräumen"
        exit 0
    fi
fi

red "❌ Methode 2 fehlgeschlagen, versuche Methode 3..."

# Method 3: No Docker approach
blue "🚀 Methode 3: Direkte Python-Installation..."

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    blue "🐍 Python3 gefunden, installiere SchulBuddy direkt..."
    
    # Install pip if needed
    if ! command -v pip3 &> /dev/null; then
        sudo apt update && sudo apt install -y python3-pip
    fi
    
    # Create virtual environment
    python3 -m venv venv 2>/dev/null || sudo apt install -y python3-venv && python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Create config
    if [ ! -f .env ]; then
        cp .env.example .env 2>/dev/null || echo "SECRET_KEY=raspberry-pi-key-$(date +%s)" > .env
    fi
    
    # Initialize database
    python3 -c "from app import create_app; from models import init_db; app = create_app(); with app.app_context(): init_db(app)"
    
    # Start application in background
    nohup python3 app.py > schulbuddy.log 2>&1 &
    echo $! > schulbuddy.pid
    
    sleep 5
    if curl -f http://localhost:5000/health 2>/dev/null; then
        green "🎉 ERFOLG! SchulBuddy läuft als Python-Anwendung!"
        echo ""
        blue "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
        blue "Logs: tail -f schulbuddy.log"
        blue "Stoppen: kill \$(cat schulbuddy.pid)"
        exit 0
    fi
fi

# All methods failed
red "❌ Alle Methoden fehlgeschlagen!"
echo ""
red "🆘 Diagnose-Informationen:"
echo "Raspberry Pi Modell: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unbekannt')"
echo "Architektur: $(uname -m)"
echo "Docker Version: $(docker --version 2>/dev/null || echo 'Nicht installiert')"
echo "Docker Compose: $(docker-compose --version 2>/dev/null || echo 'Nicht installiert')"
echo "Python Version: $(python3 --version 2>/dev/null || echo 'Nicht installiert')"
echo "Speicherplatz: $(df -h . | tail -1)"
echo "Verfügbarer RAM: $(free -h | grep Mem | awk '{print $7}')"

echo ""
blue "📋 Container Logs (falls vorhanden):"
sudo docker-compose logs --tail=10 schulbuddy 2>/dev/null || echo "Keine Container-Logs verfügbar"

echo ""
yellow "💡 Lösungsvorschläge:"
echo "1. Docker neu installieren: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
echo "2. Mehr Speicherplatz schaffen"
echo "3. Raspberry Pi neustarten"
echo "4. Manually run: python3 app.py"
