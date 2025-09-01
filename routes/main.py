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
from utils.app_settings import get_current_school_year, get_current_semester, get_school_year_options
from flask import abort
from models import User
from utils.webuntis_simple import fetch_timetable, set_default_credentials
# helper to obtain credentials for current_user
def _get_user_webuntis_creds(user):
    if not user:
        return None
    server = getattr(user, 'webuntis_server', None)
    school = getattr(user, 'webuntis_school', None)
    username = getattr(user, 'webuntis_username', None)
    password = None
    if hasattr(user, 'get_webuntis_password'):
        try:
            password = user.get_webuntis_password()
        except Exception:
            password = None
    # fallback: try direct decrypt of stored field
    if not password:
        enc = getattr(user, 'webuntis_password_enc', None)
        if enc:
            try:
                from utils.crypto import decrypt_text
                password = decrypt_text(enc)
            except Exception:
                password = None
    if server and school and username and password:
        return (server, school, username, password)
    # debug log for missing creds
    try:
        print(f"webuntis creds missing for user {getattr(user,'id',None)} -> server={server!r} school={school!r} username_field={username!r} has_password_enc={bool(getattr(user,'webuntis_password_enc',None))} password_decrypted={bool(password)}")
    except Exception:
        pass
    return None

main_bp = Blueprint('main', __name__)

@main_bp.route("/health")
def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}, 200


@main_bp.route("/")
@login_required
def index():
    """Hauptseite - Dashboard"""
    try:
        # Nur die 5 nächsten Aufgaben anzeigen (sortiert nach Fälligkeit und Priorität)
        today = date.today()
        
        # Database queries with error handling
        try:
            # Alle offenen Aufgaben
            open_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()
            print(f"DEBUG: Found {len(open_tasks)} open tasks")
        except Exception as e:
            print(f"ERROR loading open tasks: {e}")
            open_tasks = []
        
        # Sortiere nach Priorität und Fälligkeit
        def sort_by_priority_date(task):
            try:
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
            except Exception as e:
                print(f"ERROR in sort_by_priority_date for task {getattr(task, 'id', 'unknown')}: {e}")
                return (0, date(2099, 12, 31))
        
        try:
            open_tasks.sort(key=sort_by_priority_date)
            tasks = open_tasks[:5]  # Nur die 5 wichtigsten
            print(f"DEBUG: Sorted to top 5 tasks")
        except Exception as e:
            print(f"ERROR sorting tasks: {e}")
            tasks = open_tasks[:5] if open_tasks else []
        
        # Grades queries with error handling
        try:
            # Nur die 5 letzten Noten anzeigen
            grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp.desc()).limit(5).all()
            print(f"DEBUG: Found {len(grades)} recent grades")
        except Exception as e:
            print(f"ERROR loading grades: {e}")
            grades = []
        
        # Task statistics with error handling
        try:
            # Anzahl erledigter Aufgaben für Archiv-Button
            completed_tasks_count = Task.query.filter_by(user_id=current_user.id, completed=True).count()
            print(f"DEBUG: Found {completed_tasks_count} completed tasks")
        except Exception as e:
            print(f"ERROR loading completed tasks count: {e}")
            completed_tasks_count = 0
        
        try:
            # Kommende Deadlines (nächste 7 Tage)
            upcoming_deadline = today + timedelta(days=7)
            upcoming_tasks = Task.query.filter(
                Task.user_id == current_user.id,
                Task.completed == False,
                Task.due_date.between(today, upcoming_deadline)
            ).order_by(Task.due_date.asc()).all()
            print(f"DEBUG: Found {len(upcoming_tasks)} upcoming tasks")
        except Exception as e:
            print(f"ERROR loading upcoming tasks: {e}")
            upcoming_tasks = []
        
        try:
            # Überfällige Aufgaben
            overdue_tasks = Task.query.filter(
                Task.user_id == current_user.id,
                Task.completed == False,
                Task.due_date < today
            ).order_by(Task.due_date.desc()).all()
            print(f"DEBUG: Found {len(overdue_tasks)} overdue tasks")
        except Exception as e:
            print(f"ERROR loading overdue tasks: {e}")
            overdue_tasks = []
        
        # Subject summary calculation with error handling
        try:
            # Fach-Zusammenfassung
            subject_summary = defaultdict(lambda: {'tasks': 0, 'completed': 0, 'avg_grade': 0})
            
            # Aufgaben nach Fach
            all_tasks = Task.query.filter_by(user_id=current_user.id).all()
            for task in all_tasks:
                if hasattr(task, 'subject') and task.subject:
                    subject_summary[task.subject]['tasks'] += 1
                    if task.completed:
                        subject_summary[task.subject]['completed'] += 1
            
            print(f"DEBUG: Processed {len(all_tasks)} total tasks for subject summary")
        except Exception as e:
            print(f"ERROR building subject summary from tasks: {e}")
            subject_summary = defaultdict(lambda: {'tasks': 0, 'completed': 0, 'avg_grade': 0})
        
        try:
            # Noten nach Fach
            all_grades = Grade.query.filter_by(user_id=current_user.id).all()
            grades_by_subject = defaultdict(list)
            for grade in all_grades:
                if hasattr(grade, 'subject') and grade.subject:
                    grades_by_subject[grade.subject].append(grade.grade)
            
            for subject, grade_list in grades_by_subject.items():
                if grade_list:
                    subject_summary[subject]['avg_grade'] = round(sum(grade_list) / len(grade_list), 2)
                    # Template erwartet 'average' statt 'avg_grade'
                    subject_summary[subject]['average'] = subject_summary[subject]['avg_grade']
            
            print(f"DEBUG: Processed {len(all_grades)} total grades for subject summary")
        except Exception as e:
            print(f"ERROR building subject summary from grades: {e}")
        
        try:
            # Berechne Gesamtdurchschnitt
            if all_grades:
                valid_grades = [g for g in all_grades if hasattr(g, 'grade') and g.grade is not None]
                if valid_grades:
                    overall_average = sum(g.grade for g in valid_grades) / len(valid_grades)
                    overall_average = round(overall_average, 2)
                else:
                    overall_average = 0
            else:
                overall_average = 0
            
            # Zeugnis-Durchschnitt (nur Zeugnisnoten)
            certificate_grades = [g for g in all_grades if hasattr(g, 'grade_type') and g.grade_type == 'certificate' and hasattr(g, 'grade') and g.grade is not None]
            if certificate_grades:
                certificate_average = sum(g.grade for g in certificate_grades) / len(certificate_grades)
                certificate_average = round(certificate_average, 2)
            else:
                certificate_average = 0
        except Exception as e:
            print(f"ERROR calculating averages: {e}")
            overall_average = 0
            certificate_average = 0
        
        # Session-Timeout-Warnung
        try:
            logout_warning = session.pop('logout_warning', None)
        except Exception as e:
            print(f"ERROR getting logout warning: {e}")
            logout_warning = None
        
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
                             today=today,
                             current_school_year=get_current_school_year(),
                             current_semester=get_current_semester(),
                             school_year_options=get_school_year_options())
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in index route: {e}")
        print(f"Full traceback: {error_details}")
        
        # Try to identify specific error areas
        error_context = "unknown"
        try:
            # Test database connection
            Task.query.count()
            error_context = "after_db_test"
        except Exception as db_e:
            print(f"Database error: {db_e}")
            error_context = "database_connection"
        
        try:
            # Test app settings functions
            get_current_school_year()
            get_current_semester() 
            get_school_year_options()
            error_context = "after_settings_test"
        except Exception as settings_e:
            print(f"App settings error: {settings_e}")
            error_context = "app_settings"
        
        flash(f"Fehler beim Laden der Daten (Kontext: {error_context}). Details in den Logs.", "error")
        
        # Safe fallback values
        try:
            today = date.today()
        except:
            today = None
            
        try:
            school_year = get_current_school_year()
            semester = get_current_semester()
            year_options = get_school_year_options()
        except:
            school_year = '2025/26'
            semester = 1
            year_options = ['2025/26']
        
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
                             today=today,
                             current_school_year=school_year,
                             current_semester=semester,
                             school_year_options=year_options)

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

@main_bp.route('/settings/webuntis', methods=['GET', 'POST'])
@login_required
def webuntis_settings():
    """Settings page to store or clear WebUntis credentials for the current user."""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save':
            server = request.form.get('server')
            school = request.form.get('school')
            username = request.form.get('username')
            password = request.form.get('password')
            if not (server and school and username):
                flash('Server, Schule und Benutzername sind erforderlich.', 'error')
            else:
                # store directly to the user model to avoid method lookup issues
                from utils.crypto import encrypt_text
                current_user.webuntis_server = server
                current_user.webuntis_school = school
                current_user.webuntis_username = username
                if password:
                    try:
                        current_user.webuntis_password_enc = encrypt_text(password)
                    except Exception:
                        current_user.webuntis_password_enc = None
                else:
                    # keep existing password if no password provided
                    pass
                db.session.add(current_user)
                db.session.commit()
                flash('WebUntis-Zugangsdaten gespeichert.', 'success')
        elif action == 'clear':
            current_user.webuntis_server = None
            current_user.webuntis_school = None
            current_user.webuntis_username = None
            current_user.webuntis_password_enc = None
            db.session.add(current_user)
            db.session.commit()
            flash('WebUntis-Zugangsdaten entfernt.', 'success')
        return redirect(url_for('main.webuntis_settings'))
    # GET
    return render_template('webuntis_settings.html', user=current_user)

@main_bp.route('/timetable')
@login_required
def timetable_page():
    """Render the timetable HTML page. The JSON endpoint was removed; timetable can use server-side data or fetch from the settings UI if needed."""
    return render_template('timetable.html')

@main_bp.route('/webuntis/timetable')
@login_required
def webuntis_timetable():
    """JSON endpoint for WebUntis timetable. Optional query params: start=YYYY-MM-DD end=YYYY-MM-DD"""
    start = request.args.get('start')
    end = request.args.get('end')
    creds = _get_user_webuntis_creds(current_user)
    if not creds:
        flash('Bitte WebUntis-Zugang in den Einstellungen speichern.', 'warning')
        return jsonify([])
    server, school, username, password = creds
    debug_flag = request.args.get('debug') == '1'
    try:
        # set module defaults for this request
        set_default_credentials(server, school, username, password)
        entries = fetch_timetable(start=start, end=end, debug=debug_flag)
        return jsonify(entries)
    except Exception as e:
        print('webuntis endpoint error:', e)
        flash('Fehler beim Abruf vom WebUntis. Prüfe Logs.', 'error')
        return jsonify([])

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
