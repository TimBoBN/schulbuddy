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

    # Sicherstellen dass notwendige Verzeichnisse existieren
    db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "").replace("sqlite:///", "")
    if db_path and not db_path.startswith(":memory:"):
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            # Setze Berechtigungen für das Datenbankverzeichnis
            try:
                os.chmod(db_dir, 0o755)
            except (OSError, PermissionError):
                pass

    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # Datenbank initialisieren (mit Fehlerbehandlung)
    with app.app_context():
        try:
            init_db(app)
        except Exception as e:
            print(f"⚠️ Datenbankinitialisierung fehlgeschlagen: {e}")
            print("📝 Versuche später erneut über /init-db")

            # Erstelle eine Route für manuelle DB-Initialisierung
            @app.route("/init-db")
            def manual_init_db():
                try:
                    init_db(app)
                    return {
                        "status": "success",
                        "message": "Datenbank erfolgreich initialisiert",
                    }, 200
                except Exception as err:
                    return {"status": "error", "message": str(err)}, 500

    # Login Manager konfigurieren
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melde dich an, um diese Seite zu sehen."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routes registrieren
    register_routes(app)

    # Health-Check-Endpoint für Docker
    @app.route("/health")
    def health_check():
        """Health-Check-Endpoint für Container-Monitoring"""
        try:
            # Einfacher Datenbankverbindungstest
            db.session.execute("SELECT 1")
            return {"status": "healthy", "message": "SchulBuddy is running"}, 200
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}, 500

    # CLI-Kommando für automatische Bereinigung
    @app.cli.command()
    def cleanup_old_tasks():
        """CLI-Kommando zum Bereinigen alter Aufgaben"""
        from routes.tasks import auto_cleanup_old_tasks

        with app.app_context():
            deleted_count = auto_cleanup_old_tasks()
            print(f"Bereinigung abgeschlossen: {deleted_count} Aufgaben gelöscht")

    return app


def main():
    """Hauptfunktion zum Starten der Anwendung"""
    app = create_app()

    # Entwicklungsserver starten
    if __name__ == "__main__":
        app.run(debug=True, host="0.0.0.0", port=5000)

    return app


# App-Instanz erstellen
app = create_app()

if __name__ == "__main__":
    main()
