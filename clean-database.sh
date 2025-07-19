#!/bin/bash
# Datenbank-Bereinigungsskript für SchulBuddy

echo "🧹 SchulBuddy Datenbank-Bereinigung"
echo "===================================="

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️ $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Funktion um Benutzer zu fragen
ask_confirmation() {
    echo -e "${YELLOW}$1${NC}"
    read -p "Fortfahren? (j/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[JjYy]$ ]]; then
        log_info "Abgebrochen."
        exit 0
    fi
}

echo "Optionen:"
echo "1. 🗑️  Komplette Datenbank löschen (ALLE Daten gehen verloren!)"
echo "2. 🧹 Nur temporäre/Cache-Daten löschen"
echo "3. 📋 Datenbank-Status anzeigen"
echo "4. 💾 Backup vor Bereinigung erstellen"
echo "5. 🔄 Datenbank neu initialisieren"
echo ""
read -p "Wähle eine Option (1-5): " choice

case $choice in
    1)
        log_warning "ACHTUNG: Dies löscht ALLE Daten unwiderruflich!"
        ask_confirmation "Wirklich die komplette Datenbank löschen?"
        
        # Container stoppen
        log_info "Stoppe Container..."
        sudo docker-compose down 2>/dev/null || true
        
        # Datenbankdateien löschen
        log_info "Lösche Datenbankdateien..."
        rm -f instance/schulbuddy.db*
        rm -f instance/*.db
        rm -f *.db
        
        log_success "Datenbank komplett gelöscht!"
        log_info "Starte Container neu um neue DB zu erstellen..."
        sudo docker-compose up -d
        ;;
        
    2)
        log_info "Bereinige temporäre Daten..."
        
        # Flask-Cache löschen
        rm -rf __pycache__/ 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        find . -name "__pycache__" -type d -delete 2>/dev/null || true
        
        # Log-Dateien löschen
        rm -f *.log 2>/dev/null || true
        rm -f instance/*.log 2>/dev/null || true
        
        # Temporäre Uploads löschen
        find static/uploads/ -name "tmp_*" -delete 2>/dev/null || true
        
        log_success "Temporäre Daten bereinigt!"
        ;;
        
    3)
        log_info "Datenbank-Status:"
        echo ""
        
        if [ -f "instance/schulbuddy.db" ]; then
            log_success "Hauptdatenbank gefunden: instance/schulbuddy.db"
            echo "Größe: $(ls -lh instance/schulbuddy.db | awk '{print $5}')"
            echo "Letzte Änderung: $(ls -l instance/schulbuddy.db | awk '{print $6, $7, $8}')"
            
            # Tabellen-Info (falls sqlite3 verfügbar)
            if command -v sqlite3 &> /dev/null; then
                echo ""
                log_info "Tabellen in der Datenbank:"
                sqlite3 instance/schulbuddy.db ".tables" 2>/dev/null || log_warning "Konnte Tabellen nicht lesen"
                
                echo ""
                log_info "Datensätze pro Tabelle:"
                for table in $(sqlite3 instance/schulbuddy.db ".tables" 2>/dev/null); do
                    count=$(sqlite3 instance/schulbuddy.db "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "?")
                    echo "  $table: $count Einträge"
                done
            fi
        else
            log_warning "Keine Datenbank gefunden!"
        fi
        
        # Andere Datenbankdateien suchen
        echo ""
        log_info "Weitere Datenbankdateien:"
        find . -name "*.db" -type f 2>/dev/null | while read file; do
            echo "  $file ($(ls -lh "$file" | awk '{print $5}'))"
        done
        ;;
        
    4)
        log_info "Erstelle Backup..."
        
        if [ -f "instance/schulbuddy.db" ]; then
            backup_name="backup_schulbuddy_$(date +%Y%m%d_%H%M%S).db"
            cp instance/schulbuddy.db "$backup_name"
            log_success "Backup erstellt: $backup_name"
            
            # Optional: Backup komprimieren
            if command -v gzip &> /dev/null; then
                gzip "$backup_name"
                log_success "Backup komprimiert: ${backup_name}.gz"
            fi
        else
            log_error "Keine Datenbank zum Backup gefunden!"
        fi
        ;;
        
    5)
        log_warning "Dies wird die Datenbank neu initialisieren!"
        ask_confirmation "Alle bestehenden Daten gehen verloren!"
        
        # Backup erstellen
        if [ -f "instance/schulbuddy.db" ]; then
            backup_name="backup_before_reinit_$(date +%Y%m%d_%H%M%S).db"
            cp instance/schulbuddy.db "$backup_name"
            log_success "Sicherheitsbackup erstellt: $backup_name"
        fi
        
        # Container stoppen
        log_info "Stoppe Container..."
        sudo docker-compose down 2>/dev/null || true
        
        # Datenbank löschen
        rm -f instance/schulbuddy.db*
        
        # Verzeichnisse neu erstellen
        mkdir -p instance static/uploads
        chmod 755 instance static/uploads
        
        # Container starten (erstellt neue DB)
        log_info "Starte Container und erstelle neue Datenbank..."
        sudo docker-compose up -d
        
        # Warten und testen
        sleep 10
        if curl -f http://localhost:5000/health 2>/dev/null; then
            log_success "Datenbank erfolgreich neu initialisiert!"
        else
            log_warning "Container läuft, aber Health-Check fehlgeschlagen"
            log_info "Prüfe Logs: sudo docker-compose logs schulbuddy"
        fi
        ;;
        
    *)
        log_error "Ungültige Option!"
        exit 1
        ;;
esac

echo ""
log_info "Bereinigung abgeschlossen!"
echo ""
log_info "Nützliche Kommandos:"
echo "  Container-Status: sudo docker-compose ps"
echo "  Logs anzeigen: sudo docker-compose logs -f"
echo "  Zugang: http://localhost:5000"
