# 🚀 SchulBuddy Multi-Architecture Docker Deployment

SchulBuddy unterstützt jetzt **automatische Architektur-Erkennung** für:
- **AMD64** (normale PCs, Server)
- **ARM** (Raspberry Pi, Apple M1/M2)

## 🎯 Quick Start

```bash
# 1. Repository klonen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# 2. Konfiguration vorbereiten
cp .env.example .env
# Bearbeite .env nach deinen Bedürfnissen

# 3. Container starten (Docker wählt automatisch richtige Architektur!)
docker-compose up -d
```

## 🏗️ Multi-Architecture Features

### Automatische Architektur-Auswahl
```bash
# Docker erkennt automatisch dein System:
docker pull timbobn/schulbuddy:latest
# → AMD64 auf normalen PCs
# → ARM auf Raspberry Pi / Apple Silicon
```

### Verfügbare Images

| Registry | Image | Architekturen |
|----------|-------|---------------|
| **Docker Hub** | `timbobn/schulbuddy:latest` | AMD64, ARM |
| **GitHub Container Registry** | `ghcr.io/timbobn/schulbuddy:latest` | AMD64, ARM |
| **Development** | `timbobn/schulbuddy:dev` | AMD64, ARM |

## 📋 Konfiguration

### Registry wechseln
```yaml
# Docker Hub (Standard)
image: docker.io/timbobn/schulbuddy:${TAG:-latest}

# GitHub Container Registry
image: ghcr.io/timbobn/schulbuddy:${TAG:-latest}
```

### Performance-Optimierung
```bash
# .env Datei
WORKERS=auto  # Automatisch: 2 für ARM, 4 für AMD64
# WORKERS=2   # Manuell für schwächere Systeme
# WORKERS=4   # Manuell für stärkere Systeme
```

### Architektur erzwingen (optional)
```bash
# Nur wenn nötig (normalerweise automatisch)
PLATFORM=linux/amd64    # Für AMD64
PLATFORM=linux/arm64    # Für ARM64
PLATFORM=linux/arm/v7   # Für ARMv7
```

## 🔍 Multi-Arch Testing

```bash
# Verfügbare Architekturen anzeigen
docker manifest inspect timbobn/schulbuddy:latest

# PowerShell Test-Script
.\test-multiarch.ps1

# Bash Test-Script  
./test-multiarch.sh
```

## 📊 Architektur-Übersicht

### AMD64 (x86_64)
- **Hardware**: Normale PCs, Server, Intel/AMD CPUs
- **Performance**: 4 Gunicorn Worker
- **Optimiert für**: Hohe Last, viele gleichzeitige Benutzer

### ARM (ARMv7/ARM64)
- **Hardware**: Raspberry Pi, Apple M1/M2, ARM-Server
- **Performance**: 2 Gunicorn Worker
- **Optimiert für**: Energieeffizienz, kleinere Deployments

## 🚦 Health Check

```bash
# Container Status prüfen
docker-compose ps

# Health Check manuell
curl http://localhost:5000/health

# Logs anzeigen
docker-compose logs -f schulbuddy
```

## 🔧 Troubleshooting

### Architektur-Probleme
```bash
# Aktuelle System-Architektur
uname -m  # Linux/Mac
echo $env:PROCESSOR_ARCHITECTURE  # Windows PowerShell

# Container-Architektur prüfen
docker image inspect timbobn/schulbuddy:latest --format '{{.Architecture}}'
```

### Performance-Tuning
```bash
# Für ARM-Systeme (Raspberry Pi)
WORKERS=2
TIMEOUT=180

# Für starke AMD64-Systeme
WORKERS=6
TIMEOUT=60
```

## 📦 Development

### Lokales Build (Multi-Arch)
```bash
# AMD64 Build
docker build -f Dockerfile -t schulbuddy:amd64 .

# ARM Build  
docker build -f Dockerfile.arm -t schulbuddy:arm .
```

### Tags und Versioning
- `latest` → Neueste stabile Version (main branch)
- `dev` → Entwicklungsversion (dev branch)  
- `v1.0.0` → Spezifische Versionen (git tags)

## 🌟 Vorteile

✅ **Einfache Nutzung**: `docker pull latest` funktioniert überall  
✅ **Optimierte Performance**: Architektur-spezifische Worker-Anzahl  
✅ **Breite Kompatibilität**: Raspberry Pi bis High-End Server  
✅ **Automatische Erkennung**: Keine manuelle Architektur-Auswahl nötig  
✅ **Professionelles Setup**: Wie nginx, postgres, etc.  

---

**Developed with ❤️ for Multi-Architecture Deployment**
