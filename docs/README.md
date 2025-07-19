# 📚 SchulBuddy Dokumentation

Umfassende Dokumentation für das SchulBuddy Docker Setup.

## 📖 Dokumentations-Übersicht

### 🚀 [Deployment Guide](DEPLOYMENT.md)
Vollständige Anleitung für verschiedene Deployment-Szenarien:
- Docker Container Setup
- Python Direct Installation  
- Server Deployment
- SSL/HTTPS Konfiguration
- Automatisierte Deployments

### 🔧 [Development Guide](DEVELOPMENT.md)
Entwicklungs-Setup und Workflows:
- Development Environment
- Code-Struktur und Organisation
- Testing und Debugging
- Frontend/Backend Development
- Build & Deployment Prozess

### 🐳 [Docker Guide](DOCKER.md)
Docker-spezifische Konfiguration:
- Container-Architektur
- Docker Compose Setups
- Volumes und Persistierung
- Netzwerk-Konfiguration
- Performance und Monitoring

### 🔍 [Troubleshooting Guide](TROUBLESHOOTING.md)
Problemlösung und Debugging:
- Häufige Probleme und Lösungen
- Diagnostik-Tools
- Container und Netzwerk-Debugging
- Environment-spezifische Issues
- Support und Hilfe

### ⚙️ [Konfiguration](CONFIGURATION.md)
Umgebungsvariablen und Einstellungen:
- Environment Variables (.env)
- Security Configuration
- Database Setup
- Email und Upload Konfiguration
- Multi-Environment Setup

### 🤖 [CI/CD Guide](CICD.md)
Continuous Integration und Deployment:
- GitHub Actions Workflows
- Container Registry Integration
- Multi-Environment Deployments
- Security und Quality Gates
- Release Automation

## 🚀 Schnellstart Links

| Aufgabe | Dokumentation | Direkter Link |
|---------|---------------|---------------|
| **Erste Installation** | Deployment Guide | [Docker Setup](DEPLOYMENT.md#docker-container-empfohlen) |
| **Development starten** | Development Guide | [Development Setup](DEVELOPMENT.md#development-setup) |
| **Problem lösen** | Troubleshooting | [Häufige Probleme](TROUBLESHOOTING.md#häufige-probleme) |
| **Port konfigurieren** | Konfiguration | [Port Settings](CONFIGURATION.md#web-server-configuration) |
| **Backup erstellen** | Deployment Guide | [Backup & Restore](DEPLOYMENT.md#updates-und-wartung) |
| **Docker debuggen** | Docker Guide | [Container Debugging](DOCKER.md#debugging) |

## 📋 Checklisten

### ✅ Basis-Setup Checklist
- [ ] Repository geklont
- [ ] `.env` Datei erstellt und angepasst
- [ ] `SECRET_KEY` geändert
- [ ] Schuljahr und Semester konfiguriert
- [ ] Container erfolgreich gestartet
- [ ] Health Check erfolgreich

### ✅ Production-Ready Checklist
- [ ] `FLASK_ENV=production` gesetzt
- [ ] `DEBUG=false` aktiviert
- [ ] Sichere `SECRET_KEY` konfiguriert
- [ ] HTTPS aktiviert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring eingerichtet
- [ ] Logs konfiguriert

### ✅ Security Checklist
- [ ] Starke Passwörter verwendet
- [ ] API Keys konfiguriert
- [ ] Session Timeouts gesetzt
- [ ] File Upload Limits definiert
- [ ] HTTPS für Production aktiviert
- [ ] Database-Backups verschlüsselt

## 🆘 Schnelle Hilfe

### Häufigste Befehle

```bash
# Setup und Start
./start.sh setup
./start.sh up

# Status und Debugging
./start.sh status
./start.sh health
./start.sh logs

# Wartung
./start.sh backup
./start.sh restart
./start.sh clean
```

### Häufigste Probleme

| Problem | Lösung | Link |
|---------|--------|------|
| Port 5000 belegt | `.env` bearbeiten, `PORT=8080` setzen | [Port Konfiguration](CONFIGURATION.md#web-server-configuration) |
| Container startet nicht | `./start.sh status` und `./start.sh logs` prüfen | [Container Debugging](TROUBLESHOOTING.md#container-startet-nicht) |
| Database Fehler | Berechtigungen prüfen, DB neu initialisieren | [Database Issues](TROUBLESHOOTING.md#unable-to-open-database-file) |
| Upload Fehler | Upload-Ordner Berechtigungen prüfen | [File Upload](TROUBLESHOOTING.md#berechtigungsprobleme) |

## 📞 Support

- **GitHub Issues:** [Issue erstellen](https://github.com/TimBoBN/schulbuddy/issues)
- **Dokumentation:** Diese Guides durchlesen
- **Community:** GitHub Discussions

## 🔄 Dokumentation Updates

Diese Dokumentation wird kontinuierlich aktualisiert. Bei Fragen oder Verbesserungsvorschlägen:

1. Issue im GitHub Repository erstellen
2. Pull Request mit Verbesserungen einreichen
3. Diskussion in GitHub Discussions starten

---

**📝 Letzte Aktualisierung:** July 2025
**📧 Maintainer:** TimBoBN
**🏷️ Version:** v2.0
