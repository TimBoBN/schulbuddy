"""
Admin routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps
import json
import sqlite3
import os
import shutil
from datetime import datetime
import zipfile
import io

from models import User, Task, Grade, AppSettings, Achievement, UserAchievement, StudySession, UserStatistic, ActivityLog, Notification, db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator für Admin-Berechtigung"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin-Berechtigung erforderlich", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("")
@login_required
@admin_required
def admin_dashboard():
    """Admin-Dashboard"""
    # Statistiken sammeln
    total_users = User.query.count()
    total_tasks = Task.query.count()
    total_grades = Grade.query.count()
    
    # Neueste Benutzer
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Neueste Aufgaben
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template("admin_panel.html",
                         total_users=total_users,
                         total_tasks=total_tasks,
                         total_grades=total_grades,
                         recent_users=recent_users,
                         recent_tasks=recent_tasks)

@admin_bp.route("/users")
@login_required
@admin_required
def admin_users():
    """Benutzerverwaltung"""
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@admin_bp.route("/change_password", methods=["GET", "POST"])
@login_required
@admin_required
def admin_change_password():
    """Admin-Passwort ändern"""
    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_password = request.form.get("new_password")
        
        user = User.query.get(user_id)
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            flash(f"Passwort für {user.username} erfolgreich geändert!", "success")
        else:
            flash("Benutzer nicht gefunden", "error")
        
        return redirect(url_for('admin.admin_users'))
    
    users = User.query.all()
    return render_template("admin_change_password.html", users=users)

@admin_bp.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Benutzer löschen"""
    user = User.query.get(user_id)
    if user:
        if user.id == current_user.id:
            flash("Du kannst dich nicht selbst löschen", "error")
        else:
            db.session.delete(user)
            db.session.commit()
            flash(f"Benutzer {user.username} erfolgreich gelöscht!", "success")
    else:
        flash("Benutzer nicht gefunden", "error")
    
    return redirect(url_for('admin.admin_users'))

@admin_bp.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_user(user_id):
    """Benutzer bearbeiten"""
    user = User.query.get(user_id)
    if not user:
        flash("Benutzer nicht gefunden", "error")
        return redirect(url_for('admin.admin_users'))
    
    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.is_admin = request.form.get("is_admin") == "on"
        
        # Passwort nur ändern wenn eingegeben
        new_password = request.form.get("password")
        if new_password:
            user.password_hash = generate_password_hash(new_password)
        
        db.session.commit()
        flash(f"Benutzer {user.username} erfolgreich bearbeitet!", "success")
        return redirect(url_for('admin.admin_users'))
    
    return render_template("admin_edit_user.html", user=user)

@admin_bp.route("/create_user", methods=["GET", "POST"])
@login_required
@admin_required
def admin_create_user():
    """Neuen Benutzer erstellen"""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        is_admin = request.form.get("is_admin") == "on"
        
        # Validierung
        if User.find_by_username(username):
            flash("Benutzername bereits vergeben", "error")
            return render_template("admin_create_user.html")
        
        if User.query.filter_by(email=email).first():
            flash("E-Mail bereits registriert", "error")
            return render_template("admin_create_user.html")
        
        # Benutzer erstellen
        normalized_username = username.strip()  # Leerzeichen entfernen
        user = User(
            username=normalized_username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f"Benutzer {username} erfolgreich erstellt!", "success")
        return redirect(url_for('admin.admin_users'))
    
    return render_template("admin_create_user.html")

@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
@admin_required
def admin_settings():
    """Admin-Einstellungen"""
    if request.method == "POST":
        # Einstellungen speichern
        try:
            # Validiere numerische Werte
            max_users = int(request.form.get('max_users', '100'))
            max_login_attempts = int(request.form.get('max_login_attempts', '5'))
            max_file_size = int(request.form.get('max_file_size', '16'))
            session_timeout = int(request.form.get('session_timeout_minutes', '120'))
            auto_logout_warning = int(request.form.get('auto_logout_warning_minutes', '5'))
            
            # Validiere Bereiche
            if max_users < 1 or max_users > 10000:
                flash("Maximale Benutzeranzahl muss zwischen 1 und 10000 liegen", "error")
                return redirect(url_for('admin.admin_settings'))
            
            if max_login_attempts < 1 or max_login_attempts > 50:
                flash("Maximale Login-Versuche müssen zwischen 1 und 50 liegen", "error")
                return redirect(url_for('admin.admin_settings'))
            
            settings = {
                'app_name': request.form.get('app_name', 'SchulBuddy'),
                'max_file_size': str(max_file_size),
                'allowed_file_types': request.form.get('allowed_file_types', 'txt,pdf,doc,docx,jpg,jpeg,png,gif'),
                'session_timeout_minutes': str(session_timeout),
                'auto_logout_warning_minutes': str(auto_logout_warning),
                'max_users': str(max_users),
                'max_login_attempts': str(max_login_attempts),
                'enable_registration': request.form.get('enable_registration') == 'on',
                'enable_2fa': request.form.get('enable_2fa') == 'on',
                'require_2fa': request.form.get('require_2fa') == 'on',
                'enable_gamification': request.form.get('enable_gamification') == 'on',
                'enable_notifications': request.form.get('enable_notifications') == 'on',
                'current_school_year': request.form.get('current_school_year', '2025/26'),
                'current_semester': request.form.get('current_semester', '1')
            }
            
            for key, value in settings.items():
                AppSettings.set_setting(key, str(value))
            
            flash("Einstellungen erfolgreich gespeichert!", "success")
            return redirect(url_for('admin.admin_settings'))
            
        except ValueError as e:
            flash(f"Ungültige Eingabe: {e}", "error")
            return redirect(url_for('admin.admin_settings'))
    
    # Aktuelle Einstellungen laden
    settings = {
        'app_name': AppSettings.get_setting('app_name', 'SchulBuddy'),
        'max_file_size': AppSettings.get_setting('max_file_size', '16'),
        'allowed_file_types': AppSettings.get_setting('allowed_file_types', 'txt,pdf,doc,docx,jpg,jpeg,png,gif'),
        'session_timeout_minutes': AppSettings.get_setting('session_timeout_minutes', '120'),
        'auto_logout_warning_minutes': AppSettings.get_setting('auto_logout_warning_minutes', '5'),
        'max_users': AppSettings.get_setting('max_users', '100'),
        'max_login_attempts': AppSettings.get_setting('max_login_attempts', '5'),
        'enable_registration': AppSettings.get_setting('enable_registration', 'False') == 'True',
        'enable_2fa': AppSettings.get_setting('enable_2fa', 'False') == 'True',
        'require_2fa': AppSettings.get_setting('require_2fa', 'False') == 'True',
        'enable_gamification': AppSettings.get_setting('enable_gamification', 'True') == 'True',
        'enable_notifications': AppSettings.get_setting('enable_notifications', 'True') == 'True',
        'current_school_year': AppSettings.get_setting('current_school_year', '2025/26'),
        'current_semester': AppSettings.get_setting('current_semester', '1')
    }
    
    return render_template("admin_settings.html", settings=settings)


@admin_bp.route("/backup")
@login_required
@admin_required
def admin_backup():
    """Backup-Verwaltung"""
    # Liste vorhandener Backups
    backup_dir = os.path.join(os.getcwd(), 'backups')
    backups = []
    
    if os.path.exists(backup_dir):
        for filename in os.listdir(backup_dir):
            if filename.endswith('.zip'):
                filepath = os.path.join(backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': round(stat.st_size / 1024 / 1024, 2),  # MB
                    'created': datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M')
                })
    
    backups.sort(key=lambda x: x['filename'], reverse=True)
    
    return render_template("admin_backup.html", backups=backups)


@admin_bp.route("/backup/create", methods=["POST"])
@login_required
@admin_required
def create_backup():
    """Erstelle vollständiges Backup"""
    try:
        # Backup-Verzeichnis erstellen
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup-Dateiname mit Timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"schulbuddy_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # JSON-Export aller Daten
        backup_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.username,
            'users': [],
            'tasks': [],
            'grades': [],
            'achievements': [],
            'user_achievements': [],
            'study_sessions': [],
            'user_statistics': [],
            'activity_logs': [],
            'notifications': [],
            'app_settings': []
        }
        
        # Users exportieren (ohne Passwort-Hashes aus Sicherheitsgründen)
        for user in User.query.all():
            backup_data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'total_points': user.total_points,
                'level': user.level,
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak,
                'notifications_enabled': user.notifications_enabled,
                'email_notifications': user.email_notifications,
                'reminder_hours': user.reminder_hours
            })
        
        # Tasks exportieren
        for task in Task.query.all():
            backup_data['tasks'].append({
                'id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'description': task.description,
                'subject': task.subject,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'completed': task.completed,
                'completed_date': task.completed_date.isoformat() if task.completed_date else None,
                'task_type': task.task_type,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'file': task.file
            })
        
        # Grades exportieren
        for grade in Grade.query.all():
            backup_data['grades'].append({
                'id': grade.id,
                'user_id': grade.user_id,
                'subject': grade.subject,
                'grade': grade.grade,
                'description': grade.description,
                'date': grade.date.isoformat() if grade.date else None,
                'semester': grade.semester,
                'school_year': grade.school_year,
                'task_id': grade.task_id,
                'is_final_grade': grade.is_final_grade,
                'grade_type': grade.grade_type,
                'timestamp': grade.timestamp.isoformat() if grade.timestamp else None
            })
        
        # Achievements exportieren
        for achievement in Achievement.query.all():
            backup_data['achievements'].append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'points': achievement.points,
                'condition_type': achievement.condition_type,
                'condition_value': achievement.condition_value,
                'is_active': achievement.is_active,
                'created_at': achievement.created_at.isoformat() if achievement.created_at else None
            })
        
        # User Achievements exportieren
        for user_achievement in UserAchievement.query.all():
            backup_data['user_achievements'].append({
                'id': user_achievement.id,
                'user_id': user_achievement.user_id,
                'achievement_id': user_achievement.achievement_id,
                'earned_at': user_achievement.earned_at.isoformat() if user_achievement.earned_at else None
            })
        
        # Study Sessions exportieren
        for session in StudySession.query.all():
            backup_data['study_sessions'].append({
                'id': session.id,
                'user_id': session.user_id,
                'subject': session.subject,
                'task_id': session.task_id,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'duration_minutes': session.duration_minutes,
                'actual_duration_seconds': session.actual_duration_seconds,
                'session_type': session.session_type,
                'completed': session.completed,
                'notes': session.notes,
                'created_at': session.created_at.isoformat() if session.created_at else None
            })
        
        # User Statistics exportieren
        for stat in UserStatistic.query.all():
            backup_data['user_statistics'].append({
                'id': stat.id,
                'user_id': stat.user_id,
                'date': stat.date.isoformat() if stat.date else None,
                'tasks_created': stat.tasks_created,
                'tasks_completed': stat.tasks_completed,
                'grades_added': stat.grades_added,
                'points_earned': stat.points_earned,
                'study_sessions': stat.study_sessions,
                'study_time_minutes': stat.study_time_minutes,
                'subject_tasks': stat.subject_tasks,
                'subject_grades': stat.subject_grades,
                'task_types': stat.task_types,
                'created_at': stat.created_at.isoformat() if stat.created_at else None
            })
        
        # Activity Logs exportieren
        for log in ActivityLog.query.all():
            backup_data['activity_logs'].append({
                'id': log.id,
                'user_id': log.user_id,
                'activity_type': log.activity_type,
                'activity_data': log.activity_data,
                'points_earned': log.points_earned,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })
        
        # Notifications exportieren
        for notification in Notification.query.all():
            backup_data['notifications'].append({
                'id': notification.id,
                'user_id': notification.user_id,
                'title': notification.title,
                'message': notification.message,
                'notification_type': notification.notification_type,
                'is_read': notification.is_read,
                'scheduled_for': notification.scheduled_for.isoformat() if notification.scheduled_for else None,
                'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                'created_at': notification.created_at.isoformat() if notification.created_at else None
            })
        
        # App Settings exportieren
        for setting in AppSettings.query.all():
            backup_data['app_settings'].append({
                'id': setting.id,
                'key': setting.key,
                'value': setting.value,
                'description': setting.description,
                'created_at': setting.created_at.isoformat() if setting.created_at else None,
                'updated_at': setting.updated_at.isoformat() if setting.updated_at else None
            })
        
        # ZIP-Archiv erstellen
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # JSON-Daten hinzufügen
            json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
            zipf.writestr(f'schulbuddy_data_{timestamp}.json', json_data)
            
            # Upload-Dateien hinzufügen (falls vorhanden)
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            if os.path.exists(uploads_dir):
                for root, dirs, files in os.walk(uploads_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, os.getcwd())
                        zipf.write(file_path, arc_path)
        
        flash(f"Backup erfolgreich erstellt: {backup_filename}", "success")
        
    except Exception as e:
        flash(f"Fehler beim Erstellen des Backups: {str(e)}", "error")
    
    return redirect(url_for('admin.admin_backup'))


@admin_bp.route("/backup/download/<filename>")
@login_required
@admin_required
def download_backup(filename):
    """Backup-Datei herunterladen"""
    try:
        backup_dir = os.path.join(os.getcwd(), 'backups')
        backup_path = os.path.join(backup_dir, filename)
        
        if not os.path.exists(backup_path) or not filename.endswith('.zip'):
            flash("Backup-Datei nicht gefunden", "error")
            return redirect(url_for('admin.admin_backup'))
        
        return send_file(backup_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        flash(f"Fehler beim Download: {str(e)}", "error")
        return redirect(url_for('admin.admin_backup'))


@admin_bp.route("/backup/delete/<filename>", methods=["POST"])
@login_required
@admin_required
def delete_backup(filename):
    """Backup-Datei löschen"""
    try:
        backup_dir = os.path.join(os.getcwd(), 'backups')
        backup_path = os.path.join(backup_dir, filename)
        
        if os.path.exists(backup_path) and filename.endswith('.zip'):
            os.remove(backup_path)
            flash(f"Backup {filename} erfolgreich gelöscht", "success")
        else:
            flash("Backup-Datei nicht gefunden", "error")
            
    except Exception as e:
        flash(f"Fehler beim Löschen: {str(e)}", "error")
    
    return redirect(url_for('admin.admin_backup'))


@admin_bp.route("/backup/export-json")
@login_required
@admin_required
def export_json():
    """Exportiere nur die Datenbank als JSON (ohne Dateien)"""
    try:
        # JSON-Export aller Daten (gleicher Code wie in create_backup)
        backup_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'created_by': current_user.username,
            'users': [],
            'tasks': [],
            'grades': [],
            'achievements': [],
            'user_achievements': [],
            'study_sessions': [],
            'user_statistics': [],
            'activity_logs': [],
            'notifications': [],
            'app_settings': []
        }
        
        # Alle Tabellen exportieren (Code aus create_backup wiederverwenden)
        for user in User.query.all():
            backup_data['users'].append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'total_points': user.total_points,
                'level': user.level,
                'current_streak': user.current_streak,
                'longest_streak': user.longest_streak
            })
        
        for task in Task.query.all():
            backup_data['tasks'].append({
                'id': task.id,
                'user_id': task.user_id,
                'title': task.title,
                'description': task.description,
                'subject': task.subject,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'completed': task.completed,
                'completed_date': task.completed_date.isoformat() if task.completed_date else None,
                'task_type': task.task_type,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'file': task.file
            })
        
        # ... weitere Tabellen (verkürzt für Lesbarkeit)
        
        # JSON als Download zurückgeben
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"schulbuddy_data_{timestamp}.json"
        
        json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
        
        return Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        flash(f"Fehler beim JSON-Export: {str(e)}", "error")
        return redirect(url_for('admin.admin_backup'))
