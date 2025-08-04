# SchulBuddy ARM-Unterstützung

Diese Datei dokumentiert die ARM-Unterstützung für SchulBuddy.

## ARM-Images

SchulBuddy bietet Docker-Images für folgende Architekturen:
- AMD64 (x86_64): Vollständige Unterstützung aller Funktionen
- ARM64 (aarch64): Eingeschränkte Funktionalität
- ARMv7: Eingeschränkte Funktionalität

## Funktionale Einschränkungen auf ARM

Aufgrund von Build-Zeit- und Kompatibilitätsüberlegungen haben die ARM-basierten Docker-Images folgende Einschränkungen:

1. **Keine pandas-Unterstützung**: 
   - Die Datenanalyse- und Export-Funktionen, die pandas verwenden, sind auf ARM-Architekturen nicht verfügbar
   - Die entsprechenden Funktionen in der Benutzeroberfläche werden fehlerhafte Ergebnisse liefern

2. **Keine reportlab-Unterstützung**:
   - Die PDF-Generierungsfunktionen sind auf ARM-Architekturen nicht verfügbar
   - Versuche, PDFs zu generieren, werden fehlschlagen

## Empfohlene Verwendung

1. **Entwicklung und Testing**: AMD64-Architektur verwenden
2. **Produktive Umgebungen**: AMD64-Architektur empfohlen
3. **Raspberry Pi und andere ARM-Geräte**: Verwenden Sie ARM-Images nur, wenn Sie die o.g. Einschränkungen akzeptieren können

## Technische Details

In den ARM-Docker-Images wurden die komplexen Abhängigkeiten (pandas, reportlab) durch Stub-Module ersetzt, um die Build-Zeit drastisch zu reduzieren. Die Grundfunktionalität der Anwendung bleibt erhalten, aber Funktionen, die diese Bibliotheken nutzen, werden nicht korrekt funktionieren.

Wenn Sie die volle Funktionalität auf ARM benötigen, müssen Sie das Docker-Image selbst lokal bauen und dabei ausreichend Zeit für die Kompilierung der komplexen Abhängigkeiten einplanen.

## Build-Prozess

Um die Entwicklung zu beschleunigen, wurden die Docker-Builds in separate Workflows aufgeteilt:

1. **Einheitlicher AMD64-Build** (`docker-amd64-unified.yml`):
   - Schnell (ca. 3-5 Minuten)
   - Wird automatisch bei jedem Push auf main/dev ausgeführt
   - Pusht Images sowohl zu Docker Hub als auch zu GitHub Container Registry

2. **Separate ARM-Builds** (`docker-arm-build.yml`):
   - Deutlich langsamer (30+ Minuten)
   - Wird nur manuell oder bei Änderungen an ARM-spezifischen Dateien ausgeführt
   - Verwendet `Dockerfile.arm` statt des Standard-Dockerfiles

## Container-Tags

Die Container-Images werden mit verschiedenen Tags veröffentlicht:

- `schulbuddy:v1.2.3-amd64` - Nur AMD64-Version
- `schulbuddy:v1.2.3-arm` - Nur ARM-Version (ARM64/ARMv7)
- `schulbuddy:v1.2.3` - Multi-Architektur-Manifest (AMD64 + ARM)

Ähnliches gilt für die `latest` und `dev` Tags.
