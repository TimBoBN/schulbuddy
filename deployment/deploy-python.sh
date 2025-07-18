#!/bin/bash
# Python Deployment Script für SchulBuddy

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Konfiguration
APP_DIR="/opt/schulbuddy"
SERVICE_NAME="schulbuddy"
USER="schulbuddy"
PYTHON_VERSION="3.11"
VENV_DIR="$APP_DIR/venv"
BACKUP_DIR="$APP_DIR/backups"

echo -e "${BLUE}🐍 SchulBuddy Python Deployment${NC}"

# Funktionen
check_requirements() {
    echo -e "${BLUE}📋 Prüfe Systemvoraussetzungen...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 ist nicht installiert${NC}"
        exit 1
    fi
    
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 ist nicht installiert${NC}"
        exit 1
    fi
    
    python_ver=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ "$python_ver" < "3.9" ]]; then
        echo -e "${RED}❌ Python 3.9+ erforderlich, gefunden: $python_ver${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Python verfügbar: $(python3 --version)${NC}"
}

setup_user() {
    echo -e "${BLUE}👤 Richte Benutzer ein...${NC}"
    
    if ! id "$USER" &>/dev/null; then
        sudo useradd -r -s /bin/bash -d "$APP_DIR" "$USER"
        echo -e "${GREEN}✅ Benutzer $USER erstellt${NC}"
    else
        echo -e "${YELLOW}⚠️ Benutzer $USER existiert bereits${NC}"
    fi
}

setup_directories() {
    echo -e "${BLUE}📁 Erstelle Verzeichnisse...${NC}"
    
    sudo mkdir -p "$APP_DIR"
    sudo mkdir -p "$BACKUP_DIR"
    sudo mkdir -p "$APP_DIR/instance"
    sudo mkdir -p "$APP_DIR/static/uploads"
    sudo mkdir -p "/var/log/schulbuddy"
    
    sudo chown -R "$USER:$USER" "$APP_DIR"
    sudo chown -R "$USER:$USER" "/var/log/schulbuddy"
    
    echo -e "${GREEN}✅ Verzeichnisse erstellt${NC}"
}

setup_virtual_environment() {
    echo -e "${BLUE}🔧 Richte Virtual Environment ein...${NC}"
    
    sudo -u "$USER" python3 -m venv "$VENV_DIR"
    sudo -u "$USER" "$VENV_DIR/bin/pip" install --upgrade pip
    
    echo -e "${GREEN}✅ Virtual Environment erstellt${NC}"
}

backup_current() {
    echo -e "${BLUE}💾 Erstelle Backup...${NC}"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    if [[ -f "$APP_DIR/instance/schulbuddy.db" ]]; then
        sudo -u "$USER" cp "$APP_DIR/instance/schulbuddy.db" "$BACKUP_DIR/schulbuddy_${timestamp}.db"
        echo -e "${GREEN}✅ Datenbank-Backup: $BACKUP_DIR/schulbuddy_${timestamp}.db${NC}"
    fi
    
    if [[ -d "$APP_DIR/static/uploads" ]]; then
        sudo -u "$USER" tar -czf "$BACKUP_DIR/uploads_${timestamp}.tar.gz" -C "$APP_DIR" static/uploads/
        echo -e "${GREEN}✅ Uploads-Backup: $BACKUP_DIR/uploads_${timestamp}.tar.gz${NC}"
    fi
}

deploy_application() {
    local package_path=$1
    
    if [[ ! -f "$package_path" ]]; then
        echo -e "${RED}❌ Package nicht gefunden: $package_path${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🚀 Deploye Anwendung...${NC}"
    
    # Stoppe Service falls vorhanden
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    
    # Erstelle Backup
    backup_current
    
    # Extrahiere neue Version
    local temp_dir=$(mktemp -d)
    tar -xzf "$package_path" -C "$temp_dir"
    
    # Kopiere neue Dateien
    sudo -u "$USER" rsync -av --delete \
        --exclude='instance/' \
        --exclude='static/uploads/' \
        --exclude='venv/' \
        "$temp_dir/" "$APP_DIR/"
    
    # Installiere Dependencies
    echo -e "${BLUE}📦 Installiere Dependencies...${NC}"
    if [[ -f "$APP_DIR/requirements-frozen.txt" ]]; then
        sudo -u "$USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements-frozen.txt"
    else
        sudo -u "$USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    fi
    
    # Setup Environment
    if [[ ! -f "$APP_DIR/.env" ]]; then
        if [[ -f "$APP_DIR/.env.example" ]]; then
            sudo -u "$USER" cp "$APP_DIR/.env.example" "$APP_DIR/.env"
            echo -e "${YELLOW}⚠️ .env Datei erstellt. Bitte SECRET_KEY anpassen!${NC}"
        fi
    fi
    
    # Setze Berechtigungen
    sudo chown -R "$USER:$USER" "$APP_DIR"
    sudo chmod +x "$APP_DIR/app.py"
    
    # Cleanup
    rm -rf "$temp_dir"
    
    echo -e "${GREEN}✅ Anwendung deployed${NC}"
}

create_systemd_service() {
    echo -e "${BLUE}⚙️ Erstelle systemd Service...${NC}"
    
    sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=SchulBuddy Flask Application
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=schulbuddy

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    
    echo -e "${GREEN}✅ systemd Service erstellt${NC}"
}

start_service() {
    echo -e "${BLUE}▶️ Starte Service...${NC}"
    
    sudo systemctl start "$SERVICE_NAME"
    
    # Warte auf Start
    sleep 10
    
    for i in {1..12}; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            echo -e "${GREEN}✅ Service erfolgreich gestartet!${NC}"
            echo -e "${GREEN}🌐 SchulBuddy verfügbar unter: http://localhost:5000${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Warte auf Start... ($i/12)${NC}"
        sleep 5
    done
    
    echo -e "${RED}❌ Service-Start fehlgeschlagen${NC}"
    show_status
    exit 1
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    sudo systemctl status "$SERVICE_NAME" --no-pager
    
    echo -e "\n${BLUE}🏥 Health Check:${NC}"
    if curl -f http://localhost:5000/health 2>/dev/null; then
        curl -s http://localhost:5000/health | python3 -m json.tool 2>/dev/null
    else
        echo -e "${RED}❌ Health-Check fehlgeschlagen${NC}"
    fi
}

show_logs() {
    local lines=${1:-50}
    echo -e "${BLUE}📋 Logs (letzte $lines Zeilen):${NC}"
    sudo journalctl -u "$SERVICE_NAME" -n "$lines" --no-pager
}

rollback() {
    echo -e "${BLUE}🔄 Rollback wird durchgeführt...${NC}"
    
    # Zeige verfügbare Backups
    echo -e "${CYAN}Verfügbare Backups:${NC}"
    sudo ls -la "$BACKUP_DIR"/schulbuddy_*.db 2>/dev/null || {
        echo -e "${RED}❌ Keine Backups gefunden${NC}"
        exit 1
    }
    
    # Letztes Backup automatisch wählen
    latest_backup=$(sudo ls -t "$BACKUP_DIR"/schulbuddy_*.db 2>/dev/null | head -1)
    
    if [[ -n $latest_backup ]]; then
        echo -e "${BLUE}📄 Verwende Backup: $latest_backup${NC}"
        
        # Service stoppen
        sudo systemctl stop "$SERVICE_NAME"
        
        # Backup wiederherstellen
        sudo -u "$USER" cp "$latest_backup" "$APP_DIR/instance/schulbuddy.db"
        
        # Service starten
        sudo systemctl start "$SERVICE_NAME"
        
        echo -e "${GREEN}✅ Rollback abgeschlossen${NC}"
    else
        echo -e "${RED}❌ Kein Backup verfügbar${NC}"
        exit 1
    fi
}

install_nginx() {
    echo -e "${BLUE}🔗 Installiere Nginx Reverse Proxy...${NC}"
    
    # Installiere Nginx
    sudo apt update
    sudo apt install -y nginx
    
    # Nginx Konfiguration
    sudo tee "/etc/nginx/sites-available/schulbuddy" > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 16M;

    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF

    # Aktiviere Site
    sudo ln -sf /etc/nginx/sites-available/schulbuddy /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Teste und starte Nginx
    sudo nginx -t
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    echo -e "${GREEN}✅ Nginx konfiguriert${NC}"
}

# Hauptlogik
case "${1:-help}" in
    "check")
        check_requirements
        ;;
    "install")
        check_requirements
        setup_user
        setup_directories
        setup_virtual_environment
        create_systemd_service
        echo -e "${GREEN}✅ Basis-Installation abgeschlossen${NC}"
        echo -e "${YELLOW}Nächster Schritt: $0 deploy <package.tar.gz>${NC}"
        ;;
    "deploy")
        if [[ -z "$2" ]]; then
            echo -e "${RED}❌ Package-Pfad erforderlich${NC}"
            echo -e "${YELLOW}Verwendung: $0 deploy <package.tar.gz>${NC}"
            exit 1
        fi
        deploy_application "$2"
        start_service
        ;;
    "start")
        sudo systemctl start "$SERVICE_NAME"
        echo -e "${GREEN}✅ Service gestartet${NC}"
        ;;
    "stop")
        sudo systemctl stop "$SERVICE_NAME"
        echo -e "${GREEN}✅ Service gestoppt${NC}"
        ;;
    "restart")
        sudo systemctl restart "$SERVICE_NAME"
        echo -e "${GREEN}✅ Service neu gestartet${NC}"
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-50}"
        ;;
    "rollback")
        rollback
        ;;
    "backup")
        backup_current
        ;;
    "nginx")
        install_nginx
        ;;
    *)
        echo -e "${CYAN}SchulBuddy Python Deployment Script${NC}"
        echo ""
        echo -e "${GREEN}Verwendung: $0 <command> [options]${NC}"
        echo ""
        echo -e "${YELLOW}Installation:${NC}"
        echo -e "  check    - Prüfe Systemvoraussetzungen"
        echo -e "  install  - Basis-Installation (Benutzer, Verzeichnisse, Service)"
        echo -e "  nginx    - Installiere Nginx Reverse Proxy"
        echo ""
        echo -e "${YELLOW}Deployment:${NC}"
        echo -e "  deploy   - Deploye Anwendung aus Package"
        echo -e "  rollback - Rollback zum letzten Backup"
        echo -e "  backup   - Erstelle manuelles Backup"
        echo ""
        echo -e "${YELLOW}Service Management:${NC}"
        echo -e "  start    - Starte Service"
        echo -e "  stop     - Stoppe Service"
        echo -e "  restart  - Starte Service neu"
        echo -e "  status   - Zeige Service-Status"
        echo -e "  logs     - Zeige Logs [anzahl_zeilen]"
        echo ""
        echo -e "${YELLOW}Beispiele:${NC}"
        echo -e "  $0 install                              # Basis-Installation"
        echo -e "  $0 deploy schulbuddy-package.tar.gz     # Deploy Package"
        echo -e "  $0 logs 100                             # Zeige 100 Log-Zeilen"
        echo -e "  $0 nginx                                # Installiere Nginx"
        ;;
esac
