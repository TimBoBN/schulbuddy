from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, StudySession, Task
from datetime import datetime, timedelta
from config import Config

timer_bp = Blueprint('timer', __name__)

@timer_bp.route('/timer')
@login_required
def timer_page():
    """Hauptseite für den Lern-Timer"""
    # Aktuelle laufende Session finden
    active_session = StudySession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).first()
    
    # Letzte Sessions für Statistik
    recent_sessions = StudySession.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(StudySession.end_time.desc()).limit(10).all()
    
    # Heutige Sessions
    today = datetime.now().date()
    today_sessions = StudySession.query.filter(
        StudySession.user_id == current_user.id,
        StudySession.completed == True,
        StudySession.start_time >= today,
        StudySession.start_time < today + timedelta(days=1)
    ).all()
    
    # Statistiken berechnen
    today_total_minutes = sum(s.actual_duration_seconds for s in today_sessions) // 60 if today_sessions else 0
    today_sessions_count = len(today_sessions)
    
    # Verfügbare Aufgaben für Timer
    available_tasks = Task.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).order_by(Task.due_date.asc()).limit(20).all()
    
    return render_template('timer.html',
                         active_session=active_session,
                         recent_sessions=recent_sessions,
                         today_sessions=today_sessions,
                         today_total_minutes=today_total_minutes,
                         today_sessions_count=today_sessions_count,
                         available_tasks=available_tasks,
                         subjects=Config.SUBJECTS)

@timer_bp.route('/timer/start', methods=['POST'])
@login_required
def start_timer():
    """Timer starten"""
    try:
        data = request.get_json()
        
        # Prüfen ob bereits eine Session läuft
        active_session = StudySession.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).first()
        
        if active_session:
            return jsonify({
                'success': False,
                'message': 'Es läuft bereits eine Session!'
            }), 400
        
        # Neue Session erstellen
        session = StudySession(
            user_id=current_user.id,
            subject=data.get('subject'),
            task_id=data.get('task_id'),
            duration_minutes=data.get('duration_minutes', 25),
            session_type=data.get('session_type', 'study'),
            notes=data.get('notes')
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'message': 'Timer gestartet!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler beim Starten: {str(e)}'
        }), 500

@timer_bp.route('/timer/stop', methods=['POST'])
@login_required
def stop_timer():
    """Timer stoppen"""
    try:
        # Aktive Session finden
        active_session = StudySession.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).first()
        
        if not active_session:
            return jsonify({
                'success': False,
                'message': 'Keine aktive Session gefunden!'
            }), 400
        
        # Session beenden
        active_session.end_session()
        db.session.commit()
        
        # Streak aktualisieren
        current_user.update_streak()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': active_session.to_dict(),
            'points_earned': active_session._calculate_points(),
            'message': f'Session beendet! +{active_session._calculate_points()} Punkte'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler beim Stoppen: {str(e)}'
        }), 500

@timer_bp.route('/timer/pause', methods=['POST'])
@login_required
def pause_timer():
    """Timer pausieren (für Pausen)"""
    try:
        # Aktive Session finden
        active_session = StudySession.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).first()
        
        if not active_session:
            return jsonify({
                'success': False,
                'message': 'Keine aktive Session gefunden!'
            }), 400
        
        # Session pausieren (temporär beenden)
        if not active_session.end_time:
            active_session.end_time = datetime.utcnow()
            duration = active_session.end_time - active_session.start_time
            active_session.actual_duration_seconds = int(duration.total_seconds())
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': active_session.to_dict(),
            'message': 'Timer pausiert'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Fehler beim Pausieren: {str(e)}'
        }), 500

@timer_bp.route('/timer/status')
@login_required
def timer_status():
    """Aktueller Timer-Status für AJAX Updates"""
    active_session = StudySession.query.filter_by(
        user_id=current_user.id,
        completed=False
    ).first()
    
    if active_session:
        # Berechne aktuelle Laufzeit
        current_time = datetime.utcnow()
        elapsed = current_time - active_session.start_time
        elapsed_seconds = int(elapsed.total_seconds())
        
        return jsonify({
            'active': True,
            'session': active_session.to_dict(),
            'elapsed_seconds': elapsed_seconds,
            'elapsed_display': f"{elapsed_seconds // 60}:{elapsed_seconds % 60:02d}"
        })
    else:
        return jsonify({'active': False})

@timer_bp.route('/timer/history')
@login_required
def timer_history():
    """Timer-Verlauf anzeigen"""
    page = request.args.get('page', 1, type=int)
    sessions = StudySession.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(StudySession.end_time.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('timer_history.html', sessions=sessions)

@timer_bp.route('/timer/quick-start/<session_type>')
@login_required
def quick_start_timer(session_type):
    """Schnellstart für verschiedene Timer-Typen"""
    try:
        # Prüfen ob bereits eine Session läuft
        active_session = StudySession.query.filter_by(
            user_id=current_user.id,
            completed=False
        ).first()
        
        if active_session:
            flash('Es läuft bereits eine Timer-Session!', 'warning')
            return redirect(url_for('timer.timer_page'))
        
        # Standard-Dauern für verschiedene Typen
        durations = {
            'pomodoro': 25,
            'short-break': 5,
            'long-break': 15,
            'study': 45,
            'quick': 15
        }
        
        duration = durations.get(session_type, 25)
        
        # Session erstellen
        session = StudySession(
            user_id=current_user.id,
            duration_minutes=duration,
            session_type=session_type
        )
        
        db.session.add(session)
        db.session.commit()
        
        flash(f'{session_type.title()}-Timer gestartet! ({duration} Min)', 'success')
        return redirect(url_for('timer.timer_page'))
        
    except Exception as e:
        flash(f'Fehler beim Starten: {str(e)}', 'error')
        return redirect(url_for('timer.timer_page'))


def auto_cleanup_old_sessions():
    """Automatische Bereinigung alter Timer-Sessions (älter als 14 Tage)"""
    from datetime import datetime, timedelta
    from models import db, StudySession, UserStatistic
    
    try:
        cutoff_date = datetime.now() - timedelta(days=14)
        
        # Alle Sessions älter als 14 Tage finden
        old_sessions = StudySession.query.filter(
            StudySession.start_time < cutoff_date,
            StudySession.completed == True
        ).all()
        
        # Statistiken für diese Sessions in UserStatistic sichern
        sessions_by_date = {}
        for session in old_sessions:
            session_date = session.start_time.date()
            if session_date not in sessions_by_date:
                sessions_by_date[session_date] = []
            sessions_by_date[session_date].append(session)
        
        # Für jeden Tag die Statistiken aktualisieren
        for date, sessions in sessions_by_date.items():
            for session in sessions:
                # UserStatistic für diesen Tag erstellen/aktualisieren
                UserStatistic.create_or_update_daily_stat(session.user_id, date)
        
        # Alte Sessions löschen
        deleted_count = len(old_sessions)
        for session in old_sessions:
            db.session.delete(session)
        
        db.session.commit()
        
        print(f"Timer-Sessions bereinigt: {deleted_count} Sessions gelöscht (älter als 14 Tage)")
        return deleted_count
        
    except Exception as e:
        print(f"Fehler bei Timer-Sessions Bereinigung: {e}")
        db.session.rollback()
        return 0
