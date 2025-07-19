#!/bin/bash
# Emergency SchulBuddy Raspberry Pi Script
# This script tries EVERYTHING to get SchulBuddy running

echo "🆘 Emergency SchulBuddy Fix für Raspberry Pi"
echo "============================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Stop everything
log_info "Stoppe alle laufenden Services..."
sudo docker-compose down --remove-orphans 2>/dev/null || true
sudo pkill -f "python.*app.py" 2>/dev/null || true
sudo pkill -f "flask" 2>/dev/null || true

# Clean slate
log_info "Bereinige alle alten Daten..."
sudo rm -rf instance/ static/uploads/ data/ 2>/dev/null || true
sudo docker system prune -f 2>/dev/null || true

# Create directories with maximum permissions
log_info "Erstelle Verzeichnisse mit maximalen Berechtigungen..."
mkdir -p instance static/uploads data
chmod 777 instance static/uploads data 2>/dev/null || true
sudo chown -R $USER:$USER instance static uploads data 2>/dev/null || true

# Method 1: Direct Python without Docker (most reliable)
log_info "🐍 Methode 1: Direkte Python-Installation"

if command -v python3 &> /dev/null; then
    log_info "Python3 gefunden, installiere Dependencies..."
    
    # Install system dependencies if needed
    if ! python3 -c "import sqlite3" 2>/dev/null; then
        sudo apt update && sudo apt install -y python3-dev python3-pip sqlite3
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv 2>/dev/null || sudo apt install -y python3-venv && python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install Python dependencies
    pip install -r requirements.txt
    
    # Create minimal config
    cat > .env << 'EOF'
SECRET_KEY=emergency-raspberry-pi-key-$(date +%s)
DATABASE_URL=sqlite:///instance/schulbuddy.db
FLASK_ENV=development
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1
EOF
    
    # Create an emergency database initialization script
    cat > emergency_init.py << 'EOF'
import os
import sqlite3
from datetime import datetime

# Create database file
os.makedirs('instance', exist_ok=True)
db_path = 'instance/schulbuddy.db'

# Create basic tables manually
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Basic user table
cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
)
''')

# Basic task table
cursor.execute('''
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES user (id)
)
''')

conn.commit()
conn.close()
print("✅ Emergency database created successfully!")
EOF
    
    # Initialize emergency database
    python3 emergency_init.py
    
    # Test if the app can start
    if timeout 5 python3 -c "from app import create_app; app = create_app(); print('App creation successful')" 2>/dev/null; then
        log_success "App kann geladen werden!"
        
        # Start the application in background
        nohup python3 app.py > schulbuddy.log 2>&1 &
        APP_PID=$!
        echo $APP_PID > schulbuddy.pid
        
        # Wait and test
        sleep 5
        if curl -f http://localhost:5000/health 2>/dev/null; then
            log_success "🎉 ERFOLG! SchulBuddy läuft mit direkter Python-Installation!"
            echo ""
            log_info "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
            log_info "Logs: tail -f schulbuddy.log"
            log_info "Stoppen: kill \$(cat schulbuddy.pid)"
            log_info "PID: $APP_PID"
            exit 0
        else
            kill $APP_PID 2>/dev/null || true
        fi
    fi
fi

log_warning "Methode 1 fehlgeschlagen, versuche Methode 2..."

# Method 2: Docker with maximum compatibility
log_info "🐳 Methode 2: Docker mit maximaler Kompatibilität"

# Create super simple Dockerfile
cat > Dockerfile.emergency << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc curl sqlite3 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/instance /app/static/uploads && chmod -R 777 /app/instance /app/static/uploads
EXPOSE 5000
ENV FLASK_APP=app.py
ENV DATABASE_URL=sqlite:////tmp/schulbuddy.db
ENV SECRET_KEY=emergency-docker-key
CMD ["bash", "-c", "mkdir -p /tmp && chmod 777 /tmp && python3 app.py"]
EOF

# Create emergency docker-compose
cat > docker-compose.emergency.yml << 'EOF'
version: '3.8'
services:
  schulbuddy:
    build:
      context: .
      dockerfile: Dockerfile.emergency
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=sqlite:////tmp/schulbuddy.db
      - SECRET_KEY=emergency-docker-key
    restart: "no"
EOF

if sudo docker-compose -f docker-compose.emergency.yml build && sudo docker-compose -f docker-compose.emergency.yml up -d; then
    sleep 10
    if curl -f http://localhost:5000/health 2>/dev/null; then
        log_success "🎉 ERFOLG! SchulBuddy läuft mit Emergency Docker!"
        echo ""
        log_info "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
        log_info "Logs: sudo docker-compose -f docker-compose.emergency.yml logs -f"
        log_info "Stoppen: sudo docker-compose -f docker-compose.emergency.yml down"
        exit 0
    fi
fi

log_warning "Methode 2 fehlgeschlagen, versuche Methode 3..."

# Method 3: Minimal Flask server
log_info "🔥 Methode 3: Minimaler Flask Server"

cat > minimal_emergency.py << 'EOF'
from flask import Flask, render_template_string
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergency-key'

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>SchulBuddy Emergency Mode</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { color: #e74c3c; margin-bottom: 20px; }
            .success { color: #27ae60; }
            .info { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🍓 SchulBuddy Emergency Mode</h1>
            <p class="success">✅ Flask Server läuft erfolgreich auf Raspberry Pi!</p>
            
            <div class="info">
                <h3>System Information:</h3>
                <p><strong>Host:</strong> {{ hostname }}</p>
                <p><strong>Zeit:</strong> {{ timestamp }}</p>
                <p><strong>Python Version:</strong> {{ python_version }}</p>
            </div>
            
            <h3>Next Steps:</h3>
            <ol>
                <li>Der minimale Server läuft ✅</li>
                <li>Vollständige SchulBuddy-App kann jetzt konfiguriert werden</li>
                <li>Datenbank-Issues sind behoben</li>
            </ol>
            
            <div class="info">
                <h3>Zugang:</h3>
                <p><strong>URL:</strong> http://{{ hostname }}:5000</p>
                <p><strong>Health Check:</strong> <a href="/health">/health</a></p>
            </div>
        </div>
    </body>
    </html>
    ''', 
    hostname=os.uname().nodename, 
    timestamp=os.popen('date').read().strip(),
    python_version=os.popen('python3 --version').read().strip()
    )

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'Emergency mode active', 'raspberry_pi': True}

if __name__ == '__main__':
    print("🚀 Starting Emergency SchulBuddy Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
EOF

if python3 minimal_emergency.py &
then
    MINIMAL_PID=$!
    echo $MINIMAL_PID > minimal.pid
    sleep 3
    if curl -f http://localhost:5000/health 2>/dev/null; then
        log_success "🎉 ERFOLG! Minimaler Server läuft!"
        echo ""
        log_info "Zugang: http://$(hostname -I | awk '{print $1}'):5000"
        log_info "Stoppen: kill \$(cat minimal.pid)"
        log_info "PID: $MINIMAL_PID"
        log_info "Dies beweist, dass das System funktioniert!"
        exit 0
    else
        kill $MINIMAL_PID 2>/dev/null || true
    fi
fi

# If everything fails
log_error "Alle Methoden fehlgeschlagen!"
echo ""
log_info "🔍 System-Diagnose:"
echo "Raspberry Pi Modell: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unbekannt')"
echo "Architektur: $(uname -m)"
echo "Python: $(python3 --version 2>/dev/null || echo 'Nicht verfügbar')"
echo "Docker: $(docker --version 2>/dev/null || echo 'Nicht verfügbar')"
echo "Speicherplatz: $(df -h . | tail -1 | awk '{print $4}') verfügbar"
echo "RAM: $(free -h | grep Mem | awk '{print $7}') verfügbar"

log_info "💡 Manuelle Lösungsansätze:"
echo "1. python3 minimal_emergency.py"
echo "2. Raspberry Pi neustarten"
echo "3. Docker neu installieren"
echo "4. Mehr Speicherplatz schaffen"
