# 🎓 SchulBuddy - Multi-Architecture Docker Edition

Ein modernes Schulmanagementsystem
```
schulbuddy/
├── 📁 config/                   # Konfigurationsdateien
│   ├── .env.example            # Environment-Variablen Vorlage
│   ├── .env.template           # Alternative Vorlage
│   └── nginx.conf              # Nginx Konfiguration
├── 📁 docs/                     # Dokumentation
│   ├── ARM_SUPPORT.md          # ARM-Support Details
│   ├── DOCKER_README.md        # Docker Setup Guide
│   ├── INDEX.md                # Dokumentations-Index
│   ├── MULTI-ARCH-README.md    # Multi-Architecture Guide
│   └── SECURITY.md             # Sicherheitsrichtlinien
├── 📁 scripts/                  # Utility Scripts
│   ├── build-multiarch.ps1     # Multi-Arch Build (PowerShell)
│   ├── build-multiarch.sh      # Multi-Arch Build (Bash)
│   ├── setup-env.ps1           # Environment Setup (PowerShell)
│   ├── setup-env.sh            # Environment Setup (Bash)
│   ├── trigger-multiplatform.ps1 # Workflow Trigger (PowerShell)
│   └── trigger-multiplatform.sh  # Workflow Trigger (Bash)
├── 📄 app.py                    # Haupt-Flask-Anwendung
├── 📄 config.py                 # Konfigurationsverwaltung
├── 📄 models.py                 # Datenbankmodellee Docker-Support für einfache Bereitstellung auf AMD64 und ARM-Systemen.

```
[![Docker Multi-Platform Build](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml/badge.svg)](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml)

## 🚀 Quick Start

### Option 1: Schnellstart mit curl (empfohlen)

```bash
# 1. Konfigurationsdatei herunterladen
curl -o docker-compose.yml https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/docker-compose.multiplatform.yml

# 2. .env herunterladen
curl -o .env https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example

# 3. Wichtige Einstellungen anpassen
nano .env  # Ändere mindestens SECRET_KEY!

# 4. Container starten (automatische Architektur-Erkennung!)
docker-compose up -d

# 5. Öffne http://localhost:5000
```

### Option 2: Manueller Start

```bash
# 1. Repository klonen (optional)
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# 2. Konfiguration kopieren
cp config/.env.example .env

# 3. Anpassen und starten
nano .env
docker-compose up -d
```

### 🎯 Verschiedene Versionen

```bash
# Produktionsversion (main branch)
docker pull timbobn/schulbuddy:latest

# Entwicklungsversion (dev branch) 
docker pull timbobn/schulbuddy:dev

# Spezifische Version
docker pull timbobn/schulbuddy:v1.2.0
```

## 🏗️ Multi-Architecture Support

SchulBuddy unterstützt automatisch:
- **AMD64**: Normale PCs, Server (4 Gunicorn Worker)
- **ARM**: Raspberry Pi, Apple M1/M2 (2 Gunicorn Worker)

Docker wählt automatisch die richtige Architektur für dein System!

## ⚙️ Konfiguration (.env Datei)

### Automatisch herunterladen:
```bash
curl -o .env https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example
```

### Wichtigste Einstellungen:

```bash
# 🔐 WICHTIG: Ändere den Secret Key!
SECRET_KEY=dein-sehr-sicherer-geheimer-schluessel-hier

# 🏫 Schuleinstellungen
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1

# 🌐 Server
PORT=5000
EXTERNAL_PORT=5000

# 🐳 Docker Image Version  
TAG=latest  # oder 'dev' für Entwicklungsversion
```

### Vollständige .env Optionen:
- **Sicherheit**: `SECRET_KEY`, Session-Timeouts, Login-Limits
- **Schule**: Schuljahr, Semester
- **Performance**: Worker-Anzahl (automatisch), Timeouts
- **Docker**: Image-Tags, Registries

## 📁 Projektstruktur

```
schulbuddy/
├── � config/                   # Konfigurationsdateien
│   ├── .env.example            # Environment-Variablen Vorlage
│   ├── .env.template           # Alternative Vorlage
│   └── nginx.conf              # Nginx Konfiguration
├── 📁 docs/                     # Dokumentation
│   ├── ARM_SUPPORT.md          # ARM-Support Details
│   ├── DOCKER_README.md        # Docker Setup Guide
│   ├── MULTI-ARCH-README.md    # Multi-Architecture Guide
│   └── SECURITY.md             # Sicherheitsrichtlinien
├── 📁 scripts/                  # Utility Scripts
│   ├── build-multiarch.ps1     # Multi-Arch Build (PowerShell)
│   ├── build-multiarch.sh      # Multi-Arch Build (Bash)
│   ├── setup-env.ps1           # Environment Setup (PowerShell)
│   └── setup-env.sh            # Environment Setup (Bash)
├── �📄 app.py                    # Haupt-Flask-Anwendung
├── 📄 config.py                 # Konfigurationsverwaltung
├── 📄 models.py                 # Datenbankmodelle
├── 📄 wsgi.py                   # WSGI-Einstiegspunkt
├── 📄 api_security.py           # API-Sicherheit
├── 📄 requirements.txt          # Python-Abhängigkeiten
├── 🐳 Dockerfile                # AMD64 Container
├── 🐳 Dockerfile.arm            # ARM Container
├── 🐳 docker-compose.yml        # Service-Orchestrierung
├── 📄 entrypoint.sh             # Container Startup
└── 📄 gunicorn.conf.py          # Gunicorn-Konfiguration
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

### Unterstützte Architekturen

Alle unsere Docker Images unterstützen folgende Plattformen:
- **linux/amd64**: Standard x86_64 (Intel/AMD)
- **linux/arm64**: 64-bit ARM (z.B. Apple Silicon, Raspberry Pi 4 64-bit)
- **linux/arm/v7**: 32-bit ARM (z.B. Raspberry Pi 2/3)

## 📖 Erweiterte Dokumentation

- [🔒 Sicherheitsrichtlinie & CVE-Übersicht](SECURITY.md)
- [🐳 Docker-Anleitung](docs/DOCKER_README.md)
- [🏠 Vollständige Dokumentation](docs/INDEX.md)

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
- **Container-Sicherheit**: Least-Privilege-Prinzip, non-root User, minimierte Angriffsfläche
- **Schwachstellenmanagement**: Dokumentierte Risikobewertung für nicht-fixbare CVEs in [SECURITY.md](SECURITY.md)

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

## 🔄 Updates und Versionen

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

## 📝 Lizenz

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

1. **Vollständige Dokumentation**: [docs/INDEX.md](docs/INDEX.md)
2. **Multi-Architecture Guide**: [docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md)
3. **Docker Setup**: [docs/DOCKER_README.md](docs/DOCKER_README.md)
4. **Sicherheit**: [docs/SECURITY.md](docs/SECURITY.md)
5. **ARM Support**: [docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md)
6. **GitHub Issues**: [Issues](../../issues)

## 📚 Dokumentationsübersicht

| Thema | Datei | Beschreibung |
|-------|-------|--------------|
| 🏠 **Hauptindex** | [docs/INDEX.md](docs/INDEX.md) | Übersicht aller Dokumentation |
| 🏗️ **Multi-Arch** | [docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md) | AMD64 & ARM Support |
| 🐳 **Docker Setup** | [docs/DOCKER_README.md](docs/DOCKER_README.md) | Detaillierte Installation |
| 🛡️ **Sicherheit** | [docs/SECURITY.md](docs/SECURITY.md) | Sicherheitsrichtlinien |
| 🔋 **ARM Support** | [docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md) | Raspberry Pi & Apple Silicon |

---

*Erstellt mit ❤️ für eine bessere Schulverwaltung*
