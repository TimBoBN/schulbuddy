# ⚙️ Konfiguration

Umfassende Anleitung für die Konfiguration von SchulBuddy.

## 📝 Environment Variables (.env)

### Basis-Konfiguration

```env
# Flask Settings
SECRET_KEY=your-very-secure-secret-key-change-this
FLASK_ENV=production
PORT=5000

# Database
DATABASE_URL=sqlite:///instance/schulbuddy.db

# School Configuration
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1
```

### Vollständige .env Referenz

```env
# ===== FLASK SETTINGS =====
SECRET_KEY=your-very-secure-secret-key-change-this
FLASK_ENV=production  # development, production
PORT=5000
DEBUG=false

# ===== DATABASE =====
DATABASE_URL=sqlite:///instance/schulbuddy.db
# Alternative: PostgreSQL
# DATABASE_URL=postgresql://user:password@db:5432/schulbuddy
# Alternative: MySQL
# DATABASE_URL=mysql://user:password@db:3306/schulbuddy

# ===== SESSION CONFIGURATION =====
SESSION_TIMEOUT_MINUTES=120
SESSION_COOKIE_SECURE=false  # true für HTTPS
REMEMBER_COOKIE_DAYS=30
LOGIN_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_TIMEOUT_MINUTES=15
TWO_FACTOR_TIMEOUT_MINUTES=5

# ===== SCHOOL CONFIGURATION =====
CURRENT_SCHOOL_YEAR=2024/25
CURRENT_SEMESTER=1

# ===== SECURITY =====
API_KEY_ENABLED=true
API_KEY=your-api-key-here
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# ===== FILE UPLOADS =====
MAX_UPLOAD_SIZE=16777216  # 16MB in Bytes
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png

# ===== EMAIL (Optional) =====
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# ===== EXTERNAL SERVICES =====
# Backup Service
BACKUP_ENABLED=false
BACKUP_LOCATION=/backups
BACKUP_RETENTION_DAYS=30

# Monitoring
MONITORING_ENABLED=false
HEALTH_CHECK_URL=/health
```

## 🏫 School Configuration

### Schuljahr-Setup

```env
# Aktuelles Schuljahr
CURRENT_SCHOOL_YEAR=2024/25

# Semester (1 oder 2)
CURRENT_SEMESTER=1

# Schuljahres-Start (Optional)
SCHOOL_YEAR_START=2024-09-01
SCHOOL_YEAR_END=2025-07-31
```

### Notensystem

```python
# config.py
GRADE_SYSTEM = {
    'scale': '1-6',  # 1-6, A-F, 0-100
    'passing_grade': 4,
    'excellent_grade': 1
}
```

## 🔐 Security Configuration

### Session Management

```env
# Session Timeout (Minuten)
SESSION_TIMEOUT_MINUTES=120

# Login Versuche
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_TIMEOUT_MINUTES=15

# Cookie Settings
SESSION_COOKIE_SECURE=true  # Nur HTTPS
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### API Security

```env
# API Key Protection
API_KEY_ENABLED=true
API_KEY=your-secure-api-key

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Two-Factor Authentication

```env
# 2FA Settings
TWO_FACTOR_ENABLED=true
TWO_FACTOR_TIMEOUT_MINUTES=5
TWO_FACTOR_BACKUP_CODES=10
```

## 🗄️ Database Configuration

### SQLite (Standard)

```env
DATABASE_URL=sqlite:///instance/schulbuddy.db
```

**Vorteile:**
- Einfaches Setup
- Keine externe Datenbank nötig
- Gut für kleine bis mittlere Installationen

### PostgreSQL (Empfohlen für Produktion)

```env
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

**Docker Compose Setup:**
```yaml
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: schulbuddy
      POSTGRES_USER: schulbuddy
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### MySQL

```env
DATABASE_URL=mysql://username:password@hostname:3306/database_name
```

## 📧 Email Configuration

### Gmail Setup

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # App-spezifisches Passwort
```

### Outlook/Hotmail

```env
MAIL_SERVER=smtp.live.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### Custom SMTP

```env
MAIL_SERVER=mail.your-domain.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@your-domain.com
MAIL_PASSWORD=your-password
```

## 📁 File Upload Configuration

### Upload Settings

```env
# Maximale Datei-Größe (Bytes)
MAX_UPLOAD_SIZE=16777216  # 16MB

# Erlaubte Dateierweiterungen
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,jpg,jpeg,png,gif

# Upload-Verzeichnis
UPLOAD_FOLDER=static/uploads
```

### Storage Backends

**Lokaler Storage (Standard):**
```env
STORAGE_BACKEND=local
STORAGE_PATH=static/uploads
```

**S3-kompatible Storage:**
```env
STORAGE_BACKEND=s3
S3_BUCKET=schulbuddy-uploads
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT=https://s3.amazonaws.com
```

## 🌐 Web Server Configuration

### Development

```env
FLASK_ENV=development
DEBUG=true
PORT=5000
HOST=127.0.0.1
```

### Production

```env
FLASK_ENV=production
DEBUG=false
PORT=5000
HOST=0.0.0.0

# Gunicorn Settings
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=30
GUNICORN_KEEPALIVE=2
```

## 📊 Logging Configuration

### Log Levels

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=detailed  # simple, detailed, json
LOG_FILE=logs/schulbuddy.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

### Structured Logging

```python
# config.py
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/schulbuddy.log',
            'maxBytes': 10485760,
            'backupCount': 5,
            'formatter': 'default',
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}
```

## 🔄 Backup Configuration

### Automatische Backups

```env
# Backup Settings
BACKUP_ENABLED=true
BACKUP_SCHEDULE=daily  # hourly, daily, weekly
BACKUP_RETENTION_DAYS=30
BACKUP_LOCATION=/backups

# S3 Backup
BACKUP_S3_ENABLED=false
BACKUP_S3_BUCKET=schulbuddy-backups
```

### Backup Script

```bash
#!/bin/bash
# backup-config.sh
BACKUP_DIR="/backups"
RETENTION_DAYS=30
DATABASE_FILE="instance/schulbuddy.db"
UPLOADS_DIR="static/uploads"

# Automatisches Backup erstellen
./start.sh backup

# Alte Backups aufräumen
find $BACKUP_DIR -name "*.db" -mtime +$RETENTION_DAYS -delete
```

## 🌍 Multi-Environment Setup

### Development (.env.dev)

```env
FLASK_ENV=development
DEBUG=true
PORT=5000
DATABASE_URL=sqlite:///instance/schulbuddy_dev.db
LOG_LEVEL=DEBUG
```

### Staging (.env.staging)

```env
FLASK_ENV=production
DEBUG=false
PORT=8080
DATABASE_URL=postgresql://staging_user:password@staging-db:5432/schulbuddy_staging
LOG_LEVEL=INFO
```

### Production (.env.prod)

```env
FLASK_ENV=production
DEBUG=false
PORT=80
DATABASE_URL=postgresql://prod_user:secure_password@prod-db:5432/schulbuddy
LOG_LEVEL=WARNING
SESSION_COOKIE_SECURE=true
```

## 🔧 Docker Configuration

### docker-compose.override.yml

```yaml
# Lokale Overrides
version: '3.8'
services:
  schulbuddy:
    environment:
      - FLASK_ENV=development
      - DEBUG=true
    volumes:
      - .:/app
    ports:
      - "5000:5000"
```

### Environment Files in Docker

```yaml
services:
  schulbuddy:
    env_file:
      - .env.common
      - .env.${ENVIRONMENT:-development}
```

## 📋 Configuration Checklist

### Basis-Setup
- [ ] `SECRET_KEY` geändert
- [ ] `CURRENT_SCHOOL_YEAR` gesetzt
- [ ] `CURRENT_SEMESTER` konfiguriert
- [ ] `PORT` nach Bedarf angepasst

### Security
- [ ] Strong `SECRET_KEY` (32+ Zeichen)
- [ ] `API_KEY` für API-Zugriff
- [ ] Session-Timeouts konfiguriert
- [ ] HTTPS in Produktion (`SESSION_COOKIE_SECURE=true`)

### Production
- [ ] `FLASK_ENV=production`
- [ ] `DEBUG=false`
- [ ] Database für Produktion konfiguriert
- [ ] Backup-Strategie implementiert
- [ ] Monitoring konfiguriert
