# 🐳 Docker Guide

Umfassende Dokumentation für Docker-basierte Setups von SchulBuddy.

## 🏗️ Docker-Architektur

### Container-Struktur

```
┌─────────────────────────────────────┐
│ SchulBuddy Application Container    │
├─────────────────────────────────────┤
│ • Flask Application (Port 5000)     │
│ • Gunicorn WSGI Server              │
│ • Python 3.11 Alpine                │
│ • SQLite Database                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Nginx Reverse Proxy (Optional)      │
├─────────────────────────────────────┤
│ • HTTP/HTTPS Termination            │
│ • Static File Serving               │
│ • Load Balancing                    │
└─────────────────────────────────────┘
```

## 📁 Docker Files

### Dockerfile
Haupt-Container Image für SchulBuddy:

```dockerfile
FROM python:3.11-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### docker-compose.yml
Standard Entwicklungs-Setup:

```yaml
version: '3.8'
services:
  schulbuddy:
    build: .
    ports:
      - "${PORT:-5000}:5000"
    environment:
      - FLASK_ENV=${FLASK_ENV:-production}
    volumes:
      - ./instance:/app/instance
      - ./static/uploads:/app/static/uploads
    env_file: .env
```

### docker-compose.prod.yml
Produktions-Setup mit Gunicorn:

```yaml
version: '3.8'
services:
  schulbuddy:
    build: .
    command: ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
    ports:
      - "${PORT:-5000}:5000"
    volumes:
      - schulbuddy_data:/app/instance
      - schulbuddy_uploads:/app/static/uploads
    env_file: .env
    restart: unless-stopped

volumes:
  schulbuddy_data:
  schulbuddy_uploads:
```

## 🔧 Docker Compose Profiles

### Standard Profile
```bash
docker-compose up -d
```

### Mit Nginx
```bash
docker-compose --profile with-nginx up -d
```

### Produktionsumgebung
```bash
docker-compose -f docker-compose.prod.yml --profile production up -d
```

## 💾 Volumes und Persistierung

### Named Volumes (Empfohlen für Produktion)

**Vorteile:**
- Automatisches Management durch Docker
- Bessere Performance
- Plattformunabhängig

```yaml
volumes:
  schulbuddy_data:
    driver: local
  schulbuddy_uploads:
    driver: local
```

### Bind Mounts (Gut für Development)

**Vorteile:**
- Direkter Zugriff auf Dateien
- Live-Editing möglich
- Einfaches Backup

```yaml
volumes:
  - ./instance:/app/instance
  - ./static/uploads:/app/static/uploads
```

## 🌐 Netzwerk-Konfiguration

### Port-Mapping
```yaml
ports:
  - "5000:5000"    # Standard
  - "8080:5000"    # Custom Port
  - "${PORT:-5000}:5000"  # Environment Variable
```

### Custom Networks
```yaml
networks:
  schulbuddy-net:
    driver: bridge

services:
  schulbuddy:
    networks:
      - schulbuddy-net
```

## 🔄 Multi-Stage Builds

### Optimiertes Dockerfile

```dockerfile
# Build Stage
FROM python:3.11-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production Stage  
FROM python:3.11-alpine
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🏥 Health Checks

### Container Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

### Docker Compose Health Check

```yaml
services:
  schulbuddy:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 🐛 Debugging

### Container Logs

```bash
# Alle Logs
docker-compose logs

# Nur App Logs
docker-compose logs schulbuddy

# Live Logs folgen
docker-compose logs -f

# Letzten 100 Zeilen
docker-compose logs --tail=100
```

### Container Shell

```bash
# Shell im laufenden Container
docker-compose exec schulbuddy bash

# Neuen Container für Debugging
docker run -it --rm schulbuddy:latest bash
```

### Debug Modus

```yaml
# docker-compose.debug.yml
services:
  schulbuddy:
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: ["python", "app.py"]
    ports:
      - "5000:5000"
      - "5678:5678"  # Debug Port
```

## 🧹 Wartung und Cleanup

### Images aufräumen

```bash
# Nicht verwendete Images
docker image prune

# Alle nicht verwendeten Ressourcen
docker system prune -a

# Volumes aufräumen
docker volume prune
```

### Container Updates

```bash
# Images neu bauen
docker-compose build --no-cache

# Container neu starten
docker-compose up -d --force-recreate
```

## 📊 Monitoring

### Container Ressourcen

```bash
# Container Statistiken
docker stats

# Container Prozesse
docker-compose top
```

### Prometheus Integration

```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## 🔐 Sicherheit

### Non-Root User

```dockerfile
RUN addgroup -g 1001 -S schulbuddy && \
    adduser -S -D -H -u 1001 -s /sbin/nologin -G schulbuddy schulbuddy
USER schulbuddy
```

### Security Scanning

```bash
# Vulnerability Scan
docker scan schulbuddy:latest

# Container Audit
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image schulbuddy:latest
```
