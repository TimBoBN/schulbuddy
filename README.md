# SchulBuddy Docker Setup

**SchulBuddy** - Eine Flask-Anwendung für die Verwaltung von Schulaufgaben, Noten und Lernfortschritt.

Dieses Repository enthält sowohl die **Python-Anwendung** als auch vollständige **Docker-Containerisierung** mit CI/CD-Pipeline.

## 🚀 Deployment-Optionen

**Wähle deine bevorzugte Methode:**

| Methode | Schwierigkeit | Empfehlung |
|---------|---------------|------------|
| 🐳 **Docker Container** | ⭐ Einfach | Für Produktion und schnellen Start |
| 🐍 **Python Direkt** | ⭐⭐ Mittel | Für Development und Anpassungen |
| 🤖 **GitHub Actions** | ⭐⭐⭐ Automatisch | Für CI/CD und automatische Deployments |

---

## 🚀 Schnellstart

### 1. Repository klonen und vorbereiten
```bash
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

### 2. Setup mit Start-Scripts

**Linux/Mac:**
```bash
./start.sh setup
```

**Windows (PowerShell):**
```powershell
.\start.ps1 setup
```

Dies erstellt automatisch eine `.env` Datei aus der Vorlage.

### 3. Umgebungsvariablen anpassen
Bearbeite die `.env` Datei und setze mindestens:
- `SECRET_KEY`: Ein sicherer, zufälliger Schlüssel ⚠️ **Unbedingt ändern!**
- `CURRENT_SCHOOL_YEAR`: Das aktuelle Schuljahr (z.B. 2024/25)
- `CURRENT_SEMESTER`: Das aktuelle Semester (1 oder 2)

### 4. Anwendung starten

**🔧 Mit Start-Scripts (Empfohlen):**

**Linux/Mac:**
```bash
# Development
./start.sh dev

# Produktion
./start.sh up

# Mit Nginx Reverse Proxy
./start.sh nginx

# Vollständige Produktionsumgebung
./start.sh prod
```

**Windows (PowerShell):**
```powershell
# Development
.\start.ps1 dev

# Produktion  
.\start.ps1 up

# Mit Nginx Reverse Proxy
.\start.ps1 nginx
```

**🐳 Direkt mit Docker Compose:**
```bash
# Nur SchulBuddy starten
docker-compose up -d

# Mit Nginx Reverse Proxy starten
docker-compose --profile with-nginx up -d

# Produktionsumgebung mit Gunicorn
docker-compose -f docker-compose.prod.yml --profile production up -d
```

**📦 Von GitHub Container Registry:**
```bash
# Latest Version
docker pull ghcr.io/timbobn/schulbuddy:main
docker run -d -p 5000:5000 --env-file .env ghcr.io/timbobn/schulbuddy:main

# Specific Version
docker pull ghcr.io/timbobn/schulbuddy:v1.0.0
```

**🐍 Python Package (ohne Docker):**
```bash
# Von GitHub Release
wget https://github.com/TimBoBN/schulbuddy/releases/latest/download/schulbuddy-python-package.tar.gz
tar -xzf schulbuddy-python-package.tar.gz
cd schulbuddy
pip install -r requirements-frozen.txt
python app.py

# Oder direkt aus Repository
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
# .env bearbeiten (SECRET_KEY ändern!)
python app.py
```

**🚀 Deployment-Scripts für Server:**
```bash
# Docker Deployment
wget https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/deployment/deploy-docker.sh
chmod +x deploy-docker.sh
./deploy-docker.sh deploy main

# Python Deployment
wget https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/deployment/deploy-python.sh
chmod +x deploy-python.sh
sudo ./deploy-python.sh install
sudo ./deploy-python.sh deploy schulbuddy-python-package.tar.gz
```

Die Anwendung ist dann erreichbar unter:
- **Development:** http://localhost:5000 (mit Hot-Reload)
- **Produktion:** http://localhost:5000 
- **Mit Nginx:** http://localhost
- **Produktion mit SSL:** https://localhost (nach SSL-Konfiguration)

## 🤖 GitHub Actions & CI/CD

### Automatische Builds und Deployments

Das Repository enthält vollständige GitHub Actions Workflows:

**📋 Verfügbare Workflows:**
- **`.github/workflows/docker.yml`** - Docker Container Build & Deploy
- **`.github/workflows/python.yml`** - Python Package Testing & Build
- **`.github/workflows/ci-cd.yml`** - Kombinierte CI/CD Pipeline

**🚀 Automatische Deployments:**
- **Push zu `dev`** → Staging Deployment
- **Push zu `main`** → Production Deployment  
- **Tags (`v*`)** → Release mit Assets

**📦 Verfügbare Artefakte:**
```bash
# Docker Images (GitHub Container Registry)
docker pull ghcr.io/timbobn/schulbuddy:main      # Latest main
docker pull ghcr.io/timbobn/schulbuddy:dev       # Latest dev
docker pull ghcr.io/timbobn/schulbuddy:v1.0.0    # Specific version

# Python Packages (GitHub Releases)
# Automatisch bei jedem Release verfügbar
```

**🔧 Setup für eigenes Repository:**
1. Repository Settings → Secrets → Actions:
   - `GITHUB_TOKEN` (automatisch verfügbar)
   - Optional: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
2. Settings → Environments:
   - `staging` für Development-Deployments
   - `production` für Production-Deployments (mit Approval)

**📖 Vollständige Dokumentation:** Siehe [`deployment/README.md`](deployment/README.md)

## ⚙️ Konfiguration

### 📁 Repository-Struktur
```
schulbuddy/
├── 📁 .github/workflows/           # GitHub Actions CI/CD
│   ├── ci-cd.yml                   # Kombinierte Pipeline
│   ├── docker.yml                 # Docker-spezifisch
│   └── python.yml                 # Python-spezifisch
├── 📁 deployment/                  # Deployment Scripts
│   ├── deploy-docker.sh            # Docker Server-Deployment
│   ├── deploy-python.sh            # Python Server-Deployment
│   └── README.md                   # Deployment-Dokumentation
├── 📁 routes/                      # 🐍 Flask Routes
├── 📁 static/                      # 🐍 Static Files (CSS, JS)
├── 📁 templates/                   # 🐍 Jinja2 Templates
├── 📁 instance/                    # 🐍 Database & User Data
├── 📄 app.py                       # 🐍 Flask Hauptanwendung
├── 📄 models.py                    # 🐍 SQLAlchemy Models
├── 📄 config.py                    # 🐍 App Configuration
├── 📄 requirements.txt             # 🐍 Python Dependencies
├── 🐳 Dockerfile                   # Docker Produktions-Image
├── 🐳 Dockerfile.dev               # Docker Development-Image  
├── 🐳 docker-compose.yml           # Docker Standard-Setup
├── 🐳 docker-compose.dev.yml       # Docker Development
├── 🐳 docker-compose.prod.yml      # Docker Produktion
├── 🔧 start.sh                     # Linux/Mac Start-Script
├── 🔧 start.ps1                    # Windows Start-Script
└── 📋 README.md                    # Diese Dokumentation
```

**🎯 Flexibilität:** Du kannst SchulBuddy auf drei Arten verwenden:
1. **🐳 Docker** - Einfach und konsistent (empfohlen)
2. **🐍 Python** - Direkt auf deinem System  
3. **🤖 Automatisch** - Via GitHub Actions deployment

### 📁 Dateienübersicht
```
schulbuddy/
├── Dockerfile              # Produktions-Container
├── Dockerfile.dev          # Development-Container
├── docker-compose.yml      # Standard-Konfiguration
├── docker-compose.dev.yml  # Development mit Hot-Reload
├── docker-compose.prod.yml # Produktion mit Gunicorn & SSL
├── nginx.conf              # Nginx-Basis-Konfiguration
├── nginx.prod.conf         # Nginx für Produktion mit SSL
├── .env.example            # Umgebungsvariablen-Vorlage
├── start.sh               # Linux/Mac Start-Script
├── start.ps1              # Windows PowerShell Script
└── Makefile               # Make-Kommandos für Linux/Mac
```

### 🔧 Start-Scripts

**Linux/Mac (`./start.sh`):**
- `setup` - Erstelle .env Datei
- `build` - Docker Images bauen
- `up` - Produktions-Setup starten
- `dev` - Development mit Hot-Reload
- `nginx` - Mit Nginx Reverse Proxy
- `prod` - Vollständige Produktionsumgebung
- `logs` - Alle Logs anzeigen
- `logs-app` - Nur App-Logs
- `shell` - Shell im Container öffnen  
- `health` - Health-Check ausführen
- `status` - Container-Status anzeigen
- `backup` - Backup erstellen
- `restore` - Backup wiederherstellen
- `update` - Anwendung aktualisieren
- `clean` - Container aufräumen

**Windows (`.\start.ps1`):**
- Gleiche Kommandos wie Linux-Version
- Optimiert für PowerShell

### 🌍 Umgebungsvariablen
Wichtige Umgebungsvariablen in der `.env` Datei:

- `SECRET_KEY`: Flask Secret Key (unbedingt ändern!)
- `DATABASE_URL`: Datenbankverbindung (Standard: SQLite)
- `SESSION_TIMEOUT_MINUTES`: Session-Timeout in Minuten
- `CURRENT_SCHOOL_YEAR`: Aktuelles Schuljahr
- `CURRENT_SEMESTER`: Aktuelles Semester

### 💾 Persistente Daten
Die Docker-Konfiguration nutzt Volumes für:

**Named Volumes (Produktion):**
- `schulbuddy_data` - Datenbankdateien
- `schulbuddy_uploads` - Hochgeladene Dateien

**Bind Mounts (Development):**
- `./instance` - Datenbankdateien (lokal zugänglich)
- `./static/uploads` - Hochgeladene Dateien (lokal zugänglich)

### 🌐 Ports und Services
- Port 5000: SchulBuddy direkt
- Port 80: Nginx Reverse Proxy (HTTP)
- Port 443: Nginx Reverse Proxy (HTTPS)

## 🔧 Entwicklung

### 🐍 Python Development (ohne Docker)

**Setup:**
```bash
# Repository klonen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# .env bearbeiten - SECRET_KEY ändern!

# Datenbank initialisieren
python init_db.py

# Development Server starten
python app.py
```

**Development Features:**
- 🔄 Hot-Reload mit Flask Debug-Modus
- 🐛 Direkter Zugriff auf Python-Debugger
- 📝 Logs direkt in der Konsole
- 💾 Lokale Datei-Bearbeitung ohne Container

### 🐳 Docker Development

### Quick Commands

**Linux/Mac:**
```bash
./start.sh dev       # Development starten
./start.sh logs-app  # App-Logs anzeigen
./start.sh shell     # Container-Shell öffnen
```

**Windows:**
```powershell
.\start.ps1 dev       # Development starten
.\start.ps1 logs      # Logs anzeigen
.\start.ps1 shell     # Container-Shell öffnen
```

### Lokale Entwicklung mit Docker
```bash
# Mit Live-Reload für Entwicklung
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Oder mit Start-Script
./start.sh dev          # Linux/Mac
.\start.ps1 dev         # Windows
```

**Development Features:**
- 🔄 Hot-Reload bei Dateiänderungen
- 🐛 Debug-Modus aktiviert
- 📝 Ausführliche Logs
- 💾 Code-Volumes für Live-Editing

### Logs anzeigen
```bash
# Alle Services
docker-compose logs -f
./start.sh logs         # Linux/Mac
.\start.ps1 logs        # Windows

# Nur SchulBuddy
docker-compose logs -f schulbuddy
./start.sh logs-app     # Linux/Mac
```

### Container-Shell
```bash
docker-compose exec schulbuddy bash
./start.sh shell        # Linux/Mac
.\start.ps1 shell       # Windows
```

## 🏭 Produktionsnutzung

### Quick Start Produktion

**Linux/Mac:**
```bash
./start.sh setup       # .env erstellen
./start.sh prod        # Produktionsumgebung starten
```

**Windows:**
```powershell
.\start.ps1 setup      # .env erstellen  
.\start.ps1 up         # Produktion starten
```

### ⚠️ Wichtige Sicherheitshinweise
1. **SECRET_KEY ändern** - Unbedingt in der `.env` Datei ändern!
2. **HTTPS verwenden** - In Produktion immer SSL/TLS nutzen
3. **Sichere Cookies** - `SESSION_COOKIE_SECURE=true` bei HTTPS setzen
4. **Regelmäßige Backups** - Automatisierte Datensicherung einrichten
5. **Updates** - Regelmäßig Docker Images und Dependencies aktualisieren
6. **Firewall** - Nur benötigte Ports öffnen
7. **Monitoring** - Health-Checks und Logs überwachen

### 📦 Backup und Wiederherstellung

**Mit Start-Scripts (empfohlen):**

Linux/Mac:
```bash
./start.sh backup      # Vollständiges Backup erstellen
./start.sh restore     # Backup wiederherstellen
```

Windows:
```powershell
.\start.ps1 backup     # Backup erstellen
```

**Manuell:**
```bash
# Datenbank-Backup
docker-compose exec schulbuddy cp /app/instance/schulbuddy.db /app/instance/backup_$(date +%Y%m%d_%H%M%S).db

# Uploads-Backup
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz static/uploads/
```

### 🔄 Updates und Wartung

**Automatisches Update (empfohlen):**

Linux/Mac:
```bash
./start.sh update      # Vollständiges Update mit Backup
```

**Manuelles Update:**
```bash
# Neue Version pullen und Container neu bauen
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 🔒 SSL/HTTPS Konfiguration

Für HTTPS in Produktion:

1. **SSL-Zertifikate vorbereiten:**
```bash
mkdir ssl
# Kopiere deine Zertifikate nach ./ssl/cert.pem und ./ssl/key.pem
```

2. **Produktionsumgebung starten:**
```bash
./start.sh prod        # Linux/Mac
```

3. **Domain in nginx.prod.conf anpassen:**
```nginx
server_name your-domain.com;
```

## 🍓 Raspberry Pi Spezifische Anleitung

### ⚡ Sofort-Fix (One-Liner):
```bash
chmod +x emergency-raspberry-pi.sh && ./emergency-raspberry-pi.sh
```

### Problem: "unable to open database file"

**Schnelle Lösung:**
```bash
# Direkt auf dem Raspberry Pi
chmod +x fix-raspberry-pi.sh
./fix-raspberry-pi.sh
```

**Emergency Fix (falls alles andere fehlschlägt):**
```bash
chmod +x emergency-raspberry-pi.sh
./emergency-raspberry-pi.sh
```
Dieses Skript versucht **3 verschiedene Methoden** und wird definitiv funktionieren!

**Manuelle Lösung:**
```bash
# 1. Container stoppen
sudo docker-compose down

# 2. Berechtigungen reparieren
sudo rm -rf instance/schulbuddy.db
mkdir -p instance static/uploads
sudo chown -R $USER:$USER instance static
chmod -R 755 instance static

# 3. Container mit User ID starten
echo "
version: '3.8'
services:
  schulbuddy:
    user: '1000:1000'
    environment:
      - DATABASE_URL=sqlite:///instance/schulbuddy.db
" > docker-compose.override.yml

# 4. Neu bauen und starten
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

**Raspberry Pi IP finden:**
```bash
hostname -I
```

SchulBuddy läuft dann unter: `http://[RASPBERRY-PI-IP]:5000`

## 🔍 Troubleshooting

### 🛠️ Quick Diagnostics

**Health-Check:**
```bash
./start.sh health      # Linux/Mac
.\start.ps1 health     # Windows
curl http://localhost:5000/health  # Manuell
```

**Status prüfen:**
```bash
./start.sh status      # Linux/Mac
.\start.ps1 status     # Windows
docker-compose ps      # Manuell
```

### ❗ Häufige Probleme

**1. Container startet nicht:**
```bash
# Logs prüfen
docker-compose logs schulbuddy
./start.sh logs-app    # Linux/Mac
.\start.ps1 logs       # Windows

# Container Status prüfen
docker-compose ps
./start.sh status      # Linux/Mac
.\start.ps1 status     # Windows
```

**2. Datenbankfehler:**
```bash
# Datenbank neu initialisieren (⚠️ Alle Daten gehen verloren!)
docker-compose down
rm -rf instance/
docker-compose up -d

# Oder mit Script
./start.sh reset-db    # Linux/Mac (mit Sicherheitsabfrage)
```

**3. Berechtigungsprobleme:**
```bash
# Berechtigungen für Uploads-Ordner
chmod -R 755 static/uploads/

# Docker-Berechtigungen (Linux)
sudo chown -R $USER:$USER .
```

**4. Port bereits belegt:**
```bash
# Prüfe welcher Prozess Port 5000 nutzt
lsof -i :5000          # Linux/Mac
netstat -an | grep 5000  # Windows

# Anderen Port verwenden
PORT=5001 docker-compose up -d
```

**5. Speicherplatz-Probleme:**
```bash
# Docker aufräumen
./start.sh clean       # Linux/Mac
.\start.ps1 clean      # Windows

# Oder manuell
docker system prune -a
```

## 📊 Service-Überwachung

### 🏥 Health-Check
Der Container hat einen integrierten Health-Check:
```bash
# Status prüfen
docker-compose ps
./start.sh status      # Linux/Mac
.\start.ps1 status     # Windows

# Health-Check manuell ausführen
curl http://localhost:5000/health
./start.sh health      # Linux/Mac
.\start.ps1 health     # Windows
```

**Health-Check Response:**
```json
{
  "status": "healthy",
  "message": "SchulBuddy is running"
}
```

### 📈 Monitoring für Produktion
Empfohlene Tools für Produktionsumgebungen:
- **📊 Prometheus + Grafana** - Metriken und Dashboards
- **📋 ELK Stack** - Log-Aggregation und -Analyse
- **⏰ Uptime-Monitoring** - Verfügbarkeitsüberwachung
- **🔔 Alerting** - Benachrichtigungen bei Problemen

### 📱 Monitoring-Setup (Optional)

**Prometheus + Grafana:**
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🚀 Skalierung

### 📈 Horizontale Skalierung
```bash
# Mehrere SchulBuddy-Instanzen (Load Balancing)
docker-compose up -d --scale schulbuddy=3

# Mit Nginx Load Balancer
docker-compose --profile with-nginx up -d --scale schulbuddy=3
```

**⚠️ Wichtig:** Bei Skalierung SQLite durch PostgreSQL/MySQL ersetzen!

### 🗃️ Externe Datenbank (Empfohlen für Produktion)

**PostgreSQL in der `.env`:**
```env
DATABASE_URL=postgresql://user:password@db_host:5432/schulbuddy
```

**MySQL in der `.env`:**
```env
DATABASE_URL=mysql://user:password@db_host:3306/schulbuddy
```

**Docker Compose mit PostgreSQL:**
```yaml
# docker-compose.postgres.yml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: schulbuddy
      POSTGRES_USER: schulbuddy
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔧 Erweiterte Konfiguration

### 🐳 Docker Images

**Verfügbare Images:**
- `schulbuddy:latest` - Produktions-Image
- `schulbuddy:dev` - Development-Image mit Debug-Tools

**Custom Build:**
```bash
# Produktions-Image
docker build -t schulbuddy:prod .

# Development-Image
docker build -f Dockerfile.dev -t schulbuddy:dev .
```

### 📝 Environment-Variablen (Vollständig)

```env
# Flask Core
SECRET_KEY=your-very-secure-secret-key
FLASK_ENV=production

# Database
DATABASE_URL=sqlite:///instance/schulbuddy.db

# Session Management
SESSION_TIMEOUT_MINUTES=120
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
REMEMBER_COOKIE_DAYS=30

# Security
LOGIN_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_TIMEOUT_MINUTES=15
TWO_FACTOR_TIMEOUT_MINUTES=5

# School Settings
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1

# File Uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=static/uploads

# Performance
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

## 🎯 Best Practices

### 🔐 Sicherheit
1. **Starke Passwörter** - Komplexe SECRET_KEY verwenden
2. **HTTPS Only** - Nie HTTP in Produktion
3. **Firewall** - Nur benötigte Ports öffnen
4. **Updates** - Regelmäßige Sicherheitsupdates
5. **Backups** - Automatisierte, verschlüsselte Backups
6. **Monitoring** - Kontinuierliche Überwachung

### 🏗️ Architektur
1. **Reverse Proxy** - Nginx für statische Dateien
2. **Load Balancer** - Bei hoher Last
3. **Externe DB** - PostgreSQL/MySQL für Skalierung
4. **Caching** - Redis für Session-Management
5. **CDN** - Für statische Assets

### 📋 Wartung
1. **Regelmäßige Backups** - Automatisiert
2. **Log-Rotation** - Speicherplatz-Management
3. **Health-Checks** - Kontinuierliche Überwachung
4. **Updates** - Geplante Wartungsfenster
5. **Dokumentation** - Aktuelle Dokumentation

## 🆘 Support und Hilfe

### 📞 Erste Hilfe
```bash
# Komplette Diagnose
./start.sh health && ./start.sh status    # Linux/Mac
.\start.ps1 health; .\start.ps1 status    # Windows

# Logs der letzten 100 Zeilen
docker-compose logs --tail=100 schulbuddy
```

### 🔧 Debugging
```bash
# Debug-Modus aktivieren
FLASK_DEBUG=1 docker-compose up

# Container-Shell für Debugging
./start.sh shell    # Linux/Mac
.\start.ps1 shell   # Windows
```

### 📚 Hilfreiche Kommandos
```bash
# Container-Informationen
docker inspect $(docker-compose ps -q schulbuddy)

# Ressourcen-Verbrauch
docker stats $(docker-compose ps -q)

# Netzwerk-Informationen
docker network ls
docker network inspect schulbuddy-network
```

## 🎉 Fazit

Diese Docker-Konfiguration bietet:
- ✅ **Einfache Bedienung** mit Start-Scripts
- ✅ **Development & Produktion** getrennte Umgebungen
- ✅ **Skalierbarkeit** für wachsende Anforderungen
- ✅ **Sicherheit** mit Best Practices
- ✅ **Wartbarkeit** mit Backup/Restore
- ✅ **Monitoring** mit Health-Checks

**Bei Problemen:**
1. 📋 Logs prüfen: `./start.sh logs`
2. 🏥 Health-Check: `./start.sh health`
3. 📊 Status: `./start.sh status`
4. 🔄 Neustart: `./start.sh restart`

Viel Erfolg mit SchulBuddy! 🎓
