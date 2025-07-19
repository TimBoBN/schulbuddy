# SchulBuddy Docker Setup

**SchulBuddy** - Eine Flask-Anwendung für die Verwaltung von Schulaufgaben, Noten und Lernfortschritt.

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy
```

### 2. Setup und Konfiguration
**Linux/Mac:**
```bash
./start.sh setup
```

**Windows (PowerShell):**
```powershell
.\start.ps1 setup
```

Bearbeite die `.env` Datei und setze mindestens:
- `SECRET_KEY`: Ein sicherer, zufälliger Schlüssel ⚠️ **Unbedingt ändern!**
- `PORT`: Der Port auf dem die Anwendung läuft (Standard: 5000)
- `CURRENT_SCHOOL_YEAR`: Das aktuelle Schuljahr (z.B. 2024/25)

### 3. Starten

**Development:**
```bash
./start.sh dev       # Linux/Mac
.\start.ps1 dev      # Windows
```

**Produktion:**
```bash
./start.sh up        # Linux/Mac
.\start.ps1 up       # Windows
```

Die Anwendung ist dann erreichbar unter: `http://localhost:[PORT]`

## 📚 Dokumentation

- **[🚀 Deployment Guide](docs/DEPLOYMENT.md)** - Vollständige Deployment-Optionen
- **[🔧 Entwicklung](docs/DEVELOPMENT.md)** - Development Setup und Workflows
- **[🐳 Docker Guide](docs/DOCKER.md)** - Docker-spezifische Konfiguration
- **[🔍 Troubleshooting](docs/TROUBLESHOOTING.md)** - Problemlösung und Debugging
- **[🤖 CI/CD](docs/CICD.md)** - GitHub Actions und automatische Deployments
- **[⚙️ Konfiguration](docs/CONFIGURATION.md)** - Umgebungsvariablen und Einstellungen

## 📋 Verfügbare Kommandos

| Kommando | Linux/Mac | Windows | Beschreibung |
|----------|-----------|---------|--------------|
| Setup | `./start.sh setup` | `.\start.ps1 setup` | Erstelle .env Datei |
| Development | `./start.sh dev` | `.\start.ps1 dev` | Starte mit Hot-Reload |
| Produktion | `./start.sh up` | `.\start.ps1 up` | Starte Produktionsumgebung |
| Stoppen | `./start.sh down` | `.\start.ps1 down` | Stoppe alle Container |
| Status | `./start.sh status` | `.\start.ps1 status` | Container Status anzeigen |
| Health-Check | `./start.sh health` | `.\start.ps1 health` | Anwendungsstatus prüfen |
| Backup | `./start.sh backup` | `.\start.ps1 backup` | Datenbank und Uploads sichern |

## 🎯 Deployment-Optionen

| Methode | Schwierigkeit | Empfehlung |
|---------|---------------|------------|
| 🐳 **Docker Container** | ⭐ Einfach | Für Produktion und schnellen Start |
| 🐍 **Python Direkt** | ⭐⭐ Mittel | Für Development und Anpassungen |
| 🤖 **GitHub Actions** | ⭐⭐⭐ Automatisch | Für CI/CD und automatische Deployments |

## 🆘 Schnelle Hilfe

**Problem mit Port 5000?**
```bash
# .env bearbeiten und PORT=8080 setzen
```

**Container starten nicht?**
```bash
./start.sh status    # Status prüfen
./start.sh clean     # Aufräumen
./start.sh build     # Neu bauen
```

**Mehr Hilfe:** Siehe [Troubleshooting Guide](docs/TROUBLESHOOTING.md)

## 📝 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.
