"""
Main routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from collections import defaultdict
import os

from models import Task, Grade, AppSettings, db
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
@login_required
def index():
    """Hauptseite - Dashboard"""
    try:
        # Nur die 5 nächsten Aufgaben anzeigen (sortiert nach Fälligkeit und Priorität)
        today = date.today()
        
        # Alle offenen Aufgaben
        open_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()
        
        # Sortiere nach Priorität und Fälligkeit
        def sort_by_priority_date(task):
            # Da priority noch nicht in der DB existiert, verwende task_type als Priorität
            priority_order = {'exam': 4, 'test': 3, 'project': 2, 'homework': 1, 'other': 0}
            priority_score = priority_order.get(task.task_type, 0)
            
            # Überfällige Aufgaben haben höchste Priorität
            if task.due_date and task.due_date < today:
                priority_score += 10
            # Heute fällige Aufgaben haben hohe Priorität
            elif task.due_date and task.due_date == today:
                priority_score += 5
            
            due_date = task.due_date or date(2099, 12, 31)
            return (-priority_score, due_date)
        
        open_tasks.sort(key=sort_by_priority_date)
        tasks = open_tasks[:5]  # Nur die 5 wichtigsten
        
        # Nur die 5 letzten Noten anzeigen
        grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp.desc()).limit(5).all()
        
        # Anzahl erledigter Aufgaben für Archiv-Button
        completed_tasks_count = Task.query.filter_by(user_id=current_user.id, completed=True).count()
        
        # Kommende Deadlines (nächste 7 Tage)
        upcoming_deadline = today + timedelta(days=7)
        upcoming_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.due_date.between(today, upcoming_deadline)
        ).order_by(Task.due_date.asc()).all()
        
        # Überfällige Aufgaben
        overdue_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.due_date < today
        ).order_by(Task.due_date.desc()).all()
        
        # Fach-Zusammenfassung
        subject_summary = defaultdict(lambda: {'tasks': 0, 'completed': 0, 'avg_grade': 0})
        
        # Aufgaben nach Fach
        all_tasks = Task.query.filter_by(user_id=current_user.id).all()
        for task in all_tasks:
            subject_summary[task.subject]['tasks'] += 1
            if task.completed:
                subject_summary[task.subject]['completed'] += 1
        
        # Noten nach Fach
        all_grades = Grade.query.filter_by(user_id=current_user.id).all()
        grades_by_subject = defaultdict(list)
        for grade in all_grades:
            grades_by_subject[grade.subject].append(grade.grade)
        
        for subject, grade_list in grades_by_subject.items():
            if grade_list:
                subject_summary[subject]['avg_grade'] = round(sum(grade_list) / len(grade_list), 2)
                # Template erwartet 'average' statt 'avg_grade'
                subject_summary[subject]['average'] = subject_summary[subject]['avg_grade']
        
        # Berechne Gesamtdurchschnitt
        if all_grades:
            overall_average = sum(g.grade for g in all_grades) / len(all_grades)
            overall_average = round(overall_average, 2)
        else:
            overall_average = 0
        
        # Zeugnis-Durchschnitt (nur Zeugnisnoten)
        certificate_grades = [g for g in all_grades if g.grade_type == 'certificate']
        if certificate_grades:
            certificate_average = sum(g.grade for g in certificate_grades) / len(certificate_grades)
            certificate_average = round(certificate_average, 2)
        else:
            certificate_average = 0
        
        # Session-Timeout-Warnung
        logout_warning = session.pop('logout_warning', None)
        
        return render_template("index.html",
                             aufgaben=tasks,
                             tasks=tasks,
                             grades=grades,
                             noten=grades,
                             completed_tasks_count=completed_tasks_count,
                             upcoming_tasks=upcoming_tasks,
                             overdue_tasks=overdue_tasks,
                             subject_summary=dict(subject_summary),
                             subjects=Config.SUBJECTS,
                             logout_warning=logout_warning,
                             user=current_user,
                             open_tasks_count=len(open_tasks),  # Alle offenen Aufgaben
                             priority_tasks_count=len(tasks),  # Top 5 Aufgaben
                             overall_average=overall_average,
                             certificate_average=certificate_average,
                             total_average=certificate_average,  # Template erwartet total_average für Gesamtdurchschnitt
                             durchschnitt=dict(subject_summary),
                             today=today)
    except Exception as e:
        print(f"Error in index route: {e}")
        flash("Fehler beim Laden der Daten", "error")
        return render_template("index.html", 
                             tasks=[], 
                             grades=[], 
                             aufgaben=[],
                             noten=[],
                             completed_tasks_count=0,
                             upcoming_tasks=[],
                             overdue_tasks=[],
                             subject_summary={},
                             subjects=Config.SUBJECTS,
                             user=current_user,
                             open_tasks_count=0,
                             priority_tasks_count=0,
                             overall_average=0,
                             certificate_average=0,
                             total_average=0,
                             durchschnitt={},
                             today=today)

@main_bp.route("/repair")
@login_required
def repair():
    """Reparatur-Seite für Datenbankprobleme"""
    return render_template("repair.html")

@main_bp.route("/test")
@login_required
def test():
    """Test-Seite für Entwicklung"""
    # Teste verschiedene Funktionen
    test_results = {
        'database_connection': True,
        'user_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'task_count': Task.query.filter_by(user_id=current_user.id).count(),
        'grade_count': Grade.query.filter_by(user_id=current_user.id).count(),
        'upload_folder_exists': os.path.exists(Config.UPLOAD_FOLDER),
        'upload_folder_writable': os.access(Config.UPLOAD_FOLDER, os.W_OK),
        'session_data': dict(session),
        'user_data': {
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin,
            'total_points': current_user.total_points,
            'level': current_user.level,
            'current_streak': current_user.current_streak,
            'two_factor_enabled': current_user.two_factor_enabled
        } if current_user.is_authenticated else None
    }
    
    return render_template("test.html", test_results=test_results)

@main_bp.route("/debug")
@login_required
def debug():
    """Debug-Informationen"""
    debug_info = {
        'app_config': {
            'SECRET_KEY': '***' if Config.SECRET_KEY else 'Not set',
            'SQLALCHEMY_DATABASE_URI': Config.SQLALCHEMY_DATABASE_URI,
            'UPLOAD_FOLDER': Config.UPLOAD_FOLDER,
            'MAX_CONTENT_LENGTH': Config.MAX_CONTENT_LENGTH,
            'ALLOWED_EXTENSIONS': Config.ALLOWED_EXTENSIONS
        },
        'database_stats': {
            'users': db.session.execute(db.text("SELECT COUNT(*) FROM users")).scalar(),
            'tasks': db.session.execute(db.text("SELECT COUNT(*) FROM tasks")).scalar(),
            'grades': db.session.execute(db.text("SELECT COUNT(*) FROM grades")).scalar(),
            'activity_logs': db.session.execute(db.text("SELECT COUNT(*) FROM activity_logs")).scalar()
        },
        'app_settings': {
            'app_name': AppSettings.get_setting('app_name', 'SchulBuddy'),
            'session_timeout': AppSettings.get_setting('session_timeout_minutes', '120'),
            'max_file_size': AppSettings.get_setting('max_file_size', '16'),
            'enable_gamification': AppSettings.get_setting('enable_gamification', 'True'),
            'enable_notifications': AppSettings.get_setting('enable_notifications', 'True')
        },
        'user_info': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin,
            'created_at': current_user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'total_points': current_user.total_points,
            'level': current_user.level,
            'current_streak': current_user.current_streak,
            'longest_streak': current_user.longest_streak,
            'two_factor_enabled': current_user.two_factor_enabled
        } if current_user.is_authenticated else None
    }
    
    return render_template("debug.html", debug_info=debug_info)

@main_bp.before_request
def check_session_timeout():
    """Prüft Session-Timeout und warnt vor Ablauf"""
    if current_user.is_authenticated:
        # Hole Timeout-Einstellungen
        session_timeout = int(AppSettings.get_setting('session_timeout_minutes', '120'))
        warning_minutes = int(AppSettings.get_setting('auto_logout_warning_minutes', '5'))
        
        # Setze Timeout in Session für JavaScript
        session['session_timeout_minutes'] = session_timeout
        
        # Prüfe letzte Aktivität
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity = datetime.fromisoformat(last_activity)
            now = datetime.now()
            time_since_activity = (now - last_activity).total_seconds() / 60
            
            # Session abgelaufen
            if time_since_activity > session_timeout:
                from flask_login import logout_user
                logout_user()
                session.clear()
                flash('Sitzung abgelaufen. Bitte melde dich erneut an.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Warnung vor Ablauf
            elif time_since_activity > (session_timeout - warning_minutes):
                remaining_minutes = session_timeout - time_since_activity
                session['logout_warning'] = f"Automatischer Logout in {remaining_minutes:.0f} Minuten"
        
        # Aktualisiere letzte Aktivität
        session['last_activity'] = datetime.now().isoformat()
