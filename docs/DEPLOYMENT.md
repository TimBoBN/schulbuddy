# 🚀 Deployment Guide

Detaillierte Anleitung für verschiedene Deployment-Szenarien von SchulBuddy.

## 📦 Docker Container (Empfohlen)

### Standard Deployment

```bash
# Setup
./start.sh setup
# .env Datei bearbeiten
./start.sh up
```

### Mit Nginx Reverse Proxy

```bash
./start.sh nginx
```

### Produktionsumgebung mit Gunicorn

```bash
./start.sh prod
```

### Von GitHub Container Registry

```bash
# Latest Version
docker pull ghcr.io/timbobn/schulbuddy:main
docker run -d -p 8080:5000 --env-file .env ghcr.io/timbobn/schulbuddy:main

# Specific Version  
docker pull ghcr.io/timbobn/schulbuddy:v1.0.0
```

## 🐍 Python Direct Installation

### Voraussetzungen
- Python 3.9+
- pip
- virtualenv (empfohlen)

### Installation

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py

# Starten
python app.py
```

## 🌐 Server Deployment

### VPS/Dedicated Server

```bash
# SSH zum Server
ssh user@your-server.com

# Repository klonen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# Setup ausführen
./start.sh setup
# .env anpassen
./start.sh prod
```

### Docker Compose für Server

```yaml
# docker-compose.server.yml
version: '3.8'
services:
  schulbuddy:
    image: ghcr.io/timbobn/schulbuddy:main
    ports:
      - "80:5000"
    env_file: .env
    volumes:
      - ./instance:/app/instance
      - ./static/uploads:/app/static/uploads
    restart: unless-stopped
```

## 🔐 SSL/HTTPS Setup

### Mit Nginx und Let's Encrypt

```bash
# Nginx installieren
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# SchulBuddy mit Nginx starten
./start.sh nginx

# SSL Zertifikat erstellen
sudo certbot --nginx -d your-domain.com
```

### Nginx Konfiguration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🤖 Automatisierte Deployments

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy SchulBuddy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Server
        run: |
          ssh ${{ secrets.SSH_USER }}@${{ secrets.SSH_HOST }} \
          "cd /app/schulbuddy && git pull && ./start.sh restart"
```

## 💾 Persistente Daten

### Named Volumes (Produktion)
```yaml
volumes:
  - schulbuddy_data:/app/instance
  - schulbuddy_uploads:/app/static/uploads
```

### Bind Mounts (Development)
```yaml
volumes:
  - ./instance:/app/instance
  - ./static/uploads:/app/static/uploads
```

## 🔄 Updates und Wartung

### Docker Images aktualisieren

```bash
./start.sh update
```

### Manual Update

```bash
# Container stoppen
./start.sh down

# Images aktualisieren  
docker pull ghcr.io/timbobn/schulbuddy:main

# Container neu starten
./start.sh up
```

### Backup vor Updates

```bash
./start.sh backup
```

## 🌍 Environment-spezifische Konfiguration

### Development
```env
FLASK_ENV=development
PORT=5000
DEBUG=true
```

### Staging
```env
FLASK_ENV=production
PORT=8080
DEBUG=false
```

### Production
```env
FLASK_ENV=production
PORT=80
DEBUG=false
SESSION_COOKIE_SECURE=true
```
