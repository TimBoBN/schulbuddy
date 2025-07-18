from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Benutzer-Modell für Login-System"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        """Setze verschlüsseltes Passwort"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Prüfe Passwort"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    """Aufgaben-Modell"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    file = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    task_type = db.Column(db.String(50), default='homework')  # 'homework', 'exam', 'project'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Konvertiere zu Dictionary für API"""
        return {
            'id': self.id,
            'title': self.title,
            'subject': self.subject,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'file': self.file,
            'completed': self.completed,
            'task_type': self.task_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Grade(db.Model):
    """Noten-Modell"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=True)
    semester = db.Column(db.Integer, nullable=False, default=1)  # 1 oder 2 für Halbjahr
    school_year = db.Column(db.String(10), nullable=False, default='2024/25')  # z.B. "2024/25"
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # Verknüpfung zu Aufgabe
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Konvertiere zu Dictionary für API"""
        return {
            'id': self.id,
            'subject': self.subject,
            'grade': self.grade,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'semester': self.semester,
            'school_year': self.school_year,
            'task_id': self.task_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

def init_db(app):
    """Initialisiere die Datenbank"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Datenbank initialisiert!")
        
        # Erstelle Admin-Benutzer falls nicht vorhanden (erst nach create_all!)
        try:
            if not User.query.filter_by(id=1).first():
                admin = User(username='admin', email='admin@schulbuddy.local', is_admin=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Standard-Admin-Benutzer erstellt (admin / admin123)")
        except Exception as e:
            print(f"Fehler beim Erstellen des Admin-Users: {e}")
            db.session.rollback()
