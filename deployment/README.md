# 🚀 SchulBuddy GitHub Actions & Deployment Guide

Diese Anleitung erklärt, wie du SchulBuddy sowohl als Docker Container als auch als direktes Python-Projekt auf GitHub automatisch buildest und deployst.

## 📋 Übersicht der GitHub Actions

### 1. Docker Workflow (`.github/workflows/docker.yml`)
- **Zweck:** Baut Docker Images und pusht sie zur GitHub Container Registry
- **Trigger:** Push auf `main`/`dev`, Pull Requests, Tags
- **Features:**
  - Multi-Platform Builds (AMD64, ARM64)
  - Security Scans mit Trivy
  - Automatisches Deployment zu Staging/Production
  - Container Registry Push

### 2. Python Workflow (`.github/workflows/python.yml`) 
- **Zweck:** Testet Python-Code und erstellt Deployment-Packages
- **Features:**
  - Tests auf Python 3.9, 3.10, 3.11
  - Code-Quality-Checks (Black, Flake8, isort)
  - Security-Scans (Bandit, Safety)
  - Package-Erstellung für Deployment

### 3. Combined Workflow (`.github/workflows/ci-cd.yml`)
- **Zweck:** Kombinierte Pipeline für beide Deployment-Methoden
- **Features:**
  - Vollständige CI/CD Pipeline
  - Parallele Docker und Python Builds
  - Release-Erstellung mit Assets
  - Multi-Environment Deployment

## 🔧 GitHub Repository Setup

### 1. Repository Secrets einrichten

Gehe zu **Settings → Secrets and variables → Actions** und füge hinzu:

```
# Für Docker Deployment (falls privates Registry)
DOCKER_USERNAME=dein-docker-username
DOCKER_PASSWORD=dein-docker-password

# Für Server-Deployments
SSH_PRIVATE_KEY=dein-ssh-private-key
STAGING_HOST=staging-server.domain.com
PRODUCTION_HOST=production-server.domain.com
DEPLOY_USER=deploy-user

# Optional: Slack/Discord Notifications
SLACK_WEBHOOK=https://hooks.slack.com/...
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

### 2. Environments einrichten

Gehe zu **Settings → Environments** und erstelle:

- **staging** - Für Development-Branch Deployments
- **production** - Für Main-Branch Deployments (mit Approval-Rules)

### 3. Branch Protection Rules

Aktiviere für `main` Branch:
- ✅ Require status checks to pass
- ✅ Require pull request reviews
- ✅ Dismiss stale reviews
- ✅ Require branches to be up to date

## 🐳 Docker Deployment

### GitHub Container Registry Setup

1. **Automatisch:** GitHub Actions pusht automatisch zu `ghcr.io/username/schulbuddy`

2. **Manuell lokal testen:**
```bash
# Login zur GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build und Push
docker build -t ghcr.io/username/schulbuddy:latest .
docker push ghcr.io/username/schulbuddy:latest
```

### Server-Deployment mit Docker

**Deployment-Script verwenden:**
```bash
# Script herunterladen
wget https://raw.githubusercontent.com/username/schulbuddy/main/deployment/deploy-docker.sh
chmod +x deploy-docker.sh

# Erstes Setup
./deploy-docker.sh setup

# Deployment
./deploy-docker.sh deploy main     # Deploy main branch
./deploy-docker.sh deploy v1.0.0   # Deploy specific version
```

**Manuelles Deployment:**
```bash
# Server vorbereiten
sudo apt update && sudo apt install -y docker.io docker-compose

# Repository klonen
git clone https://github.com/username/schulbuddy.git
cd schulbuddy

# Environment setup
cp .env.example .env
# .env bearbeiten - SECRET_KEY ändern!

# Image pullen und starten
docker pull ghcr.io/username/schulbuddy:main
docker-compose up -d
```

## 🐍 Python Deployment

### Server-Setup

**Mit Deployment-Script:**
```bash
# Script herunterladen
wget https://raw.githubusercontent.com/username/schulbuddy/main/deployment/deploy-python.sh
chmod +x deploy-python.sh

# Basis-Installation
sudo ./deploy-python.sh install

# Nginx installieren (optional)
sudo ./deploy-python.sh nginx
```

**Manuelle Installation:**
```bash
# Dependencies installieren
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

# User erstellen
sudo useradd -r -s /bin/bash -d /opt/schulbuddy schulbuddy

# Verzeichnisse erstellen
sudo mkdir -p /opt/schulbuddy
sudo chown schulbuddy:schulbuddy /opt/schulbuddy
```

### Deployment von GitHub Releases

```bash
# Latest Release herunterladen
wget https://github.com/username/schulbuddy/releases/latest/download/schulbuddy-python-package.tar.gz

# Deployment
sudo ./deploy-python.sh deploy schulbuddy-python-package.tar.gz
```

### Systemd Service

Der Python-Deployment-Script erstellt automatisch einen systemd Service:

```bash
# Service-Status
sudo systemctl status schulbuddy

# Logs anzeigen
sudo journalctl -u schulbuddy -f

# Service neustarten
sudo systemctl restart schulbuddy
```

## 🔄 CI/CD Workflow

### Automatische Deployments

**Development Workflow:**
1. Push zu `dev` Branch
2. GitHub Actions läuft automatisch
3. Tests werden ausgeführt
4. Docker Image wird gebaut
5. Deployment zu Staging-Umgebung

**Production Workflow:**
1. Pull Request zu `main`
2. Code Review und Approval
3. Merge zu `main`
4. GitHub Actions läuft
5. Security-Scans
6. Deployment zu Production (mit Approval)

**Release Workflow:**
1. Tag erstellen: `git tag v1.0.0`
2. Tag pushen: `git push origin v1.0.0`
3. GitHub Actions erstellt automatisch Release
4. Docker Image und Python Package verfügbar

### Branch-Strategie

```
main ──┬── v1.0.0 (Release Tag)
       │
       ├── feature/new-feature
       │
dev ───┴── hotfix/critical-fix
```

## 📦 Verfügbare Artefakte

### Docker Images
```bash
# Latest von main branch
docker pull ghcr.io/username/schulbuddy:main

# Latest von dev branch
docker pull ghcr.io/username/schulbuddy:dev

# Specific version
docker pull ghcr.io/username/schulbuddy:v1.0.0
```

### Python Packages
```bash
# Von GitHub Releases
wget https://github.com/username/schulbuddy/releases/download/v1.0.0/schulbuddy-python-package.tar.gz

# Entpacken und installieren
tar -xzf schulbuddy-python-package.tar.gz
cd schulbuddy
pip install -r requirements-frozen.txt
python app.py
```

## 🔧 Lokale Entwicklung

### Mit Docker
```bash
git clone https://github.com/username/schulbuddy.git
cd schulbuddy

# Development starten
./start.sh dev      # Linux/Mac
.\start.ps1 dev     # Windows
```

### Ohne Docker
```bash
git clone https://github.com/username/schulbuddy.git
cd schulbuddy

# Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# .env bearbeiten

# App starten
python app.py
```

## 🛠️ Troubleshooting

### GitHub Actions Fehler

**1. Docker Build Fehler:**
```bash
# Lokal testen
docker build -t schulbuddy:test .
docker run -p 5000:5000 schulbuddy:test
```

**2. Python Test Fehler:**
```bash
# Lokal testen
python -m pytest
flake8 .
black --check .
```

**3. Deployment Fehler:**
```bash
# Logs prüfen
./deploy-docker.sh logs
./deploy-python.sh logs

# Status prüfen
./deploy-docker.sh status
./deploy-python.sh status
```

### Häufige Probleme

**Permission Denied:**
```bash
# Scripts ausführbar machen
chmod +x deployment/*.sh
chmod +x start.sh
```

**GitHub Token Permissions:**
- Repository: Read/Write
- Packages: Write
- Actions: Write

**SSL/TLS Zertifikate:**
```bash
# Let's Encrypt mit Certbot
sudo certbot --nginx -d your-domain.com
```

## 📋 Monitoring und Wartung

### Health Checks
```bash
# Docker
curl http://localhost:5000/health

# Mit Scripts
./deploy-docker.sh status
./deploy-python.sh status
```

### Backup-Strategien

**Automatische Backups (Crontab):**
```bash
# Täglich um 2 Uhr
0 2 * * * /opt/schulbuddy/deploy-python.sh backup

# Wöchentlich alte Backups löschen
0 3 * * 0 find /opt/schulbuddy/backups -name "*.db" -mtime +30 -delete
```

### Log-Rotation
```bash
# Logrotate Konfiguration
sudo tee /etc/logrotate.d/schulbuddy <<EOF
/var/log/schulbuddy/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 schulbuddy schulbuddy
}
EOF
```

## 🎯 Best Practices

### Security
1. **Secrets Management** - Niemals Secrets in Code
2. **Image Scanning** - Automatische Vulnerability Scans
3. **HTTPS Only** - SSL/TLS in Produktion
4. **Regular Updates** - Dependencies aktuell halten

### Performance
1. **Multi-Stage Builds** - Kleinere Docker Images
2. **Caching** - Build-Cache nutzen
3. **CDN** - Statische Assets über CDN
4. **Database** - PostgreSQL für Produktion

### Monitoring
1. **Health Checks** - Regelmäßige Verfügbarkeitsprüfung
2. **Metrics** - Prometheus/Grafana
3. **Alerting** - Notification bei Problemen
4. **Backup Verification** - Backup-Integrität prüfen

---

**🎓 Viel Erfolg mit SchulBuddy auf GitHub!**

Bei Fragen oder Problemen erstelle ein Issue im Repository oder nutze die GitHub Discussions.
