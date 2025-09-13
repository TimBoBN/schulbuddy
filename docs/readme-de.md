# 🎓 SchulBuddy - Multi-Architecture Docker Edition

Ein modernes Schulmanagementsystem mit Docker-Support für einfache Bereitstellung auf AMD64 und ARM-Systemen.

[![Docker Multi-Platform Build](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml/badge.svg)](https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml)

## 🚀 Quick Start

### Option 1: Schnellstart mit curl (empfohlen)

```bash
# 1. Konfigurationsdatei herunterladen
curl -o .env https://raw.githubusercontent.com/TimBoBN/schulbuddy/main/config/.env.example

# 2. Wichtige Einstellungen anpassen
nano .env  # Ändere mindestens SECRET_KEY!

# 3. Container starten (automatische Architektur-Erkennung!)
docker-compose up -d

# 4. Öffne http://localhost:5000
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
├── 📁 config/                   # Konfigurationsdateien
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
│   ├── setup-env.sh            # Environment Setup (Bash)
├── 📄 app.py                    # Haupt-Flask-Anwendung
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
```

## 🚀 Schnellstart (Docker Images)

```bash
# Produktionsversion (latest)
docker pull timbobn/schulbuddy:latest
# Entwicklungsversion
docker pull timbobn/schulbuddy:dev
# Spezifische Version
docker pull timbobn/schulbuddy:v1.2.3
```

Weitere Details siehe: [docs/DOCKER_README.md](./DOCKER_README.md), [docs/MULTI-ARCH-README.md](./MULTI-ARCH-README.md), [docs/SECURITY.md](./SECURITY.md).

## 🔧 Entwicklung

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
python init_db.py
python app.py
```

## 📝 Lizenz

MIT – siehe [LICENSE](../LICENSE).
