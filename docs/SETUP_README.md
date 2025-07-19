# 🚀 SchulBuddy Docker - Schnellstart

## **Wie und wann wird die .env-Datei erstellt?**

Die `.env`-Datei wird **NICHT automatisch** erstellt. Sie müssen sie manuell erstellen:

### **Option 1: Automatisches Setup (Empfohlen)**

#### Windows PowerShell:
```powershell
.\setup-env.ps1
```

#### Linux/Mac:
```bash
chmod +x setup-env.sh
./setup-env.sh
```

### **Option 2: Manuelle Erstellung**

```bash
# Kopiere Template zu .env
cp .env.template .env

# Oder alternativ
cp .env.example .env

# Bearbeite die Datei
notepad .env  # Windows
nano .env     # Linux/Mac
```

### **Option 3: Schnellstart mit Standard-Werten**

```bash
# Erstelle .env mit Standard-Port 5000
echo "PORT=5000" > .env
echo "EXTERNAL_PORT=5000" >> .env
echo "DOCKER_ENV=1" >> .env
```

## **📋 Verfügbare .env-Dateien:**

| Datei | Zweck | Status |
|-------|-------|--------|
| `.env` | **Aktive Konfiguration** | ✅ Wird von Docker Compose gelesen |
| `.env.example` | Basis-Vorlage | 📋 Kopiervorlage |
| `.env.template` | Vollständige Vorlage | 📋 Kopiervorlage mit Port-Config |

## **🔧 Wichtige Umgebungsvariablen:**

```bash
# Server
HOST=0.0.0.0
PORT=5000                    # Port im Container
EXTERNAL_PORT=5000          # Port für Zugriff von außen

# Datenbank  
DOCKER_ENV=1                # Aktiviert Docker-Modus
DATABASE_URL=sqlite:////app/data/schulbuddy.db

# Sicherheit
SECRET_KEY=dein-geheimer-schlüssel
```

## **🚀 Schnellstart-Befehle:**

```bash
# 1. Setup
.\setup-env.ps1            # Windows
./setup-env.sh             # Linux/Mac

# 2. Starten
docker-compose up -d

# 3. Zugriff
http://localhost:5000
```

## **🔍 Port-Konfiguration testen:**

```bash
# Standard-Port 5000
docker-compose up -d

# Anderer Port (z.B. 8080)
$env:PORT=8080; $env:EXTERNAL_PORT=8080; docker-compose up -d

# Mit .env-Datei
# Ändere PORT=8080 in .env, dann:
docker-compose up -d
```

## **❓ Troubleshooting:**

### `.env` wird nicht gefunden
```bash
# Prüfe verfügbare Dateien
ls -la *.env*

# Erstelle von Template
cp .env.template .env
```

### Port bereits belegt
```bash
# Prüfe Port-Belegung
netstat -an | findstr :5000

# Verwende anderen Port
$env:EXTERNAL_PORT=5001; docker-compose up -d
```

### Konfiguration wird nicht übernommen
```bash
# Container neu starten
docker-compose down
docker-compose up -d

# Logs prüfen
docker-compose logs schulbuddy
```
