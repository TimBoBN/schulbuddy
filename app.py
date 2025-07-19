"""
SchulBuddy - Hauptanwendung
Eine Flask-Anwendung für die Verwaltung von Schulaufgaben, Noten und Lernfortschritt
"""

from flask import Flask
from flask_login import LoginManager
import os
from datetime import datetime

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

    # Einfacher Root-Endpoint für Tests
    @app.route("/ping")
    def ping():
        """Einfacher Ping-Endpoint ohne Authentifizierung"""
        return {"message": "pong", "timestamp": datetime.now().isoformat()}, 200

    # Health-Check-Endpoint für Docker
    @app.route("/health")
    def health_check():
        """Health-Check-Endpoint für Container-Monitoring"""
        health_status = {"status": "healthy", "checks": {}}
        status_code = 200

        try:
            # Test Flask App
            health_status["checks"]["flask"] = {
                "status": "ok",
                "message": "Flask app running",
            }

            # Test Datenbank
            try:
                with app.app_context():
                    result = db.session.execute("SELECT 1").scalar()
                    if result == 1:
                        health_status["checks"]["database"] = {
                            "status": "ok",
                            "message": "Database connection successful",
                        }
                    else:
                        health_status["checks"]["database"] = {
                            "status": "warning",
                            "message": "Database query returned unexpected result",
                        }
            except Exception as db_error:
                health_status["checks"]["database"] = {
                    "status": "error",
                    "message": f"Database connection failed: {str(db_error)}",
                }
                health_status["status"] = "degraded"

            # Test Datenbankverzeichnis
            try:
                db_path = app.config.get("SQLALCHEMY_DATABASE_URI", "").replace(
                    "sqlite:///", ""
                )
                if db_path and not db_path.startswith(":memory:"):
                    db_dir = os.path.dirname(db_path)
                    if os.path.exists(db_dir):
                        health_status["checks"]["db_directory"] = {
                            "status": "ok",
                            "message": f"Database directory exists: {db_dir}",
                        }
                    else:
                        health_status["checks"]["db_directory"] = {
                            "status": "warning",
                            "message": f"Database directory missing: {db_dir}",
                        }
                else:
                    health_status["checks"]["db_directory"] = {
                        "status": "ok",
                        "message": "Using in-memory or relative database",
                    }
            except Exception as dir_error:
                health_status["checks"]["db_directory"] = {
                    "status": "error",
                    "message": f"Directory check failed: {str(dir_error)}",
                }

            health_status["message"] = "SchulBuddy health check completed"
            health_status["timestamp"] = datetime.now().isoformat()

        except Exception as e:
            health_status = {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }
            status_code = 500

        return health_status, status_code

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
