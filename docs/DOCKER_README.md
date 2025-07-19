# SchulBuddy Docker Setup

Dieses Projekt enthält eine vollständige Docker-Konfiguration für die SchulBuddy Flask-Anwendung.

## 🚀 Schnellstart

### Voraussetzungen
- Docker Desktop installiert
- Docker Compose verfügbar

### Setup (Windows)
```bash
# Setup-Script ausführen
setup.bat

# Oder manuell:
docker-compose build
cp .env.example .env
# .env Datei bearbeiten!
```

### Setup (Linux/macOS)
```bash
# Setup-Script ausführen
chmod +x setup.sh
./setup.sh

# Oder manuell:
docker-compose build
cp .env.example .env
# .env Datei bearbeiten!
```

## 🔧 Konfiguration

### Environment-Variablen (.env)
Kopieren Sie `.env.example` zu `.env` und passen Sie die Werte an:

```env
SECRET_KEY=your-very-secure-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/schulbuddy.db
FLASK_ENV=production
SESSION_TIMEOUT_MINUTES=120
# ... weitere Einstellungen
```

**⚠️ Wichtig**: Ändern Sie unbedingt den `SECRET_KEY` für die Produktion!

## 🏃‍♂️ Anwendung starten

### Einfache Konfiguration (nur SchulBuddy)
```bash
docker-compose up -d
```

### Mit nginx Reverse Proxy
```bash
docker-compose --profile nginx up -d
```

Die Anwendung ist dann verfügbar unter:
- Einfach: http://localhost:5000
- Mit nginx: http://localhost:80

## 📋 Verwaltung

### Logs anzeigen
```bash
# Alle Services
docker-compose logs -f

# Nur SchulBuddy
docker-compose logs -f schulbuddy

# Nur nginx
docker-compose logs -f nginx
```

### Status prüfen
```bash
docker-compose ps
```

### Container stoppen
```bash
docker-compose down
```

### Container stoppen und Volumes löschen
```bash
docker-compose down -v
```

### Neu bauen
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 📁 Datenverteilung

### Volumes
- `schulbuddy_data`: SQLite-Datenbank und Instanz-Daten
- `schulbuddy_uploads`: Hochgeladene Dateien

### Backup erstellen
```bash
# Datenbank-Backup
docker-compose exec schulbuddy cp /app/instance/schulbuddy.db /app/backup.db
docker cp $(docker-compose ps -q schulbuddy):/app/backup.db ./backup.db

# Uploads-Backup
docker run --rm -v schulbuddy_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads.tar.gz -C /data .
```

### Backup wiederherstellen
```bash
# Datenbank wiederherstellen
docker cp ./backup.db $(docker-compose ps -q schulbuddy):/app/instance/schulbuddy.db
docker-compose restart schulbuddy
```

## 🔒 Sicherheit

### Produktionseinstellungen
1. **SECRET_KEY**: Verwenden Sie einen starken, zufälligen Schlüssel
2. **HTTPS**: Konfigurieren Sie SSL-Zertifikate für nginx
3. **Firewall**: Beschränken Sie Zugriff auf notwendige Ports
4. **Updates**: Halten Sie Base-Images aktuell

### SSL/TLS mit nginx
1. Platzieren Sie Zertifikate in `./ssl/`
2. Aktualisieren Sie `nginx.conf` für HTTPS
3. Starten Sie mit `--profile nginx`

## 🐛 Troubleshooting

### Häufige Probleme

#### Container startet nicht
```bash
# Logs prüfen
docker-compose logs schulbuddy

# Container-Status prüfen
docker-compose ps
```

#### Port bereits in Verwendung
```bash
# Anderen Service stoppen oder Port in docker-compose.yml ändern
docker-compose down
# Port in docker-compose.yml anpassen
docker-compose up -d
```

#### Datenbank-Probleme
```bash
# Container neu starten
docker-compose restart schulbuddy

# Datenbank neu initialisieren (⚠️ löscht alle Daten!)
docker-compose down -v
docker-compose up -d
```

#### Permission-Probleme
```bash
# Container läuft als non-root user
# Volumes sollten automatisch richtige Berechtigungen haben
docker-compose exec schulbuddy ls -la /app/
```

### Container debuggen
```bash
# In Container einloggen
docker-compose exec schulbuddy bash

# Python-Shell
docker-compose exec schulbuddy python
```

## 📊 Monitoring

### Health Checks
Die Anwendung hat eingebaute Health Checks:
```bash
# Status prüfen
curl http://localhost:5000/health

# Docker Health Status
docker inspect $(docker-compose ps -q schulbuddy) | grep Health -A 10
```

### Resource-Nutzung
```bash
# Container-Statistiken
docker stats $(docker-compose ps -q)
```

## 🔧 Entwicklung

### Development-Setup
Für die Entwicklung können Sie das lokale Verzeichnis mounten:

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  schulbuddy:
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=development
      - DEBUG=True
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## 📄 Dateien

- `Dockerfile`: Multi-stage Build für optimierte Images
- `docker-compose.yml`: Service-Definition
- `nginx.conf`: nginx Reverse Proxy Konfiguration
- `.dockerignore`: Ausgeschlossene Dateien für Build
- `.env.example`: Template für Environment-Variablen
- `setup.sh` / `setup.bat`: Automatisches Setup-Script
