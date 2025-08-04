# Sicherheitsrichtlinie

## Unterstützte Versionen

| Version | Unterstützt          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| 1.2.x   | :white_check_mark: |
| 1.1.x   | :x:                |
| 1.0.x   | :x:                |

## Sicherheitslücken melden

Wir nehmen die Sicherheit von SchulBuddy ernst. Wenn Sie eine Sicherheitslücke entdecken, melden Sie diese bitte direkt an uns.

### Meldeprozess
1. Erstellen Sie ein neues Issue mit dem Label "security"
2. Beschreiben Sie das Problem und potenzielle Auswirkungen
3. Wenn möglich, fügen Sie Schritte zur Reproduktion hinzu

## Bekannte CVEs

Dieses Projekt verwendet einige Abhängigkeiten, die bekannte CVEs aufweisen, für die es noch keine Fixes gibt oder bei denen ein Update aus Kompatibilitätsgründen nicht möglich ist.

### Nicht-fixbare CVEs

| CVE-ID | Paket | Version | Schweregrad | Begründung | Risikobewertung |
|--------|-------|---------|-------------|------------|-----------------|
| [CVE-XXXX-XXXX](https://nvd.nist.gov/vuln/detail/CVE-XXXX-XXXX) | paket-name | X.Y.Z | Medium | Transitive Abhängigkeit ohne verfügbaren Fix | Niedrig (nicht ausnutzbar in unserer Konfiguration) |

### Risikobewertung und Entschärfungsmaßnahmen

Für jede nicht-fixbare CVE haben wir eine Risikobewertung durchgeführt und gegebenenfalls Maßnahmen zur Risikominderung implementiert:

1. **Container-Isolation**: Alle Dienste laufen in isolierten Containern
2. **Least-Privilege-Prinzip**: Container laufen mit minimalen Berechtigungen
3. **Regelmäßige Neubewertung**: Wir überprüfen regelmäßig, ob Updates verfügbar sind

## Sicherheits-Updates

Wir aktualisieren regelmäßig alle Abhängigkeiten, um Sicherheitslücken zu schließen. Die Container-Images werden automatisch über unsere CI/CD-Pipeline neu gebaut und veröffentlicht, sobald neue Sicherheits-Updates verfügbar sind.

## Best Practices für Deployment

1. Regelmäßige Updates durchführen: `docker-compose pull && docker-compose up -d`
2. Host-System aktuell halten
3. Netzwerkzugriff auf den Container beschränken
4. SSL/TLS für alle externen Verbindungen verwenden
