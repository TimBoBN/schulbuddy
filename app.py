"""
SchulBuddy - Hauptanwendung
Eine Flask-Anwendung für die Verwaltung von Schulaufgaben, Noten und Lernfortschritt
"""
from flask import Flask
from flask_login import LoginManager
import os

from config import Config
from models import init_db, User, db
from routes import register_routes

def create_app():
    """Flask App Factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Datenbank initialisieren
    with app.app_context():
        init_db(app)
    
    # Login Manager konfigurieren
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melde dich an, um diese Seite zu sehen.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Upload-Ordner erstellen
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
    
    # Routes registrieren
    register_routes(app)
    
    # CLI-Kommando für automatische Bereinigung
    @app.cli.command()
    def cleanup_old_tasks():
        """CLI-Kommando zum Bereinigen alter Aufgaben"""
        from routes.tasks import auto_cleanup_old_tasks
        with app.app_context():
            deleted_count = auto_cleanup_old_tasks()
            print(f"Bereinigung abgeschlossen: {deleted_count} Aufgaben gelöscht")
    
    @app.cli.command()
    def cleanup_old_sessions():
        """CLI-Kommando zum Bereinigen alter Timer-Sessions"""
        from routes.timer import auto_cleanup_old_sessions
        with app.app_context():
            deleted_count = auto_cleanup_old_sessions()
            print(f"Timer-Sessions Bereinigung abgeschlossen: {deleted_count} Sessions gelöscht")
    
    @app.cli.command()
    def cleanup_all():
        """CLI-Kommando zum Bereinigen aller alten Daten"""
        from routes.tasks import auto_cleanup_old_tasks
        from routes.timer import auto_cleanup_old_sessions
        with app.app_context():
            tasks_deleted = auto_cleanup_old_tasks()
            sessions_deleted = auto_cleanup_old_sessions()
            print(f"Vollständige Bereinigung abgeschlossen:")
            print(f"- {tasks_deleted} Aufgaben gelöscht")
            print(f"- {sessions_deleted} Timer-Sessions gelöscht")
    
    return app

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    app = create_app()
    
    # Entwicklungsserver starten
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)
    
    return app

# App-Instanz erstellen
app = create_app()

if __name__ == '__main__':
    main()
