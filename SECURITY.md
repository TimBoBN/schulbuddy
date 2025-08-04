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
| [CVE-2025-6020](https://nvd.nist.gov/vuln/detail/CVE-2025-6020) | - | - | Hoch (7.8) | Basisbetriebssystem-Komponente | Mittel (Container-Isolation reduziert das Risiko) |
| [CVE-2025-7458](https://nvd.nist.gov/vuln/detail/CVE-2025-7458) | debian/pam | 1.5.2-6+deb12u1 | Medium (6.9) | Basisbetriebssystem-Abhängigkeit | Niedrig (Authentifizierungsmodule haben eingeschränkte Nutzung im Container) |
| [CVE-2021-45346](https://nvd.nist.gov/vuln/detail/CVE-2021-45346) | debian/sqlite3 | 3.40.1-2+deb12u1 | Niedrig | Ältere Schwachstelle, lokal begrenzt | Sehr niedrig (benötigt lokalen Zugriff) |
| [CVE-2025-45582](https://nvd.nist.gov/vuln/detail/CVE-2025-45582) | debian/tar | 1.34+dfsg-1.2+deb12u1 | Medium (4.1) | Nur während des Container-Builds relevant | Sehr niedrig (nicht ausnutzbar im laufenden Container) |
| [CVE-2025-1180](https://nvd.nist.gov/vuln/detail/CVE-2025-1180) | debian/binutils | 2.40-2 | Niedrig | Nur während des Container-Builds relevant | Sehr niedrig (wird zur Laufzeit nicht verwendet) |
| [CVE-2025-1152](https://nvd.nist.gov/vuln/detail/CVE-2025-1152) | debian/binutils | 2.40-2 | Niedrig | Nur während des Container-Builds relevant | Sehr niedrig (wird zur Laufzeit nicht verwendet) |

### Risikobewertung und Entschärfungsmaßnahmen

Für jede nicht-fixbare CVE haben wir eine Risikobewertung durchgeführt und Maßnahmen zur Risikominderung implementiert:

1. **Container-Isolation**: Alle Dienste laufen in isolierten Containern, was das Ausnutzen von Basis-OS-Schwachstellen erschwert
2. **Least-Privilege-Prinzip**: Container laufen mit non-root User und minimalen Berechtigungen
3. **Minimierte Angriffsfläche**: Unnötige Tools und Dateien wurden entfernt
4. **Strikte Dateiberechtigungen**: Alle Dateien haben restriktive Berechtigungen
5. **Multistage Build**: Build-Tools wie binutils sind nicht im finalen Container enthalten
6. **Regelmäßige Neubewertung**: Wir überprüfen regelmäßig, ob Updates für diese CVEs verfügbar sind

#### Spezifische Entschärfungsmaßnahmen:

- **SQLite3-Schwachstellen**: Die Datenbank wird nur vom Anwendungscode mit begrenzten Berechtigungen verwendet, nicht direkt von Benutzern
- **PAM-Schwachstellen**: Im Container wird keine interaktive Benutzerauthentifizierung über PAM verwendet
- **Binutils**: Diese Tools werden nur während des Build-Prozesses verwendet und sind nicht im finalen Container enthalten
- **Tar**: Wird nur während des Container-Builds verwendet, nicht zur Laufzeit

## Sicherheits-Updates

Wir aktualisieren regelmäßig alle Abhängigkeiten, um Sicherheitslücken zu schließen. Die Container-Images werden automatisch über unsere CI/CD-Pipeline neu gebaut und veröffentlicht, sobald neue Sicherheits-Updates verfügbar sind.

## Best Practices für Deployment

1. Regelmäßige Updates durchführen: `docker-compose pull && docker-compose up -d`
2. Host-System aktuell halten
3. Netzwerkzugriff auf den Container beschränken
4. SSL/TLS für alle externen Verbindungen verwenden
