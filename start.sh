#!/bin/bash
# SchulBuddy Docker Start Script für Linux/Unix

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktionen
show_help() {
    echo -e "${CYAN}SchulBuddy Docker Commands:${NC}"
    echo ""
    echo -e "  ${GREEN}setup${NC}     - Erstelle .env Datei aus Vorlage"
    echo -e "  ${GREEN}build${NC}     - Docker Images bauen"
    echo -e "  ${GREEN}up${NC}        - Starte SchulBuddy (Produktion)"
    echo -e "  ${GREEN}down${NC}      - Stoppe alle Container"
    echo -e "  ${GREEN}dev${NC}       - Starte Development-Umgebung"
    echo -e "  ${GREEN}nginx${NC}     - Starte mit Nginx Reverse Proxy"
    echo -e "  ${GREEN}prod${NC}      - Starte Produktions-Umgebung"
    echo -e "  ${GREEN}logs${NC}      - Zeige Logs"
    echo -e "  ${GREEN}logs-app${NC}  - Zeige nur App-Logs"
    echo -e "  ${GREEN}shell${NC}     - Öffne Shell im Container"
    echo -e "  ${GREEN}health${NC}    - Prüfe Anwendungsstatus"
    echo -e "  ${GREEN}status${NC}    - Zeige Container-Status"
    echo -e "  ${GREEN}restart${NC}   - Starte Container neu"
    echo -e "  ${GREEN}update${NC}    - Update der Anwendung"
    echo -e "  ${GREEN}backup${NC}    - Erstelle Backup"
    echo -e "  ${GREEN}restore${NC}   - Stelle Backup wieder her"
    echo -e "  ${GREEN}clean${NC}     - Entferne Container und Images"
    echo -e "  ${GREEN}reset-db${NC}  - Setze Datenbank zurück (VORSICHT!)"
    echo ""
    echo -e "${YELLOW}Verwendung: ./start.sh <command>${NC}"
    echo ""
    echo -e "${YELLOW}Beispiele:${NC}"
    echo -e "  ./start.sh setup     # Erstelle .env Datei"
    echo -e "  ./start.sh dev       # Starte Development"
    echo -e "  ./start.sh up        # Starte Produktion"
    echo -e "  ./start.sh nginx     # Starte mit Nginx"
    echo -e "  ./start.sh backup    # Erstelle Backup"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose ist nicht installiert${NC}"
        exit 1
    fi
}

setup() {
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env Datei erstellt. Bitte anpassen!${NC}"
        echo -e "${YELLOW}⚠️  Vergiss nicht, den SECRET_KEY zu ändern!${NC}"
        echo ""
        echo -e "${CYAN}Wichtige Umgebungsvariablen:${NC}"
        echo -e "  SECRET_KEY - Sicherer Schlüssel (unbedingt ändern!)"
        echo -e "  CURRENT_SCHOOL_YEAR - Aktuelles Schuljahr"
        echo -e "  CURRENT_SEMESTER - Aktuelles Semester"
    else
        echo -e "${YELLOW}⚠️  .env Datei existiert bereits${NC}"
    fi
}

build() {
    echo -e "${BLUE}🔨 Baue Docker Images...${NC}"
    docker-compose build
    echo -e "${GREEN}✅ Images erfolgreich gebaut${NC}"
}

up() {
    echo -e "${BLUE}🚀 Starte SchulBuddy...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ SchulBuddy gestartet: http://localhost:5000${NC}"
}

down() {
    echo -e "${BLUE}🛑 Stoppe Container...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Container gestoppt${NC}"
}

dev() {
    echo -e "${BLUE}🔧 Starte Development-Umgebung...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
}

nginx() {
    echo -e "${BLUE}🔗 Starte mit Nginx Reverse Proxy...${NC}"
    docker-compose --profile with-nginx up -d
    echo -e "${GREEN}✅ SchulBuddy mit Nginx gestartet: http://localhost${NC}"
}

prod() {
    echo -e "${BLUE}🏭 Starte Produktions-Umgebung...${NC}"
    docker-compose -f docker-compose.prod.yml --profile production up -d
    echo -e "${GREEN}✅ Produktions-Umgebung gestartet${NC}"
}

logs() {
    echo -e "${BLUE}📋 Zeige Logs...${NC}"
    docker-compose logs -f
}

logs_app() {
    echo -e "${BLUE}📋 Zeige App-Logs...${NC}"
    docker-compose logs -f schulbuddy
}

shell() {
    echo -e "${BLUE}🐚 Öffne Shell im Container...${NC}"
    docker-compose exec schulbuddy bash
}

health() {
    echo -e "${BLUE}🏥 Prüfe Anwendungsstatus...${NC}"
    if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
        response=$(curl -s http://localhost:5000/health)
        echo -e "${GREEN}✅ Health-Check erfolgreich:${NC}"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo -e "${RED}❌ Health-Check fehlgeschlagen${NC}"
        echo -e "${YELLOW}Ist die Anwendung gestartet? Versuche: ./start.sh status${NC}"
    fi
}

status() {
    echo -e "${BLUE}📊 Container-Status:${NC}"
    docker-compose ps
}

restart() {
    echo -e "${BLUE}🔄 Starte Container neu...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Container neu gestartet${NC}"
}

update() {
    echo -e "${BLUE}🔄 Update der Anwendung...${NC}"
    
    # Backup vor Update
    echo -e "${YELLOW}📦 Erstelle Backup vor Update...${NC}"
    backup
    
    # Git pull
    echo -e "${BLUE}📥 Lade neueste Version...${NC}"
    git pull
    
    # Container stoppen
    echo -e "${BLUE}🛑 Stoppe Container...${NC}"
    docker-compose down
    
    # Images neu bauen
    echo -e "${BLUE}🔨 Baue neue Images...${NC}"
    docker-compose build --no-cache
    
    # Container starten
    echo -e "${BLUE}🚀 Starte Container...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✅ Update abgeschlossen${NC}"
}

backup() {
    echo -e "${BLUE}📦 Erstelle Backup...${NC}"
    
    # Backup-Ordner erstellen
    mkdir -p backups
    
    # Zeitstempel
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Prüfe ob Container läuft
    if docker-compose ps | grep -q "Up"; then
        # Datenbank-Backup
        echo -e "${BLUE}💾 Sichere Datenbank...${NC}"
        docker-compose exec schulbuddy cp /app/instance/schulbuddy.db "/app/instance/backup_${timestamp}.db"
        container_id=$(docker-compose ps -q schulbuddy)
        docker cp "${container_id}:/app/instance/backup_${timestamp}.db" "./backups/"
        
        # Uploads-Backup
        echo -e "${BLUE}📁 Sichere Uploads...${NC}"
        tar -czf "backups/uploads_${timestamp}.tar.gz" static/uploads/
        
        echo -e "${GREEN}✅ Backup erstellt:${NC}"
        echo -e "  📄 Datenbank: backups/backup_${timestamp}.db"
        echo -e "  📁 Uploads: backups/uploads_${timestamp}.tar.gz"
    else
        echo -e "${RED}❌ Container läuft nicht. Starte zuerst die Anwendung.${NC}"
        exit 1
    fi
}

restore() {
    echo -e "${BLUE}🔄 Stelle Backup wieder her...${NC}"
    
    # Verfügbare Backups anzeigen
    echo -e "${CYAN}Verfügbare Backups:${NC}"
    ls -la backups/backup_*.db 2>/dev/null || {
        echo -e "${RED}❌ Keine Backups gefunden${NC}"
        exit 1
    }
    
    echo ""
    read -p "Backup-Datei eingeben (z.B. backup_20240719_143000.db): " backup_file
    
    if [[ ! -f "backups/${backup_file}" ]]; then
        echo -e "${RED}❌ Backup-Datei nicht gefunden${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}⚠️  WARNUNG: Alle aktuellen Daten gehen verloren!${NC}"
    read -p "Fortfahren? (y/N): " confirm
    
    if [[ $confirm != "y" && $confirm != "Y" ]]; then
        echo -e "${YELLOW}Abgebrochen${NC}"
        exit 0
    fi
    
    # Container stoppen
    docker-compose down
    
    # Backup wiederherstellen
    cp "backups/${backup_file}" instance/schulbuddy.db
    
    # Container starten
    docker-compose up -d
    
    echo -e "${GREEN}✅ Backup wiederhergestellt${NC}"
}

clean() {
    echo -e "${BLUE}🧹 Entferne Container und Images...${NC}"
    docker-compose down -v
    docker system prune -f
    echo -e "${GREEN}✅ Bereinigung abgeschlossen${NC}"
}

reset_db() {
    echo -e "${RED}⚠️  WARNUNG: Alle Daten gehen verloren!${NC}"
    read -p "Datenbank wirklich zurücksetzen? (y/N): " confirm
    
    if [[ $confirm != "y" && $confirm != "Y" ]]; then
        echo -e "${YELLOW}Abgebrochen${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}🔄 Setze Datenbank zurück...${NC}"
    docker-compose down
    rm -rf instance/
    docker-compose up -d
    echo -e "${GREEN}✅ Datenbank zurückgesetzt${NC}"
}

# Hauptlogik
case "${1:-help}" in
    setup)
        check_docker
        setup
        ;;
    build)
        check_docker
        build
        ;;
    up)
        check_docker
        up
        ;;
    down)
        check_docker
        down
        ;;
    dev)
        check_docker
        dev
        ;;
    nginx)
        check_docker
        nginx
        ;;
    prod)
        check_docker
        prod
        ;;
    logs)
        check_docker
        logs
        ;;
    logs-app)
        check_docker
        logs_app
        ;;
    shell)
        check_docker
        shell
        ;;
    health)
        health
        ;;
    status)
        check_docker
        status
        ;;
    restart)
        check_docker
        restart
        ;;
    update)
        check_docker
        update
        ;;
    backup)
        check_docker
        backup
        ;;
    restore)
        check_docker
        restore
        ;;
    clean)
        check_docker
        clean
        ;;
    reset-db)
        check_docker
        reset_db
        ;;
    help|*)
        show_help
        ;;
esac
