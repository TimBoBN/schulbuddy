from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pyotp
import qrcode
import io
import base64
import json
import secrets

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
    
    # 2FA Felder
    totp_secret = db.Column(db.String(32), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    backup_codes = db.Column(db.Text, nullable=True)  # JSON string mit Backup-Codes
    
    # API Security
    api_key = db.Column(db.String(64), nullable=True)  # API-Key für sicheren Zugriff
    api_key_created_at = db.Column(db.DateTime, nullable=True)
    
    # Gamification & Statistiken
    total_points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    # Einstellungen
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=False)
    reminder_hours = db.Column(db.Integer, default=24)  # Stunden vor Deadline
    
    # Beziehungen
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    statistics = db.relationship('UserStatistic', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Setze verschlüsseltes Passwort"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Prüfe Passwort"""
        return check_password_hash(self.password_hash, password)
    
    def generate_totp_secret(self):
        """Generiere TOTP Secret für 2FA"""
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Generiere TOTP URI für QR-Code"""
        if not self.totp_secret:
            self.generate_totp_secret()
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='SchulBuddy'
        )
    
    def verify_totp(self, token):
        """Verifiziere TOTP Token"""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=2)
    
    def generate_qr_code(self):
        """Generiere QR-Code für 2FA Setup"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.get_totp_uri())
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return base64.b64encode(buf.getvalue()).decode()
    
    def generate_api_key(self):
        """Generiere neuen API-Key"""
        self.api_key = secrets.token_urlsafe(32)  # 32 Bytes = 256 Bit
        self.api_key_created_at = datetime.utcnow()
        return self.api_key
    
    def verify_api_key(self, provided_key):
        """Verifiziere API-Key"""
        if not self.api_key or not provided_key:
            return False
        return secrets.compare_digest(self.api_key, provided_key)
    
    def get_or_create_api_key(self):
        """Hole existierenden API-Key oder erstelle neuen"""
        if not self.api_key:
            self.generate_api_key()
            db.session.commit()
        return self.api_key
    
    def add_points(self, points, activity_type, activity_data=None):
        """Füge Punkte hinzu und logge Aktivität"""
        self.total_points += points
        
        # Level-up basierend auf Punkten
        new_level = (self.total_points // 100) + 1
        if new_level > self.level:
            self.level = new_level
            # Achievement für Level-up
            self.check_achievements()
        
        # Aktivität loggen
        log = ActivityLog(
            user_id=self.id,
            activity_type=activity_type,
            activity_data=json.dumps(activity_data) if activity_data else None,
            points_earned=points
        )
        db.session.add(log)
        db.session.commit()
    
    def update_streak(self):
        """Aktualisiere Lernstreak"""
        from datetime import date
        today = date.today()
        
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            if days_diff == 1:
                # Streak fortsetzen
                self.current_streak += 1
            elif days_diff > 1:
                # Streak unterbrochen
                self.current_streak = 1
        else:
            # Erster Tag
            self.current_streak = 1
        
        self.last_activity_date = today
        
        # Längsten Streak aktualisieren
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        db.session.commit()
        self.check_achievements()
    
    def check_achievements(self):
        """Prüfe und verleihe Achievements"""
        achievements = Achievement.query.filter_by(is_active=True).all()
        
        for achievement in achievements:
            # Prüfe ob bereits erhalten
            if UserAchievement.query.filter_by(user_id=self.id, achievement_id=achievement.id).first():
                continue
            
            earned = False
            
            if achievement.condition_type == 'streak':
                earned = self.current_streak >= achievement.condition_value
            elif achievement.condition_type == 'level':
                earned = self.level >= achievement.condition_value
            elif achievement.condition_type == 'points':
                earned = self.total_points >= achievement.condition_value
            elif achievement.condition_type == 'tasks_completed':
                completed_tasks = Task.query.filter_by(user_id=self.id, completed=True).count()
                earned = completed_tasks >= achievement.condition_value
            
            if earned:
                user_achievement = UserAchievement(user_id=self.id, achievement_id=achievement.id)
                db.session.add(user_achievement)
                
                # Benachrichtigung erstellen
                notification = Notification(
                    user_id=self.id,
                    title=f"Achievement erhalten: {achievement.name}",
                    message=f"Glückwunsch! Du hast das Achievement '{achievement.name}' erhalten: {achievement.description}",
                    notification_type='achievement'
                )
                db.session.add(notification)
        
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    """Aufgaben-Modell"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    file = db.Column(db.String(255), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime, nullable=True)  # Wann wurde die Aufgabe erledigt
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
            'filename': self.file,  # Alias für Kompatibilität
            'completed': self.completed,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'task_type': self.task_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_date': self.created_at.strftime('%Y-%m-%d') if self.created_at else None
        }

class Grade(db.Model):
    """Noten-Modell"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=True)
    semester = db.Column(db.Integer, nullable=False, default=1)  # 1 oder 2 für Halbjahr
    school_year = db.Column(db.String(10), nullable=False, default='2024/25')  # z.B. "2024/25"
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=True)  # Verknüpfung zu Aufgabe
    is_final_grade = db.Column(db.Boolean, default=False)  # Zeugnisnote (Endnote)
    grade_type = db.Column(db.String(20), default='regular')  # 'regular', 'final', 'exam', 'oral'
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
            'is_final_grade': self.is_final_grade,
            'grade_type': self.grade_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AppSettings(db.Model):
    """App-Einstellungen"""
    __tablename__ = 'app_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        """Hole eine Einstellung"""
        setting = AppSettings.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Setze eine Einstellung"""
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            if description:
                setting.description = description
        else:
            setting = AppSettings(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting
    
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

class Achievement(db.Model):
    """Achievements für Gamification"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)
    condition_type = db.Column(db.String(50), nullable=False)  # 'streak', 'tasks_completed', 'grade_average', etc.
    condition_value = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAchievement(db.Model):
    """Verknüpfung zwischen Benutzer und Achievements"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    achievement = db.relationship('Achievement', backref='user_achievements')

class ActivityLog(db.Model):
    """Aktivitäts-Log für Statistiken"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'task_completed', 'grade_added', 'login', etc.
    activity_data = db.Column(db.Text, nullable=True)  # JSON string mit zusätzlichen Daten
    points_earned = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    """Benachrichtigungen für Benutzer"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'reminder', 'achievement', 'deadline', etc.
    is_read = db.Column(db.Boolean, default=False)
    scheduled_for = db.Column(db.DateTime, nullable=True)  # Für geplante Benachrichtigungen
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications')

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
        
        # Erstelle Standard-Achievements
        init_achievements()
        
        # Migriere existierende Benutzer-Statistiken
        migrate_user_statistics()


def migrate_user_statistics():
    """Migriert existierende Daten zu UserStatistic"""
    try:
        # Prüfe, ob UserStatistic-Tabelle leer ist
        if UserStatistic.query.count() > 0:
            return  # Bereits migriert
        
        print("Migriere Benutzer-Statistiken...")
        
        # Für jeden Benutzer
        for user in User.query.all():
            # Sammle alle Daten der letzten 30 Tage (nicht 365 für bessere Performance)
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            current_date = start_date
            while current_date <= end_date:
                # Prüfe, ob für diesen Tag bereits Statistiken existieren
                if not UserStatistic.query.filter_by(user_id=user.id, date=current_date).first():
                    UserStatistic.update_daily_stats(user.id, current_date)
                current_date += timedelta(days=1)
        
        print("Statistik-Migration abgeschlossen!")
        
    except Exception as e:
        print(f"Fehler bei der Statistik-Migration: {e}")
        db.session.rollback()

def init_achievements():
    """Initialisiere Standard-Achievements"""
    try:
        if Achievement.query.count() == 0:
            achievements = [
                # Streak Achievements
                Achievement(name="Erste Schritte", description="Erster Tag aktiv", icon="🌟", points=10, condition_type="streak", condition_value=1),
                Achievement(name="Dranbleiben", description="3 Tage in Folge aktiv", icon="🔥", points=25, condition_type="streak", condition_value=3),
                Achievement(name="Wochenkämpfer", description="7 Tage in Folge aktiv", icon="⚡", points=50, condition_type="streak", condition_value=7),
                Achievement(name="Unaufhaltsam", description="14 Tage in Folge aktiv", icon="🚀", points=100, condition_type="streak", condition_value=14),
                Achievement(name="Lernmaschine", description="30 Tage in Folge aktiv", icon="🏆", points=200, condition_type="streak", condition_value=30),
                
                # Level Achievements
                Achievement(name="Aufsteiger", description="Level 2 erreicht", icon="📈", points=20, condition_type="level", condition_value=2),
                Achievement(name="Fortgeschritten", description="Level 5 erreicht", icon="🎯", points=50, condition_type="level", condition_value=5),
                Achievement(name="Experte", description="Level 10 erreicht", icon="🧠", points=100, condition_type="level", condition_value=10),
                Achievement(name="Meister", description="Level 20 erreicht", icon="👑", points=200, condition_type="level", condition_value=20),
                
                # Punkte Achievements
                Achievement(name="Sammler", description="100 Punkte gesammelt", icon="💰", points=25, condition_type="points", condition_value=100),
                Achievement(name="Fleißig", description="500 Punkte gesammelt", icon="💎", points=50, condition_type="points", condition_value=500),
                Achievement(name="Punktejäger", description="1000 Punkte gesammelt", icon="🎖️", points=100, condition_type="points", condition_value=1000),
                Achievement(name="Legende", description="2000 Punkte gesammelt", icon="🏅", points=200, condition_type="points", condition_value=2000),
                
                # Task Achievements
                Achievement(name="Starter", description="Erste Aufgabe erledigt", icon="✅", points=15, condition_type="tasks_completed", condition_value=1),
                Achievement(name="Produktiv", description="10 Aufgaben erledigt", icon="📋", points=30, condition_type="tasks_completed", condition_value=10),
                Achievement(name="Aufgabenprofi", description="25 Aufgaben erledigt", icon="📝", points=75, condition_type="tasks_completed", condition_value=25),
                Achievement(name="Aufgabenheld", description="50 Aufgaben erledigt", icon="💪", points=150, condition_type="tasks_completed", condition_value=50),
                Achievement(name="Aufgabengott", description="100 Aufgaben erledigt", icon="⭐", points=300, condition_type="tasks_completed", condition_value=100),
            ]
            
            for achievement in achievements:
                db.session.add(achievement)
            
            db.session.commit()
            print("Standard-Achievements erstellt!")
            
    except Exception as e:
        print(f"Fehler beim Erstellen der Achievements: {e}")
        db.session.rollback()


class UserStatistic(db.Model):
    """Benutzerstatistiken für historische Daten (überleben Aufgaben-Löschungen)"""
    __tablename__ = 'user_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Tägliche Statistiken
    tasks_created = db.Column(db.Integer, default=0)
    tasks_completed = db.Column(db.Integer, default=0)
    grades_added = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    
    # Fach-spezifische Daten (JSON)
    subject_tasks = db.Column(db.Text, default='{}')  # JSON: {subject: count}
    subject_grades = db.Column(db.Text, default='{}')  # JSON: {subject: [grades]}
    
    # Aufgaben-Typ Verteilung (JSON)
    task_types = db.Column(db.Text, default='{}')  # JSON: {type: count}
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserStatistic {self.user_id}:{self.date}>'
    
    def get_subject_tasks(self):
        """Gibt Fach-Aufgaben als Dictionary zurück"""
        try:
            return json.loads(self.subject_tasks)
        except:
            return {}
    
    def set_subject_tasks(self, data):
        """Setzt Fach-Aufgaben als JSON"""
        self.subject_tasks = json.dumps(data)
    
    def get_subject_grades(self):
        """Gibt Fach-Noten als Dictionary zurück"""
        try:
            return json.loads(self.subject_grades)
        except:
            return {}
    
    def set_subject_grades(self, data):
        """Setzt Fach-Noten als JSON"""
        self.subject_grades = json.dumps(data)
    
    def get_task_types(self):
        """Gibt Aufgaben-Typen als Dictionary zurück"""
        try:
            return json.loads(self.task_types)
        except:
            return {}
    
    def set_task_types(self, data):
        """Setzt Aufgaben-Typen als JSON"""
        self.task_types = json.dumps(data)
    
    @staticmethod
    def update_daily_stats(user_id, date_obj=None):
        """Aktualisiert die täglichen Statistiken für einen Benutzer"""
        if date_obj is None:
            date_obj = datetime.now().date()
        
        # Prüfe, ob bereits Statistik für diesen Tag existiert
        stat = UserStatistic.query.filter_by(
            user_id=user_id,
            date=date_obj
        ).first()
        
        if not stat:
            stat = UserStatistic(user_id=user_id, date=date_obj)
            db.session.add(stat)
        
        # Zähle Aufgaben für diesen Tag
        tasks_created = Task.query.filter(
            Task.user_id == user_id,
            Task.created_at >= date_obj,
            Task.created_at < date_obj + timedelta(days=1)
        ).count()
        
        tasks_completed = Task.query.filter(
            Task.user_id == user_id,
            Task.completed == True,
            Task.completed_date >= date_obj,
            Task.completed_date < date_obj + timedelta(days=1)
        ).count()
        
        # Zähle Noten für diesen Tag
        grades_added = Grade.query.filter(
            Grade.user_id == user_id,
            Grade.timestamp >= date_obj,
            Grade.timestamp < date_obj + timedelta(days=1)
        ).count()
        
        # Aktualisiere Statistiken
        stat.tasks_created = tasks_created
        stat.tasks_completed = tasks_completed
        stat.grades_added = grades_added
        
        # Fach-spezifische Statistiken
        subject_tasks = {}
        subject_grades = {}
        task_types = {}
        
        # Aufgaben nach Fach
        for task in Task.query.filter(
            Task.user_id == user_id,
            Task.completed == True,
            Task.completed_date >= date_obj,
            Task.completed_date < date_obj + timedelta(days=1)
        ).all():
            subject_tasks[task.subject] = subject_tasks.get(task.subject, 0) + 1
            task_types[task.task_type] = task_types.get(task.task_type, 0) + 1
        
        # Noten nach Fach
        for grade in Grade.query.filter(
            Grade.user_id == user_id,
            Grade.timestamp >= date_obj,
            Grade.timestamp < date_obj + timedelta(days=1)
        ).all():
            if grade.subject not in subject_grades:
                subject_grades[grade.subject] = []
            subject_grades[grade.subject].append(grade.grade)
        
        stat.set_subject_tasks(subject_tasks)
        stat.set_subject_grades(subject_grades)
        stat.set_task_types(task_types)
        
        db.session.commit()
        return stat
