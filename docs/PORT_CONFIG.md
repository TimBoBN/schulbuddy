# Port-Konfiguration für SchulBuddy Docker

## 🚀 Schnellstart

### Standard-Port (5000)
```bash
docker-compose up -d
```
Anwendung erreichbar unter: `http://localhost:5000`

### Anderer Port (z.B. 8080)
```bash
# Windows PowerShell
$env:PORT=8080; $env:EXTERNAL_PORT=8080; docker-compose up -d

# Linux/Mac
PORT=8080 EXTERNAL_PORT=8080 docker-compose up -d
```
Anwendung erreichbar unter: `http://localhost:8080`

### Mit .env-Datei
1. Kopiere `.env.template` zu `.env`
2. Ändere `PORT=8080` und `EXTERNAL_PORT=8080`
3. Führe aus: `docker-compose up -d`

## 🔧 Konfigurationsoptionen

### Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `HOST` | `0.0.0.0` | Server-Host (für Container immer 0.0.0.0) |
| `PORT` | `5000` | Port innerhalb des Containers |
| `EXTERNAL_PORT` | `5000` | Port für den Zugriff von außen |

### Port-Mapping Beispiele

#### Gleicher Port innen und außen
```yaml
ports:
  - "8080:8080"  # localhost:8080 → Container:8080
environment:
  - PORT=8080
```

#### Verschiedene Ports
```yaml
ports:
  - "3000:8080"  # localhost:3000 → Container:8080
environment:
  - PORT=8080
```

## 📋 Verwendungsbeispiele

### Development (Port 3000)
```bash
# .env-Datei erstellen
echo "PORT=3000" > .env
echo "EXTERNAL_PORT=3000" >> .env
docker-compose up -d
```

### Production (Port 80 mit nginx)
```yaml
# nginx.conf anpassen
upstream schulbuddy {
    server schulbuddy:8080;
}
```

### Multiple Instanzen
```bash
# Instanz 1 auf Port 5001
PORT=5001 EXTERNAL_PORT=5001 docker-compose -p schulbuddy1 up -d

# Instanz 2 auf Port 5002  
PORT=5002 EXTERNAL_PORT=5002 docker-compose -p schulbuddy2 up -d
```

## ✅ Testen der Konfiguration

```bash
# Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs schulbuddy

# HTTP-Test
curl -I http://localhost:8080
```

## 🔒 Sicherheitshinweise

- **Production**: Verwende nginx als Reverse Proxy
- **Firewall**: Öffne nur notwendige Ports
- **SSL**: Nutze HTTPS für öffentliche Deployments
- **Monitoring**: Überwache Port-Verfügbarkeit

## 🐛 Troubleshooting

### Port bereits belegt
```bash
# Port-Belegung prüfen
netstat -an | findstr :8080

# Anderen Port verwenden
PORT=8081 EXTERNAL_PORT=8081 docker-compose up -d
```

### Container startet nicht
```bash
# Detaillierte Logs anzeigen
docker-compose logs -f schulbuddy

# Container-Status prüfen
docker-compose ps -a
```

### Health Check fehlgeschlagen
```bash
# Health Check manuell testen
docker exec schulbuddy-app python -c "import requests; print(requests.get('http://localhost:8080').status_code)"
```
