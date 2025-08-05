# 🚀 SchulBuddy Multi-Platform Docker Setup

Dieser Multi-Platform Workflow erstellt echte Multi-Architecture Docker Images mit korrekten Platform-Annotationen für automatische Architektur-Auswahl.

## 🏗️ Workflows Übersicht

| Workflow | Zweck | Ausgabe |
|----------|-------|---------|
| `docker-amd64-unified.yml` | AMD64 spezifische Builds | `*-amd64` Tags |
| `docker-arm-build.yml` | ARM spezifische Builds | `*-arm64`, `*-armv7` Tags |
| `docker-multiplatform.yml` | **Echter Multi-Arch** | `*-multiplatform` Tags |

## 🎯 Multi-Platform Images

### Verfügbare Tags
```bash
# Development (dev branch)
docker.io/timbobn/schulbuddy:dev-multiplatform
ghcr.io/timbobn/schulbuddy:dev-multiplatform

# Production (main branch)
docker.io/timbobn/schulbuddy:latest-multiplatform
ghcr.io/timbobn/schulbuddy:latest-multiplatform

# Versionierte Releases
docker.io/timbobn/schulbuddy:v1.0.0-multiplatform
ghcr.io/timbobn/schulbuddy:v1.0.0-multiplatform
```

### Unterstützte Architekturen
- **linux/amd64** - Normale PCs, Server
- **linux/arm64** - Raspberry Pi 4+, Apple M1/M2
- **linux/arm/v7** - Raspberry Pi 3, ältere ARM-Geräte

## 🚀 Quick Start

### 1. Multi-Platform Build triggern
```bash
# PowerShell
.\scripts\trigger-multiplatform.ps1 -Version dev

# Bash
./scripts/trigger-multiplatform.sh dev
```

### 2. Multi-Platform Images verwenden
```bash
# Konfiguration für Multi-Platform
cp config/.env.multiplatform .env

# Multi-Platform Docker Compose
docker-compose -f docker-compose.multiplatform.yml up -d
```

### 3. Architektur-Erkennung testen
```bash
# Manifest inspizieren
docker manifest inspect docker.io/timbobn/schulbuddy:dev-multiplatform

# Sollte zeigen:
# - linux/amd64
# - linux/arm64 
# - linux/arm/v7

# Image pullen (automatische Architektur-Auswahl)
docker pull docker.io/timbobn/schulbuddy:dev-multiplatform
```

## 📋 Workflow Details

### Multi-Platform Build Prozess
1. **AMD64 Build**: Verwendet `Dockerfile` für AMD64-Architektur
2. **ARM Build**: Verwendet `Dockerfile.arm` für ARM64/ARMv7
3. **Manifest Creation**: Kombiniert alle Architekturen mit korrekten Annotationen
4. **Platform Annotation**: Explizite Architektur-Tags für Docker
5. **Registry Push**: Sowohl Docker Hub als auch GHCR

### Trigger-Bedingungen
- **Push auf main**: Erstellt `latest-multiplatform`
- **Push auf dev**: Erstellt `dev-multiplatform`  
- **Git Tags**: Erstellt `v*-multiplatform`
- **Manual Dispatch**: Erstellt custom `*-multiplatform`

## 🔧 Konfiguration

### Environment Variables
```bash
# Multi-Platform Docker Compose
TAG=dev-multiplatform
WORKERS=auto  # Automatische Architektur-Optimierung
TIMEOUT=120
```

### Docker Compose
```yaml
# docker-compose.multiplatform.yml
services:
  schulbuddy:
    image: docker.io/timbobn/schulbuddy:${TAG:-dev-multiplatform}
    # Automatische Architektur-Erkennung durch entrypoint.sh
```

## 🐛 Troubleshooting

### Multi-Platform nicht verfügbar
```bash
# Prüfe ob Multi-Platform Build läuft
curl -s https://api.github.com/repos/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml/runs | jq '.workflow_runs[0].status'

# Manuell triggern
gh workflow run "Multi-Platform Docker Build" --field version_tag=dev
```

### Architektur-Erkennung fehlgeschlagen
```bash
# Prüfe Manifest
docker manifest inspect docker.io/timbobn/schulbuddy:dev-multiplatform

# Debug Container-Architektur
docker run --rm docker.io/timbobn/schulbuddy:dev-multiplatform uname -a
```

### Permission Denied Fehler
```bash
# Verwende Multi-Platform Image (hat korrektes entrypoint.sh)
image: docker.io/timbobn/schulbuddy:dev-multiplatform
```

## 📊 Monitoring

### Build Status
- **GitHub Actions**: https://github.com/TimBoBN/schulbuddy/actions/workflows/docker-multiplatform.yml
- **Docker Hub**: https://hub.docker.com/r/timbobn/schulbuddy/tags
- **GHCR**: https://github.com/TimBoBN/schulbuddy/pkgs/container/schulbuddy

### Performance Metriken
- **AMD64**: ~4 Gunicorn Worker, optimiert für Performance
- **ARM64**: ~2 Gunicorn Worker, optimiert für Effizienz  
- **ARMv7**: ~2 Gunicorn Worker, optimiert für Stabilität

## 🎉 Vorteile

✅ **Echte Multi-Arch**: Korrekte Platform-Annotationen  
✅ **Automatische Auswahl**: Docker wählt passende Architektur  
✅ **Optimierte Performance**: Architektur-spezifische Konfiguration  
✅ **Einfache Nutzung**: Ein Image für alle Plattformen  
✅ **Parallel zu bestehenden Workflows**: Keine Störung der aktuellen Builds  

---

**Entwickelt für nahtlose Multi-Architecture Deployments** 🌍
