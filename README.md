# 🎓 SchulBuddy - Docker Edition

Ein modernes Schulmanagementsystem mit Docker-Support für einfache Bereitstellung und Verwaltung.

## 📁 Projektstruktur

```
schulbuddy/
├── 📄 app.py                    # Haupt-Flask-Anwendung
├── 📄 config.py                 # Konfigurationsverwaltung
├── 📄 models.py                 # Datenbankmodelle
├── 📄 requirements.txt          # Python-Abhängigkeiten
├── 🐳 Dockerfile               # Docker-Container-Definition
├── 🐳 docker-compose.yml       # Service-Orchestrierung
├── 📄 Makefile                 # Build-Automatisierung
├── 📁 config/                  # Konfigurationsdateien
│   ├── .env.example            # Umgebungsvariablen-Vorlage
│   ├── .env.template           # Alternative Vorlage
│   └── nginx.conf              # Nginx-Konfiguration
├── 📁 docs/                    # Dokumentation
│   ├── DOCKER_README.md        # Docker-Anleitung
│   ├── PORT_CONFIG.md          # Port-Konfiguration
│   └── SETUP_README.md         # Setup-Anleitung
├── 📁 scripts/                 # Setup- und Hilfsskripte
│   ├── setup-env.ps1           # Windows Setup-Skript
│   ├── setup-env.sh            # Linux/Mac Setup-Skript
│   └── entrypoint.sh           # Docker-Entrypoint
├── 📁 routes/                  # Flask-Routen
├── 📁 static/                  # Statische Dateien (CSS, JS)
├── 📁 templates/               # HTML-Templates
└── 📁 instance/                # Lokale Datenbankdateien
```

## 🚀 Schnellstart

### 1. Repository klonen
```bash
git clone <repository-url>
cd schulbuddy
```

### 2. Umgebung konfigurieren
```bash
# Windows
.\scripts\setup-env.ps1

# Linux/Mac
bash scripts/setup-env.sh
```

### 3. Anwendung starten
```bash
# Mit Makefile (empfohlen)
make install

# Oder manuell
docker-compose up --build -d
```

### 4. Anwendung aufrufen
- Öffne deinen Browser
- Gehe zu `http://localhost:5000` (oder deinen konfigurierten Port)

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
MAX_LOGIN_ATTEMPTS=5
```

### Port-Konfiguration

Die Anwendung unterstützt flexible Port-Konfiguration:

- `PORT`: Interner Container-Port (Standard: 5000)
- `EXTERNAL_PORT`: Externer Port für den Zugriff (Standard: gleich PORT)
- `HOST`: Bind-Adresse (Standard: 0.0.0.0)

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

# Entwicklungsserver starten
python app.py
```

### Docker Development
```bash
# Development Build
docker-compose -f docker-compose.yml up --build

# Logs verfolgen
docker-compose logs -f schulbuddy
```

## 🗄️ Datenbank

- **Typ**: SQLite
- **Lokation**: `instance/schulbuddy.db` (lokal) oder `/app/data/schulbuddy.db` (Docker)
- **Persistenz**: Docker Volumes sorgen für Datenpersistenz
- **Backup**: Automatische Volume-Sicherung möglich

## 🔒 Sicherheit

- Sichere Session-Verwaltung
- Passwort-Hashing mit bcrypt
- 2FA-Unterstützung
- API-Schlüssel-Authentifizierung
- Rate Limiting für Login-Versuche

## 🚀 Deployment

### Produktionsdeployment
```bash
# Umgebung für Produktion konfigurieren
cp config/.env.example .env
# .env Datei anpassen

# Services starten
docker-compose up -d

# Optional: Nginx Reverse Proxy
docker-compose --profile nginx up -d
```

### Monitoring
```bash
# Service-Status prüfen
make status

# Logs anzeigen
make logs

# Ressourcenverbrauch
docker stats schulbuddy-app
```

## 📝 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

## 🤝 Beitrag leisten

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

## 📞 Support

Bei Fragen oder Problemen:

1. Prüfe die [Dokumentation](docs/)
2. Schaue in die [Issues](../../issues)
3. Erstelle ein neues Issue mit detaillierter Beschreibung

---

*Erstellt mit ❤️ für bessere Schulverwaltung*
