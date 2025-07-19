"""
Authentication routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pyotp
import qrcode
import io
import base64

from models import User, db, AppSettings

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login-Seite"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Benutzer mit case-insensitive Suche finden
        user = User.find_by_username(username)
        
        if user and check_password_hash(user.password_hash, password):
            if user.two_factor_enabled:
                # 2FA erforderlich
                session['pending_user_id'] = user.id
                session['pending_username'] = user.username
                return redirect(url_for('auth.verify_2fa'))
            else:
                # Direkt einloggen
                login_user(user)
                session['last_activity'] = datetime.now().isoformat()
                
                # Redirect zu ursprünglicher Seite oder Dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash("Ungültige Anmeldedaten", "error")
    
    # Prüfe ob Registrierung aktiviert ist für Template
    registration_enabled = AppSettings.get_setting('enable_registration', 'False') == 'True'
    return render_template("login.html", registration_enabled=registration_enabled)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Registrierung (falls aktiviert)"""
    # Prüfe ob Registrierung aktiviert ist
    registration_enabled = AppSettings.get_setting('enable_registration', 'False') == 'True'
    if not registration_enabled:
        flash("Registrierung ist derzeit deaktiviert. Bitte wenden Sie sich an den Administrator.", "error")
        return redirect(url_for('auth.login'))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validierung
        if password != confirm_password:
            flash("Passwörter stimmen nicht überein", "error")
            return render_template("register.html")
        
        # Prüfen ob Benutzer bereits existiert (case-insensitive)
        if User.find_by_username(username):
            flash("Benutzername bereits vergeben", "error")
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash("E-Mail bereits registriert", "error")
            return render_template("register.html")
        
        # Benutzer erstellen (Username normalisiert speichern)
        normalized_username = username.strip()  # Leerzeichen entfernen, aber Groß-/Kleinschreibung beibehalten
        user = User(
            username=normalized_username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash("Registrierung erfolgreich! Du kannst dich jetzt anmelden.", "success")
        return redirect(url_for('auth.login'))
    
    return render_template("register.html")

@auth_bp.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    """2FA-Verifizierung"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == "POST":
        token = request.form.get("token")
        user_id = session.get('pending_user_id')
        
        user = User.query.get(user_id)
        if user and user.verify_2fa_token(token):
            # Erfolgreich verifiziert
            login_user(user)
            session['last_activity'] = datetime.now().isoformat()
            session.pop('pending_user_id', None)
            session.pop('pending_username', None)
            
            flash("Erfolgreich angemeldet!", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Ungültiger 2FA-Code", "error")
    
    return render_template("verify_2fa.html", username=session.get('pending_username'))

@auth_bp.route("/setup_2fa", methods=["GET", "POST"])
@login_required
def setup_2fa():
    """2FA einrichten"""
    if request.method == "POST":
        token = request.form.get("token")
        
        if current_user.verify_2fa_token(token):
            current_user.two_factor_enabled = True
            db.session.commit()
            flash("2FA erfolgreich aktiviert!", "success")
            return redirect(url_for('auth.profile'))
        else:
            flash("Ungültiger 2FA-Code", "error")
    
    # QR-Code generieren
    if not current_user.two_factor_secret:
        current_user.generate_2fa_secret()
        db.session.commit()
    
    # QR-Code erstellen
    qr_uri = pyotp.totp.TOTP(current_user.two_factor_secret).provisioning_uri(
        name=current_user.username,
        issuer_name="SchulBuddy"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    qr_code_data = base64.b64encode(img_io.getvalue()).decode()
    
    return render_template("setup_2fa.html", 
                         qr_code=qr_code_data,
                         secret=current_user.two_factor_secret)

@auth_bp.route("/disable_2fa", methods=["POST"])
@login_required
def disable_2fa():
    """2FA deaktivieren"""
    password = request.form.get("password")
    
    if check_password_hash(current_user.password_hash, password):
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        db.session.commit()
        flash("2FA erfolgreich deaktiviert!", "success")
    else:
        flash("Ungültiges Passwort", "error")
    
    return redirect(url_for('auth.profile'))

@auth_bp.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Passwort ändern"""
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        
        # Validierung
        if not check_password_hash(current_user.password_hash, current_password):
            flash("Aktuelles Passwort ist falsch", "error")
            return render_template("change_password.html")
        
        if new_password != confirm_password:
            flash("Neue Passwörter stimmen nicht überein", "error")
            return render_template("change_password.html")
        
        # Passwort ändern
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash("Passwort erfolgreich geändert!", "success")
        return redirect(url_for('auth.profile'))
    
    return render_template("change_password.html")

@auth_bp.route("/profile")
@login_required
def profile():
    """Benutzerprofil"""
    return render_template("profile.html", user=current_user)

@auth_bp.route("/logout")
@login_required
def logout():
    """Logout"""
    logout_user()
    session.clear()
    flash("Erfolgreich abgemeldet", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route("/extend_session", methods=["POST"])
@login_required
def extend_session():
    """Session verlängern"""
    session['last_activity'] = datetime.now().isoformat()
    return jsonify({'success': True, 'message': 'Session verlängert'})
