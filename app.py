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
    
    # Ensure instance directory exists
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
    os.makedirs(instance_dir, exist_ok=True)
    
    # Create database file if it doesn't exist
    db_path = app.config.get('DATABASE_PATH', os.path.join(instance_dir, "schulbuddy.db"))
    if not os.path.exists(db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.close()
        print(f"Created database file: {db_path}")
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
            
            # Create admin user if not exists
            from models import User
            if not User.query.filter_by(id=1).first():
                admin = User(
                    username="admin", email="admin@schulbuddy.local", is_admin=True
                )
                admin.set_password("admin")
                db.session.add(admin)
                db.session.commit()
                print("Admin user created!")
        except Exception as e:
            print(f"Database initialization error: {e}")
            raise
    
    # Login Manager konfigurieren
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bitte melde dich an, um diese Seite zu sehen.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
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
    
    return app

def main():
    """Hauptfunktion zum Starten der Anwendung"""
    app = create_app()
    
    # Entwicklungsserver starten
    if __name__ == '__main__':
        from config import Config
        app.run(debug=True, host=Config.HOST, port=Config.PORT)
    
    return app

# App-Instanz erstellen
app = create_app()

if __name__ == '__main__':
    main()
