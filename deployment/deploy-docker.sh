#!/bin/bash
# Docker Deployment Script für SchulBuddy

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Konfiguration
REPO="ghcr.io/timbobn/schulbuddy"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

echo -e "${BLUE}🚀 SchulBuddy Docker Deployment${NC}"

# Funktionen
check_requirements() {
    echo -e "${BLUE}📋 Prüfe Systemvoraussetzungen...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker ist nicht installiert${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose ist nicht installiert${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker und Docker Compose verfügbar${NC}"
}

setup_environment() {
    echo -e "${BLUE}⚙️ Richte Umgebung ein...${NC}"
    
    if [[ ! -f $ENV_FILE ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example $ENV_FILE
            echo -e "${YELLOW}⚠️ .env Datei erstellt. Bitte SECRET_KEY anpassen!${NC}"
        else
            echo -e "${RED}❌ Keine .env.example Datei gefunden${NC}"
            exit 1
        fi
    fi
    
    # Prüfe ob SECRET_KEY geändert wurde
    if grep -q "your-very-secure-secret-key-change-this" $ENV_FILE; then
        echo -e "${RED}❌ SECRET_KEY wurde nicht geändert! Bitte .env bearbeiten.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Umgebung konfiguriert${NC}"
}

pull_latest_image() {
    local tag=${1:-latest}
    echo -e "${BLUE}📥 Lade neuestes Docker Image...${NC}"
    
    docker pull "${REPO}:${tag}" || {
        echo -e "${RED}❌ Fehler beim Laden des Images${NC}"
        exit 1
    }
    
    echo -e "${GREEN}✅ Image geladen: ${REPO}:${tag}${NC}"
}

backup_data() {
    echo -e "${BLUE}💾 Erstelle Backup...${NC}"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    mkdir -p backups
    
    if docker-compose ps | grep -q "Up"; then
        # Datenbank-Backup
        docker-compose exec -T schulbuddy cp /app/instance/schulbuddy.db "/app/instance/backup_${timestamp}.db" || true
        container_id=$(docker-compose ps -q schulbuddy)
        docker cp "${container_id}:/app/instance/backup_${timestamp}.db" "./backups/" || true
        
        # Uploads-Backup
        tar -czf "backups/uploads_${timestamp}.tar.gz" static/uploads/ || true
        
        echo -e "${GREEN}✅ Backup erstellt: backups/backup_${timestamp}.db${NC}"
    else
        echo -e "${YELLOW}⚠️ Container läuft nicht, überspringe Backup${NC}"
    fi
}

deploy() {
    local tag=${1:-latest}
    echo -e "${BLUE}🚀 Starte Deployment...${NC}"
    
    # Backup erstellen
    backup_data
    
    # Image laden
    pull_latest_image $tag
    
    # Services stoppen
    echo -e "${BLUE}🛑 Stoppe Services...${NC}"
    docker-compose down || true
    
    # Services starten
    echo -e "${BLUE}▶️ Starte Services...${NC}"
    docker-compose up -d
    
    # Warte auf Health-Check
    echo -e "${BLUE}🏥 Warte auf Health-Check...${NC}"
    sleep 30
    
    for i in {1..12}; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            echo -e "${GREEN}✅ Deployment erfolgreich!${NC}"
            echo -e "${GREEN}🌐 SchulBuddy verfügbar unter: http://localhost:5000${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Warte auf Start... ($i/12)${NC}"
        sleep 10
    done
    
    echo -e "${RED}❌ Health-Check fehlgeschlagen${NC}"
    echo -e "${YELLOW}📋 Zeige Logs:${NC}"
    docker-compose logs --tail=50 schulbuddy
    exit 1
}

rollback() {
    echo -e "${BLUE}🔄 Rollback wird durchgeführt...${NC}"
    
    # Zeige verfügbare Backups
    echo -e "${CYAN}Verfügbare Backups:${NC}"
    ls -la backups/backup_*.db 2>/dev/null || {
        echo -e "${RED}❌ Keine Backups gefunden${NC}"
        exit 1
    }
    
    # Letztes Backup automatisch wählen
    latest_backup=$(ls -t backups/backup_*.db 2>/dev/null | head -1)
    
    if [[ -n $latest_backup ]]; then
        echo -e "${BLUE}📄 Verwende Backup: $latest_backup${NC}"
        
        # Container stoppen
        docker-compose down
        
        # Backup wiederherstellen
        cp "$latest_backup" instance/schulbuddy.db
        
        # Container starten
        docker-compose up -d
        
        echo -e "${GREEN}✅ Rollback abgeschlossen${NC}"
    else
        echo -e "${RED}❌ Kein Backup verfügbar${NC}"
        exit 1
    fi
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    docker-compose ps
    
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
    docker-compose logs --tail=$lines schulbuddy
}

# Hauptlogik
case "${1:-deploy}" in
    "check")
        check_requirements
        ;;
    "setup")
        check_requirements
        setup_environment
        ;;
    "deploy")
        check_requirements
        setup_environment
        deploy "${2:-latest}"
        ;;
    "rollback")
        rollback
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs "${2:-50}"
        ;;
    "backup")
        backup_data
        ;;
    *)
        echo -e "${CYAN}SchulBuddy Docker Deployment Script${NC}"
        echo ""
        echo -e "${GREEN}Verwendung: $0 <command> [options]${NC}"
        echo ""
        echo -e "${YELLOW}Commands:${NC}"
        echo -e "  check    - Prüfe Systemvoraussetzungen"
        echo -e "  setup    - Richte Umgebung ein"
        echo -e "  deploy   - Vollständiges Deployment [tag]"
        echo -e "  rollback - Rollback zum letzten Backup"
        echo -e "  status   - Zeige Service-Status"
        echo -e "  logs     - Zeige Logs [anzahl_zeilen]"
        echo -e "  backup   - Erstelle manuelles Backup"
        echo ""
        echo -e "${YELLOW}Beispiele:${NC}"
        echo -e "  $0 deploy main    # Deploy main branch"
        echo -e "  $0 deploy v1.0.0  # Deploy specific version"
        echo -e "  $0 logs 100       # Show last 100 log lines"
        ;;
esac
