# 🎓 SchulBuddy - Docker Edition

Ein modernes Schulmanagementsystem mit Docker-Support für einfache Bereitstellung, Verwaltung und kontinuierliche Auslieferung.

[![Docker Build and Push to GHCR](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-ghcr-publish.yml/badge.svg)](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-ghcr-publish.yml)
[![Docker Hub Publish](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-hub-publish.yml/badge.svg)](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-hub-publish.yml)

## 📁 Projektstruktur

```
schulbuddy/
├── 📄 app.py                    # Haupt-Flask-Anwendung
├── 📄 config.py                 # Konfigurationsverwaltung
├── 📄 models.py                 # Datenbankmodelle
├── 📄 wsgi.py                   # WSGI-Einstiegspunkt für Produktionsserver
├── 📄 api_security.py           # API-Sicherheitsimplementierung
├── 📄 requirements.txt          # Python-Abhängigkeiten
├── 🐳 Dockerfile                # Docker-Container-Definition
├── 🐳 docker-compose.yml        # Service-Orchestrierung
├── 📄 gunicorn.conf.py          # Gunicorn-Konfiguration
├── 📄 entrypoint.sh             # Container-Einstiegsskript
├── 📄 Makefile                  # Build-Automatisierung
├── 📁 .github/workflows/        # CI/CD Workflows
│   ├── docker-ghcr-publish.yml  # GitHub Container Registry Workflow
│   └── docker-hub-publish.yml   # Docker Hub Workflow
├── 📁 config/                   # Konfigurationsdateien
│   ├── .env.example             # Umgebungsvariablen-Vorlage
│   ├── .env.template            # Alternative Vorlage
│   └── nginx.conf               # Nginx-Konfiguration
├── 📁 scripts/                  # Setup- und Hilfsskripte
│   ├── setup-env.ps1            # Windows Setup-Skript
│   └── setup-env.sh             # Linux/Mac Setup-Skript
├── 📁 routes/                   # Flask-Routen
│   ├── admin.py                 # Admin-Routen
│   ├── auth.py                  # Authentifizierungs-Routen
│   ├── grades.py                # Noten-Verwaltung
│   └── ... und weitere
├── 📁 static/                   # Statische Dateien (CSS, JS)
├── 📁 templates/                # HTML-Templates
├── 📁 instance/                 # Lokale Datenbankdateien
└── 📁 utils/                    # Hilfsfunktionen und Utilities
```

## 🚀 Schnellstart

### Methode 1: Mit fertigen Docker Images (empfohlen)

#### 1. Docker Images verwenden

Es stehen vorgefertigte Docker Images zur Verfügung, die automatisch via GitHub Actions gebaut werden:

**Docker Hub**:
```bash
# Produktionsversion (latest)
docker pull timbobn/schulbuddy:latest

# Entwicklungsversion
docker pull timbobn/schulbuddy:dev

# Spezifische Version
docker pull timbobn/schulbuddy:v1.2.3
```

**GitHub Container Registry (GHCR)**:
```bash
# Produktionsversion (latest)
docker pull ghcr.io/timbobn/schulbuddy:latest

# Entwicklungsversion
docker pull ghcr.io/timbobn/schulbuddy:dev

# Spezifische Version
docker pull ghcr.io/timbobn/schulbuddy:v1.2.3
```

#### 2. docker-compose.yml herunterladen

```bash
# Eine einzelne Datei mit curl herunterladen
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/docker-compose.yml

# Oder das Repository klonen für alle Konfigurationen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

#### 3. Anwendung starten

```bash
# Produktionsversion
TAG=latest docker-compose up -d

# Entwicklungsversion
TAG=dev docker-compose up -d

# Spezifische Version
TAG=v1.2.3 docker-compose up -d

# Für GHCR image: Zeile in docker-compose.yml anpassen
```

### Methode 2: Lokaler Build

#### 1. Repository klonen
```bash
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

#### 2. Umgebung konfigurieren
```bash
# Windows
.\scripts\setup-env.ps1

# Linux/Mac
bash scripts/setup-env.sh
```

#### 3. Anwendung bauen und starten
```bash
# Mit Makefile (empfohlen)
make install

# Oder manuell
docker-compose up --build -d
```

### 4. Anwendung aufrufen
- Öffne deinen Browser
- Gehe zu `http://localhost:5000` (oder deinen konfigurierten Port)
- Standard-Login: admin / schulbuddy (bitte ändern!)

## 🛠️ Verfügbare Befehle

```bash
make help         # Zeige alle verfügbaren Befehle
make setup        # Konfiguriere Umgebungsvariablen
make build        # Baue Docker Images
make start        # Starte Services
make stop         # Stoppe Services
make restart      # Neustart der Services
make logs         # Zeige Logs
make status       # Zeige Service-Status
make clean        # Lösche Container und Volumes
make install      # Vollständige Installation
make update       # Update auf neueste Version
```

## ⚙️ Konfiguration

### Umgebungsvariablen (.env)

```env
# Docker Image Konfiguration
TAG=latest  # latest (Produktion), dev (Entwicklung), v1.2.3 (spezifische Version)

# Server-Konfiguration
HOST=0.0.0.0
PORT=5000
EXTERNAL_PORT=5000

# Flask-Konfiguration
FLASK_ENV=production
SECRET_KEY=your-secret-key
DOCKER_ENV=1

# Datenbank
DATABASE_URL=sqlite:////app/data/schulbuddy.db

# Sicherheit
SESSION_TIMEOUT_MINUTES=120
REMEMBER_COOKIE_DAYS=30
LOGIN_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_TIMEOUT_MINUTES=15

# Schuljahr-Konfiguration
CURRENT_SCHOOL_YEAR=2025/26
CURRENT_SEMESTER=1
```

### Port-Konfiguration

Die Anwendung unterstützt flexible Port-Konfiguration:

- `PORT`: Interner Container-Port (Standard: 5000)
- `EXTERNAL_PORT`: Externer Port für den Zugriff (Standard: gleich PORT)
- `HOST`: Bind-Adresse (Standard: 0.0.0.0)

### Docker-Image-Varianten

- **latest**: Produktions-/Stable-Version (main-Branch)
- **dev**: Entwicklungsversion mit neuesten Features (dev-Branch)
- **vX.Y.Z**: Spezifische Versionen (Tags)

## 📖 Erweiterte Dokumentation

- [📚 Docker-Anleitung](docs/DOCKER_README.md)
- [🔧 Setup-Anleitung](docs/SETUP_README.md)
- [🌐 Port-Konfiguration](docs/PORT_CONFIG.md)

## 🔧 Entwicklung

### Lokale Entwicklung
```bash
# Python Virtual Environment erstellen
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py
python init_school_settings.py

# Entwicklungsserver starten
python app.py
```

### Docker Development
```bash
# Development Image verwenden
TAG=dev docker-compose up -d

# Oder lokalen Build für Entwicklung verwenden
docker-compose -f docker-compose.yml up --build -d

# Logs verfolgen
docker-compose logs -f schulbuddy
```

### Kontinuierliche Integration/Deployment

Das Projekt verwendet GitHub Actions für automatisierte Builds und Deployment:

- **Docker Hub Publish**: Baut und veröffentlicht Images bei Änderungen an `main`, `dev` oder bei Tag-Pushes
- **GHCR Publish**: Baut und veröffentlicht Images in der GitHub Container Registry

Die Workflows sind so konfiguriert, dass:
- Pushes zum `main`-Branch den `latest` Tag aktualisieren
- Pushes zum `dev`-Branch den `dev` Tag aktualisieren
- Tag-Pushes (v*) entsprechende Versions-Tags erstellen

## 🗄️ Datenbank

- **Typ**: SQLite
- **Lokation**: `instance/schulbuddy.db` (lokal) oder `/app/data/schulbuddy.db` (Docker)
- **Persistenz**: Docker Volumes sorgen für Datenpersistenz
- **Backup**: Automatische Volume-Sicherung möglich
- **Initialisierung**: Automatisch beim ersten Start des Containers

## 🔒 Sicherheit

- **Sichere Session-Verwaltung**: Konfigurierbare Session-Timeouts
- **Passwort-Hashing**: Sichere Hashing-Algorithmen für Passwörter
- **2FA-Unterstützung**: Zwei-Faktor-Authentifizierung mit TOTP
- **Backup-Codes**: Fallback bei Geräteverlust
- **API-Schlüssel**: Sichere API-Authentifizierung mit individuellen Tokens
- **Rate Limiting**: Schutz vor Brute-Force-Angriffen
- **CSRF-Schutz**: Integrierter Schutz gegen Cross-Site Request Forgery
- **Regelmäßige Sicherheitsupdates**: Automatische CVE-Überwachung und Abhängigkeits-Updates

## 🚀 Deployment

### Produktionsdeployment
```bash
# Schnellstart mit fertigen Images
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example
mv .env.example .env
# .env Datei anpassen

# Services starten
TAG=latest docker-compose up -d

# Optional: Nginx Reverse Proxy
TAG=latest docker-compose --profile nginx up -d
```

### Bereitstellungsoptionen

1. **Standalone Docker**: Einfache Installation mit Docker Compose
2. **Kubernetes**: Kubernetes-Deployment mit Helm Charts (siehe `/k8s`)
3. **Platform-as-a-Service**: Vorgefertigte Docker-Images für Plattformen wie Heroku oder Render

### Monitoring
```bash
# Service-Status prüfen
make status

# Logs anzeigen
make logs

# Ressourcenverbrauch
docker stats schulbuddy-app

# Health-Check
curl http://localhost:5000/health
```

### Docker Health-Checks

Das Image enthält eingebaute Health-Checks, die automatisch den Status der Anwendung überwachen und bei Problemen Neustarts auslösen können.

## � Updates und Versionen

### Versionshistorie

- **v1.3.0** (August 2025): Container-Registry-Support, Sicherheitsverbesserungen
- **v1.2.0** (Juli 2025): Automatisierte CI/CD-Pipeline, Schuljahreswechsel
- **v1.1.0** (Mai 2025): Statistik-Modul, Export-Funktionen
- **v1.0.0** (März 2025): Erste stabile Veröffentlichung

### Aktualisierung

```bash
# Für Docker-Hub-Installation
docker-compose pull
docker-compose up -d

# Oder mit spezifischem Tag
TAG=v1.3.0 docker-compose up -d
```

## �📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz - siehe [LICENSE](LICENSE) für Details.

## 🤝 Beitrag leisten

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

Jeder Beitrag wird geschätzt!

## 📞 Support

Bei Fragen oder Problemen:

1. Prüfe die [Dokumentation](docs/)
2. Schaue in die [Issues](../../issues)
3. Erstelle ein neues Issue mit detaillierter Beschreibung

---

*Erstellt mit ❤️ für eine bessere Schulverwaltung*
