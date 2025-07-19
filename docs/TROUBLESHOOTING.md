# 🔍 Troubleshooting Guide

Häufige Probleme und deren Lösungen für SchulBuddy Docker Setup.

## 🚨 Häufige Probleme

### 1. "Unable to open database file"

**Symptom:** SQLite Datenbankfehler beim Container-Start

**Lösungen:**

```bash
# 1. Berechtigungen reparieren
./start.sh down
sudo chown -R $USER:$USER instance static
chmod -R 755 instance static

# 2. Container neu bauen
./start.sh build
./start.sh up

# 3. Datenbank neu initialisieren
./start.sh reset-db
```

**Manuelle Lösung:**
```bash
# Container mit korrekter User ID
echo "
version: '3.8'
services:
  schulbuddy:
    user: '1000:1000'
    environment:
      - DATABASE_URL=sqlite:///instance/schulbuddy.db
" > docker-compose.override.yml

docker-compose up -d
```

### 2. Port bereits belegt

**Symptom:** "Port 5000 already in use"

**Lösungen:**

```bash
# Port in .env Datei ändern (empfohlen)
# Bearbeite .env und setze: PORT=8080

# Oder temporär anderen Port verwenden
PORT=8080 docker-compose up -d

# Prüfen welcher Prozess den Port nutzt
lsof -i :5000          # Linux/Mac
netstat -an | grep 5000  # Windows
```

### 3. Container startet nicht

**Symptom:** Container Status "Exited (1)"

**Diagnostik:**
```bash
# Container Status prüfen
./start.sh status

# Logs analysieren
./start.sh logs

# Health Check
./start.sh health
```

**Lösungen:**
```bash
# Container neu bauen
./start.sh build --no-cache

# Volumes aufräumen
./start.sh clean

# Komplett neu starten
./start.sh down
./start.sh up
```

### 4. Berechtigungsprobleme

**Symptom:** Permission denied errors

**Lösungen:**

```bash
# Berechtigungen für Uploads-Ordner
chmod -R 755 static/uploads/

# Docker-Berechtigungen (Linux)
sudo chown -R $USER:$USER .

# User Mapping im Container
export UID=$(id -u)
export GID=$(id -g)
docker-compose up -d
```

### 5. Speicherplatz-Probleme

**Symptom:** "No space left on device"

**Lösungen:**

```bash
# Docker aufräumen
./start.sh clean       # Linux/Mac
.\start.ps1 clean      # Windows

# Oder manuell
docker system prune -a

# Logs begrenzen
docker-compose logs --tail=100
```

## 🏥 Diagnostik-Tools

### Quick Health Check

```bash
# Automatische Diagnose
./start.sh health

# Manueller Health Check
curl http://localhost:[PORT]/health
```

### Detaillierte Systemprüfung

```bash
# Docker Status
docker --version
docker-compose --version

# Container Status
docker-compose ps
docker-compose top

# Resource Usage
docker stats

# Logs der letzten 10 Minuten
docker-compose logs --since=10m
```

### Netzwerk-Diagnose

```bash
# Port-Verfügbarkeit prüfen
netstat -tulpn | grep :5000

# DNS Resolution testen
nslookup localhost

# Container Netzwerk
docker network ls
docker network inspect schulbuddy_default
```

## 🛠️ Advanced Troubleshooting

### Debug Container

```bash
# Debug-Container starten
docker run -it --rm \
  -v $(pwd):/app \
  -w /app \
  python:3.11-alpine \
  /bin/sh
```

### Database Debugging

```bash
# SQLite Datei prüfen
file instance/schulbuddy.db

# SQLite Integrität testen
sqlite3 instance/schulbuddy.db "PRAGMA integrity_check;"

# Backup und Restore testen
./start.sh backup
./start.sh restore
```

### Performance Issues

```bash
# Container Ressourcen überwachen
docker stats schulbuddy

# Memory Usage
docker exec schulbuddy cat /proc/meminfo

# Disk Usage
docker exec schulbuddy df -h
```

## 🔧 Environment-spezifische Probleme

### Windows-spezifische Issues

**Problem:** Line ending issues
```bash
# Git Auto-Conversion deaktivieren
git config core.autocrlf false

# Scripts executable machen
chmod +x start.sh
```

**Problem:** Volume Mount issues
```bash
# Docker Desktop Volume Sharing aktivieren
# Settings → Resources → File Sharing
```

### macOS-spezifische Issues

**Problem:** Performance bei Volume Mounts
```bash
# Cached Volumes verwenden
volumes:
  - ./instance:/app/instance:cached
```

### Linux-spezifische Issues

**Problem:** SELinux Kontext
```bash
# SELinux Labels setzen
volumes:
  - ./instance:/app/instance:Z
```

## 📋 Checkliste für Problembehebung

### Basis-Checks
- [ ] Docker und docker-compose installiert?
- [ ] .env Datei vorhanden und korrekt?
- [ ] Ports verfügbar?
- [ ] Berechtigungen korrekt?

### Container-Checks
- [ ] Container läuft? (`docker-compose ps`)
- [ ] Logs zeigen Fehler? (`docker-compose logs`)
- [ ] Health Check erfolgreich? (`./start.sh health`)
- [ ] Volumes gemountet? (`docker inspect`)

### Netzwerk-Checks
- [ ] Port erreichbar? (`curl localhost:PORT`)
- [ ] Firewall blockiert nicht?
- [ ] Proxy-Konfiguration korrekt?

### Datenbank-Checks
- [ ] SQLite Datei existiert?
- [ ] Berechtigungen für DB-Datei?
- [ ] Datenbank-Schema initialisiert?

## 🆘 Letzte Rettung

Wenn nichts anderes funktioniert:

```bash
# Komplett aufräumen und neu starten
./start.sh down
./start.sh clean
rm -rf instance/
docker system prune -a
./start.sh setup
./start.sh build
./start.sh up
```

## 📞 Support

Falls weiterhin Probleme bestehen:

1. **Issue erstellen:** [GitHub Issues](https://github.com/TimBoBN/schulbuddy/issues)
2. **Logs sammeln:** `./start.sh logs > debug.log`
3. **System-Info:** `docker version && docker-compose version`
4. **Environment:** `.env` Datei (ohne Secrets)
