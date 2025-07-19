# 🔧 Development Guide

Entwicklungs-Setup und Workflows für SchulBuddy.

## 🚀 Development Setup

### Schnellstart

```bash
# Repository klonen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# Development Environment starten
./start.sh setup
./start.sh dev
```

Die Anwendung läuft dann mit Hot-Reload unter `http://localhost:5000`

### Alternative: Python Development

```bash
# Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Dependencies
pip install -r requirements.txt

# Environment Variables
cp .env.example .env
# .env bearbeiten

# Datenbank initialisieren
python init_db.py

# Development Server starten
export FLASK_ENV=development
python app.py
```

## 📁 Projektstruktur

```
schulbuddy/
├── app.py                 # Haupt-Flask-App
├── config.py             # Konfiguration
├── models.py             # Datenbank-Modelle
├── init_db.py           # Datenbank-Initialisierung
├── api_security.py      # API Sicherheit
├── requirements.txt     # Python Dependencies
├── Dockerfile          # Docker Container
├── docker-compose.yml  # Docker Services
├── start.sh           # Linux/Mac Startup
├── start.ps1          # Windows Startup
├── .env.example       # Environment Template
├── routes/            # Flask Routes
│   ├── auth.py       # Authentication
│   ├── main.py       # Hauptseiten
│   ├── tasks.py      # Aufgaben-Management
│   ├── grades.py     # Noten-Management
│   ├── admin.py      # Admin-Panel
│   └── statistics.py # Statistiken
├── templates/         # Jinja2 Templates
│   ├── base.html     # Basis-Template
│   ├── index.html    # Startseite
│   ├── tasks.html    # Aufgaben-Liste
│   └── ...
├── static/           # Statische Dateien
│   ├── app.css      # Haupt-Stylesheet
│   ├── app.js       # JavaScript
│   └── uploads/     # Datei-Uploads
└── instance/         # Datenbank & lokale Dateien
    └── schulbuddy.db
```

## 🔄 Development Workflow

### Hot-Reload Development

```bash
# Development mit automatischem Reload
./start.sh dev

# Logs in separatem Terminal folgen
./start.sh logs-app
```

### Code-Änderungen

1. **Frontend:** Änderungen in `templates/` und `static/` werden sofort übernommen
2. **Backend:** Container startet automatisch neu bei Python-Änderungen
3. **Database:** Änderungen an Modellen erfordern Neustart

### Database Migrations

```bash
# Datenbank zurücksetzen (Development)
./start.sh reset-db

# Backup vor größeren Änderungen
./start.sh backup
```

## 🧪 Testing

### Lokale Tests

```bash
# Unit Tests ausführen
python -m pytest

# Mit Coverage
python -m pytest --cov=app

# Einzelne Tests
python -m pytest tests/test_auth.py
```

### Integration Tests

```bash
# Container Tests
./start.sh build
./start.sh up
./start.sh health

# API Tests
curl http://localhost:5000/health
curl http://localhost:5000/api/tasks
```

## 🐛 Debugging

### Flask Debug Mode

```env
# .env
FLASK_ENV=development
FLASK_DEBUG=1
```

### Container Debugging

```bash
# Debug Shell im Container
./start.sh shell

# Logs live verfolgen
./start.sh logs -f

# Einzelne Services debuggen
docker-compose logs schulbuddy
```

### Database Debugging

```bash
# SQLite Console
sqlite3 instance/schulbuddy.db

# Database Schema anzeigen
sqlite3 instance/schulbuddy.db ".schema"

# Tabellen-Inhalt anzeigen
sqlite3 instance/schulbuddy.db "SELECT * FROM users;"
```

## 🎨 Frontend Development

### CSS/JavaScript

- **CSS:** `static/app.css` - Haupt-Stylesheet
- **JavaScript:** `static/app.js` - Client-side Logic
- **Templates:** `templates/` - Jinja2 Templates

### Live Reloading

Bei Development-Modus werden CSS/JS Änderungen sofort übernommen:

```html
<!-- Automatisches Cache-Busting -->
<link rel="stylesheet" href="{{ url_for('static', filename='app.css', v=timestamp) }}">
<script src="{{ url_for('static', filename='app.js', v=timestamp) }}"></script>
```

### Template Development

```html
<!-- Basis-Template erweitern -->
{% extends "base.html" %}

{% block title %}Meine Seite{% endblock %}

{% block content %}
<div class="container">
    <!-- Inhalt hier -->
</div>
{% endblock %}
```

## 📡 API Development

### Neue Routes hinzufügen

```python
# routes/my_feature.py
from flask import Blueprint, request, jsonify

bp = Blueprint('my_feature', __name__)

@bp.route('/api/my-endpoint', methods=['GET'])
def my_endpoint():
    return jsonify({'status': 'success'})

# In app.py registrieren
from routes import my_feature
app.register_blueprint(my_feature.bp)
```

### API Testing

```bash
# GET Request
curl http://localhost:5000/api/tasks

# POST Request
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task"}' \
  http://localhost:5000/api/tasks
```

## 🗃️ Database Development

### Neue Modelle

```python
# models.py
class MyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Nach Änderungen
./start.sh reset-db  # Development
```

### Seed Data

```python
# init_db.py erweitern
def seed_development_data():
    """Entwicklungs-Testdaten erstellen"""
    if MyModel.query.count() == 0:
        test_data = MyModel(name="Test Entry")
        db.session.add(test_data)
        db.session.commit()
```

## 🔐 Security Development

### Authentication Testing

```python
# Test verschiedene User-Rollen
def test_admin_access():
    with app.test_client() as client:
        # Login als Admin
        client.post('/login', data={'username': 'admin'})
        response = client.get('/admin')
        assert response.status_code == 200
```

### API Security

```python
# API Key Protection testen
@require_api_key
def protected_endpoint():
    return jsonify({'data': 'secret'})

# Test mit API Key
curl -H "X-API-Key: your-key" http://localhost:5000/api/protected
```

## 📦 Build & Deployment

### Docker Build

```bash
# Local Build
docker build -t schulbuddy:dev .

# Multi-Stage Build für Production
docker build --target production -t schulbuddy:prod .
```

### Environment Management

```bash
# Development
cp .env.example .env.dev

# Staging
cp .env.example .env.staging

# Production
cp .env.example .env.prod
```

## 🔧 IDE Setup

### VS Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.testing.pytestEnabled": true,
    "files.associations": {
        "*.html": "html"
    }
}
```

### PyCharm

- **Interpreter:** Virtual Environment in `venv/`
- **Run Configuration:** `app.py` als Startup
- **Templates:** Jinja2 Support aktivieren

## 📋 Development Checklist

### Vor dem Commit
- [ ] Tests laufen durch
- [ ] Linting erfolgreich
- [ ] Keine Debug-Ausgaben
- [ ] .env Änderungen in .env.example übertragen

### Vor dem Release
- [ ] Production Build erfolgreich
- [ ] Health Checks funktionieren
- [ ] Backup/Restore getestet
- [ ] Documentation aktualisiert
