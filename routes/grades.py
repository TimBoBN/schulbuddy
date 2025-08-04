"""
Grade-related routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from collections import defaultdict

from models import Grade, Task, db
from config import Config

grades_bp = Blueprint('grades', __name__)

@grades_bp.route("/add_grade", methods=["POST"])
@login_required
def add_grade():
    """Note hinzufügen"""
    subject = request.form.get("subject")
    grade_value = request.form.get("grade")
    grade_type = request.form.get("grade_type", "test")
    description = request.form.get("description", "")
    
    # Liste der erlaubten Notenwerte (1.0, 1.5, 2.0, usw.)
    valid_grades = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
    
    try:
        grade_value = float(grade_value)
        # Prüfe ob Wert in erlaubten Noten ist
        if grade_value < 1 or grade_value > 6:
            flash("Note muss zwischen 1 und 6 liegen", "error")
            return redirect(url_for('main.index'))
        
        # Prüfe ob Note in 0.5er Schritten ist
        if grade_value not in valid_grades:
            flash("Bitte nur Noten in 0.5er Schritten eingeben (1.0, 1.5, 2.0, ...)", "error")
            return redirect(url_for('main.index'))
    except ValueError:
        flash("Ungültige Note", "error")
        return redirect(url_for('main.index'))
    
    # Note erstellen
    grade = Grade(
        subject=subject,
        grade=grade_value,
        grade_type=grade_type,
        description=description,
        user_id=current_user.id
    )
    
    db.session.add(grade)
    db.session.commit()
    
    # Punkte für Note hinzufügen
    if grade_value <= 2.0:
        points = 15
    elif grade_value <= 3.0:
        points = 10
    elif grade_value <= 4.0:
        points = 5
    else:
        points = 2
    
    current_user.add_points(points, 'grade_added', {
        'grade_id': grade.id,
        'subject': subject,
        'grade': grade_value,
        'grade_type': grade_type
    })
    
    flash(f"Note erfolgreich hinzugefügt! +{points} Punkte", "success")
    return redirect(url_for('main.index'))

@grades_bp.route("/delete_note/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    """Note löschen"""
    grade = Grade.query.filter_by(id=note_id, user_id=current_user.id).first()
    if not grade:
        return jsonify({'success': False, 'message': 'Note nicht gefunden'})
    
    db.session.delete(grade)
    db.session.commit()
    
    flash("Note erfolgreich gelöscht!", "success")
    return jsonify({'success': True})

@grades_bp.route("/add_grade_to_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def add_grade_to_task(task_id):
    """Note zu Aufgabe hinzufügen"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        flash("Aufgabe nicht gefunden", "error")
        return redirect(url_for('main.index'))
    
    if request.method == "POST":
        grade_value = request.form.get("grade")
        description = request.form.get("description", "")
        
        try:
            grade_value = float(grade_value)
            if grade_value < 1 or grade_value > 6:
                flash("Note muss zwischen 1 und 6 liegen", "error")
                return render_template("add_grade_to_task.html", task=task)
        except ValueError:
            flash("Ungültige Note", "error")
            return render_template("add_grade_to_task.html", task=task)
        
        # Note erstellen
        grade = Grade(
            subject=task.subject,
            grade=grade_value,
            grade_type="task",
            description=description,
            task_id=task.id,
            user_id=current_user.id
        )
        
        db.session.add(grade)
        db.session.commit()
        
        # Punkte für Note hinzufügen
        if grade_value <= 2.0:
            points = 15
        elif grade_value <= 3.0:
            points = 10
        elif grade_value <= 4.0:
            points = 5
        else:
            points = 2
        
        current_user.add_points(points, 'grade_added', {
            'grade_id': grade.id,
            'task_id': task.id,
            'subject': task.subject,
            'grade': grade_value
        })
        
        flash(f"Note erfolgreich hinzugefügt! +{points} Punkte", "success")
        return redirect(url_for('main.index'))
    
    return render_template("add_grade_to_task.html", task=task)

@grades_bp.route("/semester_grades")
@login_required
def semester_grades():
    """Semester-Noten anzeigen"""
    # Alle Noten des Users
    all_grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp.desc()).all()
    
    # Verfügbare Schuljahre bestimmen
    available_years = set()
    for grade in all_grades:
        grade_year = grade.timestamp.year
        grade_month = grade.timestamp.month
        
        # Bestimme Schuljahr (September bis August)
        if grade_month >= 9:  # Sep-Dez
            school_year = f"{grade_year}/{str(grade_year + 1)[-2:]}"
        else:  # Jan-Aug
            school_year = f"{grade_year - 1}/{str(grade_year)[-2:]}"
        
        available_years.add(school_year)
    
    available_years = sorted(list(available_years), reverse=True)
    
    # Parameter aus URL
    semester = int(request.args.get('semester', 2))  # Standard: 2. Halbjahr
    school_year = request.args.get('school_year', available_years[0] if available_years else '2024/25')
    
    # Parse Schuljahr (z.B. "2024/25" -> 2024, 2025)
    if '/' in school_year:
        start_year, end_year_short = school_year.split('/')
        start_year = int(start_year)
        end_year = int('20' + end_year_short)
    else:
        # Fallback für alte Format
        start_year = int(school_year)
        end_year = start_year + 1
    
    # Filtere nach Halbjahr und Schuljahr
    semester_grades = []
    for grade in all_grades:
        grade_year = grade.timestamp.year
        grade_month = grade.timestamp.month
        
        # Bestimme Schuljahr der Note
        if grade_month >= 9:  # Sep-Dez
            note_school_year_start = grade_year
        else:  # Jan-Aug
            note_school_year_start = grade_year - 1
        
        # Prüfe ob Note zum gewählten Schuljahr gehört
        if note_school_year_start == start_year:
            # Bestimme Halbjahr: 1. Halbjahr = Sep-Jan, 2. Halbjahr = Feb-Aug
            if grade_month >= 9 or grade_month <= 1:
                grade_semester = 1
            else:
                grade_semester = 2
            
            if grade_semester == semester:
                semester_grades.append(grade)
    
    # Gruppiere nach Fach
    grades_by_subject = defaultdict(list)
    for grade in semester_grades:
        grades_by_subject[grade.subject].append(grade)
    
    # Berechne Durchschnitte pro Fach
    subject_averages = {}
    durchschnitt = {}
    for subject, subject_grades in grades_by_subject.items():
        if subject_grades:
            avg = sum(g.grade for g in subject_grades) / len(subject_grades)
            subject_averages[subject] = round(avg, 2)
            durchschnitt[subject] = {
                'average': round(avg, 2),
                'count': len(subject_grades)
            }
    
    # Zeugnis-Durchschnitt (nur Zeugnisnoten)
    certificate_grades = [g for g in semester_grades if g.grade_type == 'certificate']
    if certificate_grades:
        total_average = sum(g.grade for g in certificate_grades) / len(certificate_grades)
        total_average = round(total_average, 2)
    else:
        total_average = 0.00
    
    # Gesamtdurchschnitt aller Noten (alle Typen)
    if semester_grades:
        overall_average = sum(g.grade for g in semester_grades) / len(semester_grades)
        overall_average = round(overall_average, 2)
    else:
        overall_average = 0.00
    
    return render_template("semester_grades.html",
                         grades_by_subject=dict(grades_by_subject),
                         subject_averages=subject_averages,
                         durchschnitt=durchschnitt,
                         overall_average=overall_average,
                         total_average=total_average,
                         semester=semester,
                         school_year=school_year,
                         available_years=available_years,
                         subjects=Config.SUBJECTS,
                         grades=semester_grades)

@grades_bp.route("/certificate_grades")
@login_required
def certificate_grades():
    """Zeugnis-Noten anzeigen"""
    certificate_grades = Grade.query.filter_by(
        user_id=current_user.id,
        grade_type="certificate"
    ).all()
    
    # Gruppiere nach Schuljahr und Halbjahr
    grades_by_period = defaultdict(lambda: {'grades': [], 'average': 0})
    
    for grade in certificate_grades:
        # Verwende das Jahr der Note als Schuljahr
        school_year = grade.timestamp.year
        # Vereinfacht: 1. Halbjahr = Aug-Jan, 2. Halbjahr = Feb-Jul
        semester = 1 if grade.timestamp.month >= 8 or grade.timestamp.month <= 1 else 2
        
        period_key = f"{school_year}-{semester}"
        grades_by_period[period_key]['grades'].append(grade)
        grades_by_period[period_key]['school_year'] = school_year
        grades_by_period[period_key]['semester'] = semester
    
    # Berechne Durchschnitt für jede Periode
    for period_key, period_data in grades_by_period.items():
        if period_data['grades']:
            average = sum(g.grade for g in period_data['grades']) / len(period_data['grades'])
            period_data['average'] = round(average, 2)
    
    # Gesamtdurchschnitt
    if certificate_grades:
        overall_average = sum(g.grade for g in certificate_grades) / len(certificate_grades)
        overall_average = round(overall_average, 2)
    else:
        overall_average = 0
    
    return render_template("certificate_grades.html",
                         grades_by_period=grades_by_period,
                         overall_average=overall_average,
                         subjects=Config.SUBJECTS)

@grades_bp.route("/add_certificate_grades", methods=['GET', 'POST'])
@login_required
def add_certificate_grades():
    """Zeugnis-Noten hinzufügen"""
    from utils.app_settings import get_current_school_year, get_current_semester, get_school_year_options
    
    if request.method == 'POST':
        grades_added = 0
        
        for subject_key, subject_name in Config.SUBJECTS.items():
            grade_value = request.form.get(f'grade_{subject_key}')
            if grade_value:
                try:
                    grade_value = float(grade_value)
                    # Liste der erlaubten Notenwerte (1.0, 1.5, 2.0, usw.)
                    valid_grades = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
                    
                    if 1 <= grade_value <= 6:
                        # Prüfe ob Note in 0.5er Schritten ist
                        if grade_value not in valid_grades:
                            flash(f"Bitte nur Noten in 0.5er Schritten eingeben für {subject_key} (1.0, 1.5, 2.0, ...)", "error")
                            return redirect(url_for('grades.add_certificate_grades'))
                            
                        # Prüfe ob bereits eine Zeugnisnote für dieses Fach existiert
                        existing_grade = Grade.query.filter_by(
                            user_id=current_user.id,
                            subject=subject_key,
                            grade_type='certificate'
                        ).first()
                        
                        if existing_grade:
                            # Update existing grade
                            existing_grade.grade = grade_value
                            existing_grade.timestamp = datetime.utcnow()
                        else:
                            # Create new grade
                            grade = Grade(
                                subject=subject_key,
                                grade=grade_value,
                                grade_type='certificate',
                                description='Zeugnisnote',
                                user_id=current_user.id
                            )
                            db.session.add(grade)
                        
                        grades_added += 1
                except ValueError:
                    flash(f"Ungültige Note für {subject_name}", "error")
                    return redirect(url_for('grades.add_certificate_grades'))
        
        if grades_added > 0:
            db.session.commit()
            flash(f"{grades_added} Zeugnis-Noten erfolgreich gespeichert!", "success")
        else:
            flash("Keine Noten eingegeben", "warning")
        
        return redirect(url_for('grades.certificate_grades'))
    
    # Lade existierende Zeugnisnoten
    existing_grades = {}
    certificate_grades = Grade.query.filter_by(
        user_id=current_user.id,
        grade_type='certificate'
    ).all()
    
    for grade in certificate_grades:
        existing_grades[grade.subject] = grade.grade
    
    return render_template('add_certificate_grades.html', 
                         subjects=Config.SUBJECTS,
                         existing_grades=existing_grades,
                         current_school_year=get_current_school_year(),
                         current_semester=get_current_semester(),
                         school_year_options=get_school_year_options())

@grades_bp.route("/grade_progress")
@login_required
def grade_progress():
    """Notenentwicklung anzeigen"""
    grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp).all()
    
    # Gruppiere nach Fach und sortiere chronologisch
    grades_by_subject = defaultdict(list)
    for grade in grades:
        grades_by_subject[grade.subject].append(grade)
    
    # Erstelle progress_data Struktur für Template
    progress_data = {}
    for subject, subject_grades in grades_by_subject.items():
        # Trenne nach Noten-Typ
        regular_grades = [g for g in subject_grades if g.grade_type in ['normal', 'test']]
        certificate_grades = [g for g in subject_grades if g.grade_type == 'certificate']
        
        # Nur Fächer hinzufügen, die tatsächlich Noten haben
        if regular_grades or certificate_grades:
            progress_data[subject] = {
                'regular_grades': regular_grades,
                'final_grades': certificate_grades  # Template erwartet 'final_grades'
            }
    
    # Berechne Trends
    subject_trends = {}
    for subject, subject_grades in grades_by_subject.items():
        if len(subject_grades) >= 2:
            first_grade = subject_grades[0].grade
            last_grade = subject_grades[-1].grade
            
            if last_grade < first_grade:
                trend = "improving"
            elif last_grade > first_grade:
                trend = "declining"
            else:
                trend = "stable"
            
            subject_trends[subject] = {
                'trend': trend,
                'first_grade': first_grade,
                'last_grade': last_grade,
                'improvement': round(first_grade - last_grade, 2)
            }
    
    # Berechne Semester-Durchschnitte
    semester_averages = defaultdict(lambda: {'grades': [], 'average': 0, 'school_year': 0, 'semester': 0})
    
    for grade in grades:
        # Verwende das Jahr der Note als Schuljahr
        school_year = grade.timestamp.year
        # Vereinfacht: 1. Halbjahr = Aug-Jan, 2. Halbjahr = Feb-Jul
        semester = 1 if grade.timestamp.month >= 8 or grade.timestamp.month <= 1 else 2
        
        period_key = f"{school_year}-{semester}"
        semester_averages[period_key]['grades'].append(grade)
        semester_averages[period_key]['school_year'] = school_year
        semester_averages[period_key]['semester'] = semester
    
    # Berechne Durchschnitt für jede Periode
    for period_key, period_data in semester_averages.items():
        if period_data['grades']:
            average = sum(g.grade for g in period_data['grades']) / len(period_data['grades'])
            period_data['average'] = round(average, 2)
    
    return render_template("grade_progress.html",
                         grades_by_subject=dict(grades_by_subject),
                         subject_trends=subject_trends,
                         semester_averages=dict(semester_averages),
                         progress_data=progress_data)
