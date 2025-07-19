# SchulBuddy 🎓

Eine umfassende Flask-Webanwendung für die Verwaltung von Schulaufgaben, Noten und Lernfortschritt.

## 🌟 Features

### 📝 Aufgaben-Management
- Aufgaben erstellen, bearbeiten und verwalten
- Kategorisierung nach Fächern und Aufgabentypen
- Deadline-Tracking und Prioritätsverwaltung
- Fortschrittsverfolgung und Archivierung

### 🎯 Noten-System
- Einzelnoten nach Fächern eingeben
- Zeugnisnoten-Management
- Halbjahres- und Schuljahres-Übersicht
- Automatische Durchschnittsberechnung
- Notenentwicklung und Statistiken

### ⏱️ Lern-Timer (Pomodoro)
- Pomodoro-Timer für fokussiertes Lernen
- Verschiedene Timer-Modi (25min, 45min, 90min, etc.)
- Punkte-System für Motivation
- Session-Verlauf und Statistiken
- Dashboard-Integration mit Quick-Start

### 📊 Statistiken & Analytics
- Detaillierte Lernstatistiken
- Fach-spezifische Auswertungen
- Fortschrittstracking und Trends
- Exportfunktionen (PDF, Excel)

### 🎮 Gamification
- Level-System basierend auf Aktivität
- Streak-Counter für tägliche Nutzung
- Achievement-System
- Punkte für Timer-Sessions

### ⚙️ Administration
- Flexible Schuljahr-Einstellungen
- Fach-Konfiguration
- Benutzer-Management
- System-Einstellungen

## 🚀 Installation

### Voraussetzungen
- Python 3.8+
- pip

### Setup
```bash
# Repository klonen
git clone https://github.com/TimBoBN/schulbuddy.git
cd schulbuddy

# Virtual Environment erstellen
python -m venv .venv
.venv\Scripts\activate  # Windows
# oder
source .venv/bin/activate  # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Datenbank initialisieren
python init_db.py

# Schuljahr-Einstellungen initialisieren
python init_school_settings.py

# Anwendung starten
python app.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

## 📁 Projektstruktur

```
schulbuddy/
├── app.py              # Hauptanwendung
├── config.py           # Konfiguration
├── models.py           # Datenbankmodelle
├── requirements.txt    # Dependencies
├── routes/             # Flask Blueprints
│   ├── auth.py         # Authentifizierung
│   ├── main.py         # Dashboard
│   ├── tasks.py        # Aufgaben-Management
│   ├── grades.py       # Noten-System
│   ├── timer.py        # Lern-Timer
│   ├── statistics.py   # Statistiken
│   └── admin.py        # Administration
├── templates/          # HTML Templates
├── static/             # CSS, JS, Assets
├── utils/              # Utility-Funktionen
└── dev/                # Development Tools
```

## 🛠️ Technologie-Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap 5, JavaScript, Jinja2
- **Datenbank**: SQLite (development), PostgreSQL (production)
- **Export**: ReportLab (PDF), XlsxWriter (Excel)

## 📈 Aktueller Stand

Das Projekt befindet sich in aktiver Entwicklung. Alle Hauptfunktionen sind implementiert und funktionsfähig:

- ✅ Aufgaben-Management
- ✅ Noten-System
- ✅ Lern-Timer mit Pomodoro
- ✅ Statistiken und Analytics
- ✅ Gamification-System
- ✅ Admin-Panel
- ✅ Dashboard mit Quick-Actions

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte erstelle ein Issue oder einen Pull Request für Verbesserungen.

## 📄 Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

---

**Entwickelt mit ❤️ für effektives Schulmanagement**
