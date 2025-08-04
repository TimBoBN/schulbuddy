# 🐳 SchulBuddy Docker-Anleitung

## Multi-Architektur-Unterstützung

SchulBuddy Docker-Images unterstützen ab jetzt mehrere Plattformen, sodass du die Anwendung auf verschiedenen Architekturen ausführen kannst:

- **linux/amd64**: Standard x86_64 (Intel/AMD Computer)
- **linux/arm64**: 64-bit ARM (z.B. Apple Silicon, Raspberry Pi 4 64-bit)
- **linux/arm/v7**: 32-bit ARM (z.B. Raspberry Pi 2/3)

Das bedeutet, dass du die gleichen Docker-Befehle unabhängig von der Architektur deines Geräts verwenden kannst:

```bash
docker pull timbobn/schulbuddy:latest
# oder
docker pull ghcr.io/timbobn/schulbuddy:latest
```

Docker wählt automatisch das richtige Image für deine Architektur aus.

## Lokaler Multi-Architektur-Build

Wenn du SchulBuddy für mehrere Plattformen lokal bauen möchtest, kannst du unsere Build-Skripte verwenden:

### Linux/Mac:
```bash
bash scripts/build-multiarch.sh [TAG]
```

### Windows (PowerShell):
```powershell
.\scripts\build-multiarch.ps1 [TAG]
```

Dabei ist `[TAG]` optional und standardmäßig auf "dev" gesetzt.

## Voraussetzungen für Multi-Architektur-Builds

Um Multi-Architektur-Images lokal zu bauen, benötigst du:

1. Docker mit Buildx-Support (Docker Desktop oder neuere Docker Engine-Versionen)
2. QEMU für die Emulation fremder Architekturen:
   ```bash
   # Linux
   docker run --privileged --rm tonistiigi/binfmt --install all
   
   # Docker Desktop für Windows/Mac hat dies bereits integriert
   ```

## Verwendung auf ARM-Geräten (z.B. Raspberry Pi)

SchulBuddy läuft jetzt nativ auf ARM-Geräten wie dem Raspberry Pi:

```bash
# Auf einem Raspberry Pi
docker-compose up -d
```

Die Anwendung nutzt automatisch das ARM-optimierte Image und bietet bessere Performance als bei der Emulation.

## Konfiguration für beste Performance

Für optimale Performance auf ARM-Geräten empfehlen wir:

- Mindestens 2 GB RAM für Raspberry Pi 3/4
- Eine schnelle SD-Karte oder besser noch ein USB-SSD für die Datenbank
- SQLite auf externer Festplatte für bessere Dauerhaftigkeit:
  ```yaml
  volumes:
    - /external/path/to/data:/app/data
  ```

## Troubleshooting

### Bekannte Probleme und Lösungen

1. **Fehler "no matching manifest for linux/arm64/v8"**
   - Lösung: Verwende einen aktualisierten Docker-Client (20.10.0+)
   - Überprüfe mit `docker version`, dass Client und Server aktuell sind

2. **Performance-Probleme auf ARM**
   - Einige Python-Pakete benötigen mehr Ressourcen auf ARM
   - Reduziere die Anzahl der Gunicorn-Worker in `gunicorn.conf.py`:
     ```python
     workers = 2  # Standardwert für ARM reduzieren
     ```

3. **Speicherprobleme bei Build-Prozessen**
   - ARM-Builds benötigen mehr Speicher
   - Erhöhe den verfügbaren RAM für Docker oder füge Swap-Speicher hinzu
