# 📚 SchulBuddy Docker Documentation

Willkommen zur Docker-Dokumentation von SchulBuddy! Hier findest du alle wichtigen Informationen für das Deployment.

## 🚀 Quick Start

```bash
# 1. Konfiguration vorbereiten
cp config/.env.example .env
# Bearbeite .env nach deinen Bedürfnissen

# 2. Container starten
docker-compose up -d

# 3. Öffne http://localhost:5000
```

## 📁 Verzeichnisstruktur

```
schulbuddy/
├── config/                    # Konfigurationsdateien
│   ├── .env.example          # Environment-Variablen Vorlage
│   ├── .env.template         # Alternative Vorlage
│   └── nginx.conf            # Nginx Konfiguration
├── docs/                     # Dokumentation
│   ├── ARM_SUPPORT.md        # ARM-Support Details
│   ├── DOCKER_README.md      # Docker Setup Guide
│   ├── MULTI-ARCH-README.md  # Multi-Architecture Guide
│   └── SECURITY.md           # Sicherheitsrichtlinien
├── scripts/                  # Utility Scripts
│   ├── build-multiarch.ps1   # Multi-Arch Build (PowerShell)
│   ├── build-multiarch.sh    # Multi-Arch Build (Bash)
│   ├── setup-env.ps1         # Environment Setup (PowerShell)
│   └── setup-env.sh          # Environment Setup (Bash)
├── docker-compose.yml        # Container Orchestrierung
├── Dockerfile               # AMD64 Container Build
├── Dockerfile.arm          # ARM Container Build
├── entrypoint.sh           # Container Startup Script
└── README.md              # Hauptdokumentation
```

## 📖 Detaillierte Dokumentation

### 🏗️ Multi-Architecture Support
→ **[docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md)**
- Automatische Architektur-Erkennung
- AMD64 und ARM Support
- Performance-Optimierung

### 🔧 Docker Setup
→ **[docs/DOCKER_README.md](docs/DOCKER_README.md)**
- Detaillierte Installation
- Troubleshooting
- Erweiterte Konfiguration

### 🛡️ Sicherheit
→ **[docs/SECURITY.md](docs/SECURITY.md)**
- Sicherheitsrichtlinien
- Best Practices
- Vulnerability Reporting

### 🔋 ARM Support
→ **[docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md)**
- Raspberry Pi Support
- Apple Silicon (M1/M2)
- ARM-spezifische Optimierungen

## 🛠️ Verfügbare Scripts

### PowerShell (Windows)
```powershell
# Multi-Architecture Build
.\scripts\build-multiarch.ps1

# Environment Setup
.\scripts\setup-env.ps1
```

### Bash (Linux/Mac)
```bash
# Multi-Architecture Build
./scripts/build-multiarch.sh

# Environment Setup
./scripts/setup-env.sh
```

## 🎯 Häufige Anwendungsfälle

### Erste Installation
1. Lies **[docs/DOCKER_README.md](docs/DOCKER_README.md)**
2. Kopiere `config/.env.example` zu `.env`
3. Führe `docker-compose up -d` aus

### Multi-Architecture Deployment
1. Lies **[docs/MULTI-ARCH-README.md](docs/MULTI-ARCH-README.md)**
2. Verwende `scripts/build-multiarch.sh`
3. Images werden automatisch für alle Architekturen erstellt

### Production Deployment
1. Überprüfe **[docs/SECURITY.md](docs/SECURITY.md)**
2. Konfiguriere sichere Environment-Variablen
3. Verwende `docker-compose up -d --scale schulbuddy=2`

### ARM-Geräte (Raspberry Pi)
1. Lies **[docs/ARM_SUPPORT.md](docs/ARM_SUPPORT.md)**
2. Verwende `WORKERS=2` in der `.env`
3. Images werden automatisch ARM-optimiert geladen

## 🤝 Beitragen

- **Issues**: GitHub Issues für Bug Reports
- **Security**: Siehe [docs/SECURITY.md](docs/SECURITY.md)
- **Documentation**: PRs für Dokumentationsverbesserungen willkommen

## 📞 Support

- **GitHub Issues**: Für technische Probleme
- **Dokumentation**: Alle Guides in `/docs`
- **Scripts**: Automatisierte Lösungen in `/scripts`

---

**Entwickelt mit ❤️ für einfaches Multi-Architecture Deployment**
