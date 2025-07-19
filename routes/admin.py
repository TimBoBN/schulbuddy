"""
Admin routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from functools import wraps

from models import User, Task, Grade, AppSettings, db

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
        if User.query.filter_by(username=username).first():
            flash("Benutzername bereits vergeben", "error")
            return render_template("admin_create_user.html")
        
        if User.query.filter_by(email=email).first():
            flash("E-Mail bereits registriert", "error")
            return render_template("admin_create_user.html")
        
        # Benutzer erstellen
        user = User(
            username=username,
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
                'enable_notifications': request.form.get('enable_notifications') == 'on'
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
        'enable_notifications': AppSettings.get_setting('enable_notifications', 'True') == 'True'
    }
    
    return render_template("admin_settings.html", settings=settings)
