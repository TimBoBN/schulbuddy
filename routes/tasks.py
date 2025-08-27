"""
Task-related routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

from models import Task, Grade, db, ActivityLog, UserStatistic
from config import Config
from config import Config
from api_security import api_key_or_login_required

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route("/tasks")
@login_required
def tasks_overview():
    """Reine Todo-Listen Übersicht"""
    from config import Config
    
    today = datetime.now().date()
    
    # Alle offenen Aufgaben des Benutzers
    all_tasks = Task.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).all()
    
    # Erledigte Aufgaben der letzten 7 Tage
    week_ago = datetime.now() - timedelta(days=7)
    completed_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        Task.completed_date >= week_ago
    ).order_by(Task.completed_date.desc()).limit(20).all()
    
    # Kategorisiere Aufgaben
    overdue_tasks = []
    today_tasks = []
    upcoming_tasks = []
    
    for task in all_tasks:
        if task.due_date:
            # WICHTIG: task.due_date ist bereits ein date-Objekt, nicht datetime
            if task.due_date < today:
                overdue_tasks.append(task)
            elif task.due_date == today:
                today_tasks.append(task)
            else:
                upcoming_tasks.append(task)
        else:
            upcoming_tasks.append(task)
    
    # Sortiere nach Priorität und Datum
    def sort_by_priority_date(task):
        # Da priority noch nicht in der DB existiert, verwende task_type als Priorität
        priority_order = {'exam': 4, 'test': 3, 'project': 2, 'homework': 1, 'other': 0}
        priority_score = priority_order.get(task.task_type, 0)
        due_date = task.due_date or datetime(2099, 12, 31)
        return (-priority_score, due_date)
    
    overdue_tasks.sort(key=sort_by_priority_date)
    today_tasks.sort(key=sort_by_priority_date)
    upcoming_tasks.sort(key=sort_by_priority_date)
    
    # Zähler
    overdue_count = len(overdue_tasks)
    today_count = len(today_tasks)
    total_count = len(all_tasks)
    
    return render_template('tasks.html',
                         overdue_tasks=overdue_tasks,
                         today_tasks=today_tasks,
                         upcoming_tasks=upcoming_tasks,
                         completed_tasks=completed_tasks,
                         overdue_count=overdue_count,
                         today_count=today_count,
                         total_count=total_count,
                         current_date=today,
                         subjects=Config.SUBJECTS)

@tasks_bp.route("/calendar")
@login_required
def calendar():
    """Kalender-Ansicht"""
    # Alle Fächer des aktuellen Benutzers sammeln
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    subjects = {}
    for task in tasks:
        if task.subject and task.subject not in subjects:
            subjects[task.subject] = task.subject
    
    return render_template("calendar_simple.html", subjects=subjects)

@tasks_bp.route("/api-key")
@login_required
def api_key_management():
    """API-Key Verwaltungsseite"""
    return render_template("api_key.html")

@tasks_bp.route("/api/events")
@api_key_or_login_required
def api_events():
    """API-Endpoint für Kalender-Events (API-Key oder Login erforderlich)"""
    # Hole User aus Request (gesetzt durch Decorator)
    user = getattr(request, 'api_user', current_user)
    
    # Lade Fach-Farben aus Config
    from config import Config
    
    # Hole Aufgaben und Noten
    tasks = Task.query.filter_by(user_id=user.id, completed=False).all()
    grades = Grade.query.filter_by(user_id=user.id).all()
    
    events = []
    
    # Füge Aufgaben hinzu
    for task in tasks:
        # Bestimme Event-Typ basierend auf task_type
        event_type = 'homework'  # Default
        if hasattr(task, 'task_type'):
            if task.task_type == 'exam':
                event_type = 'exam'
            elif task.task_type == 'project':
                event_type = 'project'
            elif task.task_type == 'test':
                event_type = 'exam'  # Tests als Klassenarbeiten behandeln
        
        # Hole Fachfarbe
        subject_color = Config.SUBJECTS.get(task.subject, '#6c757d')
        
        events.append({
            'id': f'task_{task.id}',
            'title': task.title,
            'start': task.due_date.isoformat() if task.due_date else None,
            'subject': task.subject,
            'type': event_type,
            'color': subject_color,
            'backgroundColor': subject_color,
            'borderColor': subject_color,
            'description': task.description or '',
            'extendedProps': {
                'subject': task.subject,
                'description': task.description,
                'file': task.file,
                'task_id': task.id
            }
        })
    
    # Füge Noten hinzu (falls sie ein Datum haben)
    for grade in grades:
        if grade.date:
            subject_color = Config.SUBJECTS.get(grade.subject, '#6c757d')
            
            events.append({
                'id': f'grade_{grade.id}',
                'title': f'{grade.subject}: {grade.grade}',
                'start': grade.date.isoformat(),
                'subject': grade.subject,
                'type': 'grade',
                'color': subject_color,
                'backgroundColor': subject_color,
                'borderColor': subject_color,
                'description': grade.description or f'Note: {grade.grade}',
                'extendedProps': {
                    'subject': grade.subject,
                    'grade': grade.grade,
                    'description': grade.description,
                    'grade_id': grade.id
                }
            })
    
    return jsonify(events)

@tasks_bp.route("/api/key")
@login_required
def get_api_key():
    """Hole oder erstelle API-Key für aktuellen User"""
    api_key = current_user.get_or_create_api_key()
    return jsonify({
        'api_key': api_key,
        'created_at': current_user.api_key_created_at.isoformat() if current_user.api_key_created_at else None,
        'usage': {
            'header': f'Authorization: Bearer {api_key}',
            'query': f'?api_key={api_key}',
            'json': f'{{"api_key": "{api_key}"}}',
            'form': f'api_key={api_key}'
        },
        'example_request': f'/api/events?api_key={api_key}'
    })

@tasks_bp.route("/api/key/regenerate", methods=["POST"])
@login_required
def regenerate_api_key():
    """Generiere neuen API-Key"""
    new_api_key = current_user.generate_api_key()
    db.session.commit()
    
    flash("Neuer API-Key wurde generiert!", "success")
    return jsonify({
        'api_key': new_api_key,
        'created_at': current_user.api_key_created_at.isoformat(),
        'message': 'API-Key erfolgreich regeneriert'
    })

@tasks_bp.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    """Neue Aufgabe hinzufügen"""
    from config import Config
    
    if request.method == "GET":
        # Formular anzeigen
        return render_template('add_task.html', subjects=Config.SUBJECTS)
    
    # POST-Request verarbeiten
    title = request.form.get("title")
    description = request.form.get("description")
    subject = request.form.get("subject")
    due_date_str = request.form.get("due_date")
    task_type = request.form.get("task_type", "homework")
    
    # Datum verarbeiten
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Ungültiges Datum", "error")
            return render_template('add_task.html', subjects=Config.SUBJECTS)
    
    # Datei-Upload
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            if filename:
                file_path = os.path.join('uploads', filename)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    
    # Aufgabe erstellen
    task = Task(
        title=title,
        description=description,
        subject=subject,
        due_date=due_date,
        task_type=task_type,
        file=file_path,
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    flash("Aufgabe erfolgreich hinzugefügt!", "success")
    return redirect(url_for('main.index'))

@tasks_bp.route("/toggle_task/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    """Aufgabe als erledigt/offen markieren"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Aufgabe nicht gefunden'})
    
    # Status umschalten
    task.completed = not task.completed
    
    if task.completed:
        # Completed-Date setzen
        task.completed_date = datetime.utcnow()
        
        # Punkte hinzufügen
        points = 10
        if task.task_type == 'exam':
            points = 25
        elif task.task_type == 'test':
            points = 18
        elif task.task_type == 'project':
            points = 20
        
        current_user.add_points(points, 'task_completed', {
            'task_id': task.id,
            'task_title': task.title,
            'task_type': task.task_type
        })
        
        # Streak aktualisieren
        current_user.update_streak()
        
        flash(f"Aufgabe erledigt! +{points} Punkte", "success")
    else:
        # Wenn Aufgabe wieder geöffnet wird, completed_date löschen
        task.completed_date = None
    
    db.session.commit()
    return jsonify({'success': True, 'completed': task.completed})

@tasks_bp.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    """Aufgabe löschen"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Aufgabe nicht gefunden'})
    
    # Datei löschen falls vorhanden
    if task.file:
        try:
            file_full_path = os.path.join(Config.UPLOAD_FOLDER, os.path.basename(task.file))
            if os.path.exists(file_full_path):
                os.remove(file_full_path)
        except Exception as e:
            print(f"Fehler beim Löschen der Datei: {e}")
    
    db.session.delete(task)
    db.session.commit()
    
    flash("Aufgabe erfolgreich gelöscht!", "success")
    return jsonify({'success': True})

@tasks_bp.route("/task_detail/<int:task_id>")
@login_required
def task_detail(task_id):
    """Aufgaben-Details"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Aufgabe nicht gefunden", "error")
        return redirect(url_for('main.index'))
    
    return render_template("task_detail.html", task=task)

@tasks_bp.route("/complete_task/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    """Aufgabe als erledigt markieren"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Aufgabe nicht gefunden", "error")
        return redirect(url_for('main.index'))
    
    task.completed = True
    task.completed_date = datetime.utcnow()
    
    # Punkte hinzufügen
    points = 10
    if task.task_type == 'exam':
        points = 25
    elif task.task_type == 'test':
        points = 18
    elif task.task_type == 'project':
        points = 20
    
    current_user.add_points(points, 'task_completed', {
        'task_id': task.id,
        'task_title': task.title,
        'task_type': task.task_type
    })
    
    db.session.commit()
    flash(f"Aufgabe erledigt! +{points} Punkte", "success")
    return redirect(url_for('main.index'))

@tasks_bp.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    """Aufgabe bearbeiten"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Aufgabe nicht gefunden", "error")
        return redirect(url_for('main.index'))
    
    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.subject = request.form.get("subject")
        task.task_type = request.form.get("task_type")
        
        # Datum aktualisieren
        due_date_str = request.form.get("due_date")
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Ungültiges Datum", "error")
                return render_template("edit_task.html", task=task, subjects=Config.SUBJECTS)
        
        # Neue Datei hochladen
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                if filename:
                    # Alte Datei löschen
                    if task.file:
                        try:
                            old_file_path = os.path.join(Config.UPLOAD_FOLDER, os.path.basename(task.file))
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                        except Exception as e:
                            print(f"Fehler beim Löschen der alten Datei: {e}")
                    
                    # Neue Datei speichern
                    file_path = os.path.join('uploads', filename)
                    file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                    task.file = file_path
        
        db.session.commit()
        flash("Aufgabe erfolgreich bearbeitet!", "success")
        return redirect(url_for('main.index'))
    
    return render_template("edit_task.html", task=task, subjects=Config.SUBJECTS)

@tasks_bp.route("/archive")
@login_required
def archive():
    """Archiv mit erledigten Aufgaben"""
    # Automatische Bereinigung alter Aufgaben (beim Laden der Seite)
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=14)
        
        # Finde alle erledigten Aufgaben älter als 14 Tage
        old_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == True,
            Task.completed_date < cutoff_date
        ).all()
        
        if old_tasks:
            deleted_count = 0
            deleted_files = []
            
            # Sammle Statistiken BEFORE Löschung für alle betroffenen Tage
            affected_dates = set()
            for task in old_tasks:
                if task.completed_date:
                    affected_dates.add(task.completed_date.date())
                if task.created_at:
                    affected_dates.add(task.created_at.date())
            
            # Aktualisiere Statistiken für alle betroffenen Tage
            for date_obj in affected_dates:
                UserStatistic.update_daily_stats(current_user.id, date_obj)
            
            for task in old_tasks:
                # Datei löschen, falls vorhanden
                if task.file:
                    try:
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], task.file)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_files.append(task.file)
                    except:
                        pass  # Ignoriere Datei-Fehler
                
                db.session.delete(task)
                deleted_count += 1
            
            # Aktivitätslog für automatische Löschung
            if deleted_count > 0:
                log_entry = ActivityLog(
                    user_id=current_user.id,
                    activity_type="auto_cleanup",
                    activity_data=f"Automatische Bereinigung: {deleted_count} Aufgaben gelöscht, {len(deleted_files)} Dateien entfernt"
                )
                db.session.add(log_entry)
                db.session.commit()
                flash(f"Automatische Bereinigung: {deleted_count} alte Aufgaben wurden gelöscht (Speicher gespart).", "success")
    except Exception as e:
        db.session.rollback()
        # Stille Fehlerbehandlung - keine Fehlermeldung für Benutzer
        pass
    
    # Alle erledigten Aufgaben des Benutzers
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(Task.completed_date.desc()).all()
    
    # Gruppiere nach Monat
    from collections import defaultdict
    tasks_by_month = defaultdict(list)
    
    for task in completed_tasks:
        if task.completed_date:
            month_key = task.completed_date.strftime('%Y-%m')
            month_name = task.completed_date.strftime('%B %Y')
            tasks_by_month[month_key].append({
                'task': task,
                'month_name': month_name,
                'month_display': month_name
            })
    
    # Sortiere Monate (neueste zuerst)
    sorted_months = sorted(tasks_by_month.keys(), reverse=True)
    
    return render_template('archive.html', 
                         tasks_by_month=tasks_by_month,
                         sorted_months=sorted_months,
                         archived_tasks=completed_tasks,
                         total_completed=len(completed_tasks))


@tasks_bp.route("/delete_archived_task/<int:task_id>", methods=['POST'])
@login_required
def delete_archived_task(task_id):
    """Lösche eine archivierte Aufgabe permanent"""
    task = Task.query.get_or_404(task_id)
    
    # Sicherheitscheck: Nur eigene und erledigte Aufgaben löschen
    if task.user_id != current_user.id:
        flash("Du kannst nur deine eigenen Aufgaben löschen.", "error")
        return redirect(url_for('tasks.archive'))
    
    if not task.completed:
        flash("Nur erledigte Aufgaben können aus dem Archiv gelöscht werden.", "error")
        return redirect(url_for('tasks.archive'))
    
    try:
        # WICHTIG: Statistiken aktualisieren BEVOR die Aufgabe gelöscht wird
        affected_dates = set()
        if task.completed_date:
            affected_dates.add(task.completed_date.date())
        if task.created_at:
            affected_dates.add(task.created_at.date())
        
        for date_obj in affected_dates:
            UserStatistic.update_daily_stats(current_user.id, date_obj)
        
        # Datei löschen, falls vorhanden
        if task.file:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], task.file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Aufgabe aus der Datenbank löschen
        db.session.delete(task)
        db.session.commit()
        
        # Aktivitätslog
        log_entry = ActivityLog(
            user_id=current_user.id,
            activity_type="delete_archived_task",
            activity_data=f"Archivierte Aufgabe '{task.title}' permanent gelöscht | Fach: {task.subject}, Typ: {task.task_type}"
        )
        db.session.add(log_entry)
        db.session.commit()
        
        flash(f"Aufgabe '{task.title}' wurde permanent gelöscht.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Fehler beim Löschen der Aufgabe: {str(e)}", "error")
    
    return redirect(url_for('tasks.archive'))


def auto_cleanup_old_tasks():
    """Automatische Bereinigung alter Aufgaben (für Cron-Job oder regelmäßige Ausführung)"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=14)
        
        # Finde alle erledigten Aufgaben älter als 14 Tage
        old_tasks = Task.query.filter(
            Task.completed == True,
            Task.completed_date < cutoff_date
        ).all()
        
        deleted_count = 0
        deleted_files = []
        
        # Sammle alle betroffenen Benutzer und Daten für Statistik-Update
        users_and_dates = {}
        
        for task in old_tasks:
            user_id = task.user_id
            if user_id not in users_and_dates:
                users_and_dates[user_id] = set()
            
            if task.completed_date:
                users_and_dates[user_id].add(task.completed_date.date())
            if task.created_at:
                users_and_dates[user_id].add(task.created_at.date())
        
        # Aktualisiere Statistiken für alle betroffenen Benutzer und Tage
        for user_id, dates in users_and_dates.items():
            for date_obj in dates:
                UserStatistic.update_daily_stats(user_id, date_obj)
        
        for task in old_tasks:
            # Datei löschen, falls vorhanden
            if task.file:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], task.file)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        deleted_files.append(task.file)
                    except:
                        pass  # Ignoriere Datei-Fehler
            
            # Aktivitätslog für jeden Benutzer
            if task.user_id:
                log_entry = ActivityLog(
                    user_id=task.user_id,
                    activity_type="auto_cleanup_task",
                    activity_data=f"Automatische Löschung: '{task.title}' nach 14 Tagen entfernt | Fach: {task.subject}, Typ: {task.task_type}"
                )
                db.session.add(log_entry)
            
            db.session.delete(task)
            deleted_count += 1
        
        if deleted_count > 0:
            db.session.commit()
            print(f"Auto-Cleanup: {deleted_count} alte Aufgaben gelöscht, {len(deleted_files)} Dateien entfernt")
        
        return deleted_count
        
    except Exception as e:
        db.session.rollback()
        print(f"Fehler bei der automatischen Bereinigung: {str(e)}")
        return 0
