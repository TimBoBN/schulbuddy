# 📘 SchulBuddy - Schulmanager

Ein einfacher Schulmanager zur Verwaltung von Aufgaben und Noten, entwickelt mit Flask.

## Features

- ✅ **Aufgabenverwaltung**: Aufgaben mit Titel, Fach, Fälligkeitsdatum und optionalen Dateien
- 📊 **Notenverwaltung**: Noten mit automatischer Durchschnittsberechnung pro Fach
- � **Kalender-Ansicht**: Vollständiger Kalender mit FullCalendar.js für Aufgaben
- 🎨 **Fach-Farben**: Jedes Fach hat eine eigene Farbe für bessere Übersicht
- 📝 **Fach-Dropdown**: Vordefinierte Fächer-Liste mit Dropdown-Auswahl
- 🌙 **Dark Mode**: Umschaltbarer Dark/Light Mode mit localStorage-Persistierung
- �📎 **Datei-Uploads**: Unterstützung für verschiedene Dateiformate
- 🎨 **Responsive Design**: Bootstrap-basiertes UI mit modernem Design
- 💾 **Datenspeicherung**: JSON-basierte lokale Datenspeicherung

## Installation

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd schulbuddy
   ```

2. **Virtuelle Umgebung erstellen** (empfohlen)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # oder
   source venv/bin/activate  # Linux/Mac
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Anwendung starten**
   ```bash
   python app.py
   ```

5. **Browser öffnen**
   ```
   http://localhost:5000
   ```

## Projektstruktur

```
schulbuddy/
├── app.py                 # Hauptanwendung
├── config.py              # Konfiguration
├── models.py              # Datenbankmodelle
├── requirements.txt       # Python-Abhängigkeiten
├── README.md             # Dokumentation
├── LICENSE               # Lizenz
├── init_db.py            # Datenbankinitialisierung
├── static/              # Statische Dateien
│   ├── app.css          # Globale CSS-Styles
│   ├── app.js           # Globale JavaScript-Funktionen
│   ├── calendar.css     # Kalender-spezifische Styles
│   ├── calendar.js      # Kalender-JavaScript
│   └── uploads/         # Hochgeladene Dateien
├── templates/           # HTML-Templates
│   ├── index.html       # Dashboard
│   ├── base.html        # Basis-Template
│   ├── calendar_simple.html  # Kalender-Ansicht
│   ├── edit_task.html   # Aufgaben bearbeiten
│   ├── add_grade_to_task.html  # Noten hinzufügen
│   └── semester_grades.html    # Semester-Noten
└── utils/               # Hilfsfunktionen
    └── storage.py       # Datenmanagement
```

## Konfiguration

Die Anwendung kann über `config.py` konfiguriert werden:

- **Dateipfade**: Anpassung der Speicherorte
- **Upload-Einstellungen**: Erlaubte Dateitypen und Größenbeschränkungen
- **Flask-Einstellungen**: Debug-Modus, Secret Key

## Unterstützte Dateiformate

- **Dokumente**: PDF, DOC, DOCX, TXT
- **Bilder**: PNG, JPG, JPEG, GIF
- **Maximale Dateigröße**: 16MB

## Neue Features (v2.0)

### 📅 Kalender-Ansicht
- Vollständiger Kalender mit FullCalendar.js
- Monats-, Wochen- und Listenansicht
- Farbkodierte Aufgaben nach Fächern
- Klickbare Events mit Detailinformationen

### 🎨 Fach-Farben
- 20 vordefinierte Fächer mit eigenen Farben
- Automatische Farbzuordnung für neue Fächer
- Konsistente Farbgebung in allen Ansichten
- Fächer-Legende im Kalender

### 📝 Fach-Dropdown
- Intelligente Dropdown-Liste mit allen Fächern
- Kombination aus vordefinierten und bereits verwendeten Fächern
- Einfache Auswahl ohne Tippfehler

### 🔧 Robuste Datenbehandlung
- Automatische Datenreparatur bei Inkonsistenzen
- Migration alter Datenformate
- Fehlerbehandlung für ungültige Daten
- Manuelle Reparatur-Funktion über UI

### 🌙 Dark Mode
- Vollständig implementierter Dark/Light Mode
- Persistierung der Einstellung im localStorage
- Sanfte Übergänge zwischen den Modi
- Konsistente Darstellung aller Elemente

## Notensystem

Das System verwendet das deutsche Notensystem (1-6):
- 1-2: Sehr gut/Gut (grün)
- 3-4: Befriedigend/Ausreichend (gelb)
- 5-6: Mangelhaft/Ungenügend (rot)

## Entwicklung

### Neue Features hinzufügen

1. Erweitere die `DataManager`-Klasse in `utils/storage.py`
2. Füge neue Routen in `app.py` hinzu
3. Erstelle oder erweitere Templates in `templates/`

### Styling anpassen

Das UI verwendet Bootstrap 5. Eigene Styles können in `static/style.css` hinzugefügt werden.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` für Details.

## Beitragen

Contributions sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.
