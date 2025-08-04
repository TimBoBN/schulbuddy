"""
Statistics and gamification routes for SchulBuddy
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from collections import defaultdict
import csv
import io

from models import Task, Grade, ActivityLog, Achievement, UserAchievement, Notification, UserStatistic, db
from config import Config

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/statistics')
@login_required
def statistics():
    """Statistiken und Lernfortschritt"""
    try:
        # Aktualisiere heutige Statistiken
        UserStatistic.update_daily_stats(current_user.id)
        
        # Basis-Statistiken (aktuell verfügbare Tasks)
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
        total_grades = Grade.query.filter_by(user_id=current_user.id).count()
        
        # Historische Statistiken aus UserStatistic (überleben Löschungen)
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        # Heatmap-Daten basierend auf UserStatistic (statt ActivityLog)
        activity_data = defaultdict(int)
        stats = UserStatistic.query.filter(
            UserStatistic.user_id == current_user.id,
            UserStatistic.date >= start_date
        ).all()
        
        for stat in stats:
            activity_date = stat.date.isoformat()
            # Aktivität = abgeschlossene Aufgaben + hinzugefügte Noten
            activity_data[activity_date] = stat.tasks_completed + stat.grades_added
        
        # Wöchentliche Statistiken basierend auf UserStatistic
        weekly_stats = defaultdict(lambda: {'tasks': 0, 'grades': 0})
        for i in range(8):  # Letzte 8 Wochen
            week_start = end_date - timedelta(weeks=i, days=end_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_stats = UserStatistic.query.filter(
                UserStatistic.user_id == current_user.id,
                UserStatistic.date >= week_start,
                UserStatistic.date <= week_end
            ).all()
            
            week_tasks = sum(s.tasks_completed for s in week_stats)
            week_grades = sum(s.grades_added for s in week_stats)
            
            weekly_stats[week_start.strftime('%Y-W%U')] = {
                'tasks': week_tasks,
                'grades': week_grades,
                'week_start': week_start.strftime('%d.%m')
            }
        
        # Fach-Performance und Notenentwicklungs-Daten
        subject_performance = {}
        grade_progression_data = {}
        school_year_comparison = {}
        
        for subject in Config.SUBJECTS.keys():
            subject_grades = Grade.query.filter_by(
                user_id=current_user.id,
                subject=subject
            ).order_by(Grade.timestamp).all()
            
            if subject_grades:
                # Normale Noten (Tests, Klassenarbeiten, etc.)
                normal_grades = [g for g in subject_grades if g.grade_type != 'certificate']
                # Zeugnisnoten
                certificate_grades = [g for g in subject_grades if g.grade_type == 'certificate']
                
                avg_grade = sum(g.grade for g in subject_grades) / len(subject_grades)
                subject_performance[subject] = {
                    'average': round(avg_grade, 2),
                    'count': len(subject_grades),
                    'normal_count': len(normal_grades),
                    'certificate_count': len(certificate_grades),
                    'trend': 'improving' if len(subject_grades) > 1 and subject_grades[-1].grade < avg_grade else 'stable'
                }
                
                # Daten für Notenentwicklungs-Graph vorbereiten
                if subject_grades:
                    grade_progression_data[subject] = {
                        'dates': [g.timestamp.strftime('%Y-%m-%d') for g in subject_grades],
                        'grades': [g.grade for g in subject_grades],
                        'descriptions': [g.description or 'Unbekannt' for g in subject_grades],
                        'types': [g.grade_type for g in subject_grades]
                    }
        
        # Schuljahr-Vergleichsdaten
        all_grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp).all()
        grades_by_year = defaultdict(list)
        
        for grade in all_grades:
            grade_year = grade.timestamp.year
            grade_month = grade.timestamp.month
            
            # Bestimme Schuljahr (September bis August)
            if grade_month >= 9:  # Sep-Dez
                school_year = f"{grade_year}/{str(grade_year + 1)[-2:]}"
            else:  # Jan-Aug
                school_year = f"{grade_year - 1}/{str(grade_year)[-2:]}"
            
            grades_by_year[school_year].append(grade)
        
        for year, year_grades in grades_by_year.items():
            if year_grades:
                year_avg = sum(g.grade for g in year_grades) / len(year_grades)
                school_year_comparison[year] = {
                    'average': round(year_avg, 2),
                    'count': len(year_grades)
                }
        
        # Timer-Statistiken hinzufügen
        from models import StudySession
        
        # Gesamt-Timer-Statistiken
        total_study_sessions = StudySession.query.filter_by(user_id=current_user.id, completed=True).count()
        total_study_time = db.session.query(
            db.func.sum(StudySession.actual_duration_seconds)
        ).filter_by(user_id=current_user.id, completed=True).scalar() or 0
        total_study_hours = round(total_study_time / 3600, 1)
        
        # Heutige Timer-Statistiken
        today = datetime.now().date()
        today_sessions = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            StudySession.completed == True,
            StudySession.start_time >= today,
            StudySession.start_time < today + timedelta(days=1)
        ).all()
        
        today_study_time = sum(s.actual_duration_seconds for s in today_sessions) if today_sessions else 0
        today_study_minutes = round(today_study_time / 60)
        
        return render_template('statistics.html',
                             total_tasks=total_tasks,
                             completed_tasks=completed_tasks,
                             total_grades=total_grades,
                             activity_data=dict(activity_data),
                             weekly_stats=dict(weekly_stats),
                             subject_performance=subject_performance,
                             grade_progression_data=grade_progression_data,
                             school_year_comparison=school_year_comparison,
                             user=current_user,
                             total_study_sessions=total_study_sessions,
                             total_study_hours=total_study_hours,
                             today_study_minutes=today_study_minutes,
                             today_sessions_count=len(today_sessions))
    except Exception as e:
        flash("Fehler beim Laden der Statistiken", "error")
        return redirect(url_for('main.index'))

@statistics_bp.route('/achievements')
@login_required
def achievements():
    """Achievements und Gamification"""
    try:
        # Alle verfügbaren Achievements
        all_achievements = Achievement.query.all()
        
        # Benutzer-Achievements
        user_achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
        earned_achievement_ids = [ua.achievement_id for ua in user_achievements]
        
        # Gruppiere Achievements
        earned_achievements = []
        available_achievements = []
        
        # Progress dictionary für alle Achievements
        progress = {}
        
        for achievement in all_achievements:
            if achievement.id in earned_achievement_ids:
                # Finde das UserAchievement für das Datum
                user_achievement = next(ua for ua in user_achievements if ua.achievement_id == achievement.id)
                earned_achievements.append({
                    'achievement': achievement,
                    'earned_at': user_achievement.earned_at
                })
                progress[achievement.id] = 100  # Completed achievements are at 100%
            else:
                available_achievements.append(achievement)
                # Berechne tatsächlichen Progress für verfügbare Achievements
                current_progress = 0
                
                if achievement.condition_type == 'level':
                    current_progress = min(100, (current_user.level / achievement.condition_value) * 100)
                elif achievement.condition_type == 'points':
                    current_progress = min(100, (current_user.total_points / achievement.condition_value) * 100)
                elif achievement.condition_type == 'streak':
                    current_progress = min(100, (current_user.current_streak / achievement.condition_value) * 100)
                elif achievement.condition_type == 'tasks_completed':
                    from models import Task
                    completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
                    current_progress = min(100, (completed_tasks / achievement.condition_value) * 100)
                
                progress[achievement.id] = round(current_progress, 1)
        
        # Sortiere nach Datum (neueste zuerst)
        earned_achievements.sort(key=lambda x: x['earned_at'], reverse=True)
        
        return render_template('achievements.html',
                             earned_achievements=earned_achievements,
                             available_achievements=available_achievements,
                             progress=progress,
                             user=current_user)
    except Exception as e:
        flash("Fehler beim Laden der Achievements", "error")
        return redirect(url_for('main.index'))

@statistics_bp.route('/notifications')
@login_required
def notifications():
    """Benachrichtigungen anzeigen"""
    try:
        # Alle Benachrichtigungen des Benutzers
        notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.id.desc()).all()
        
        # Zähle ungelesene Benachrichtigungen
        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        # Markiere alle als gelesen
        unread_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).all()
        
        for notification in unread_notifications:
            notification.is_read = True
        
        db.session.commit()
        
        return render_template('notifications.html', 
                             notifications=notifications,
                             unread_count=unread_count)
    except Exception as e:
        flash("Fehler beim Laden der Benachrichtigungen", "error")
        return redirect(url_for('main.index'))

@statistics_bp.route('/mark_notification_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """Benachrichtigung als gelesen markieren"""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if notification:
            notification.is_read = True
            db.session.commit()
        
        return redirect(url_for('statistics.notifications'))
    except Exception as e:
        flash("Fehler beim Markieren der Benachrichtigung", "error")
        return redirect(url_for('statistics.notifications'))

@statistics_bp.route('/export_data')
@login_required
def export_data():
    """Export-Auswahlseite anzeigen"""
    return render_template('export_selection.html')

@statistics_bp.route('/export_csv')
@login_required
def export_csv():
    """Daten als schön formatierte Excel/CSV exportieren"""
    try:
        import pandas as pd
        import xlsxwriter
        from config import Config
        
        # Aufgaben sammeln
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.due_date.desc()).all()
        tasks_data = []
        
        for task in tasks:
            priority_text = {
                'exam': 'Höchste (Klassenarbeit)',
                'test': 'Hoch (Test)', 
                'project': 'Mittel (Projekt)',
                'homework': 'Niedrig (Hausaufgabe)',
                'other': 'Niedrig (Sonstiges)'
            }.get(task.task_type, 'Unbekannt')
            
            type_text = {
                'exam': 'Klassenarbeit',
                'test': 'Test',
                'project': 'Projekt', 
                'homework': 'Hausaufgabe',
                'other': 'Sonstiges'
            }.get(task.task_type, task.task_type.capitalize())
            
            tasks_data.append({
                'Titel': task.title,
                'Fach': Config.SUBJECTS.get(task.subject, task.subject),
                'Typ': type_text,
                'Priorität': priority_text,
                'Beschreibung': task.description or '-',
                'Fälligkeitsdatum': task.due_date.strftime('%d.%m.%Y') if task.due_date else '-',
                'Status': 'Erledigt' if task.completed else 'Offen',
                'Erledigt am': task.completed_date.strftime('%d.%m.%Y %H:%M') if task.completed_date else '-',
                'Erstellt am': task.created_at.strftime('%d.%m.%Y %H:%M') if task.created_at else '-'
            })
        
        # Noten sammeln
        grades = Grade.query.filter_by(user_id=current_user.id).order_by(Grade.timestamp.desc()).all()
        grades_data = []
        
        for grade in grades:
            grade_type_text = {
                'homework': 'Hausaufgaben-Note',
                'exam': 'Klassenarbeit', 
                'test': 'Test',
                'project': 'Projekt',
                'participation': 'Mitarbeit',
                'certificate': 'Zeugnisnote'
            }.get(grade.grade_type, grade.grade_type)
            
            grades_data.append({
                'Beschreibung': grade.description,
                'Fach': Config.SUBJECTS.get(grade.subject, grade.subject),
                'Note': grade.grade,
                'Notentyp': grade_type_text,
                'Gewichtung': grade.weight,
                'Datum': grade.timestamp.strftime('%d.%m.%Y'),
                'Notiert am': grade.timestamp.strftime('%d.%m.%Y %H:%M')
            })
        
        # Excel-Writer mit mehreren Sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Formatierungen definieren
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BD',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1
            })
            
            date_format = workbook.add_format({
                'text_wrap': True,
                'valign': 'top',
                'border': 1,
                'num_format': 'dd.mm.yyyy'
            })
            
            # Übersichtsblatt
            overview_data = {
                'Statistik': [
                    'Gesamtanzahl Aufgaben',
                    'Erledigte Aufgaben', 
                    'Offene Aufgaben',
                    'Überfällige Aufgaben',
                    'Gesamtanzahl Noten',
                    'Durchschnittsnote',
                    'Beste Note',
                    'Schlechteste Note',
                    'Aktueller Level',
                    'Aktuelle Streak',
                    'Export-Datum'
                ],
                'Wert': [
                    len(tasks),
                    len([t for t in tasks if t.completed]),
                    len([t for t in tasks if not t.completed]),
                    len([t for t in tasks if not t.completed and t.due_date and t.due_date < datetime.now().date()]),
                    len(grades),
                    f"{sum(g.grade for g in grades)/len(grades):.2f}" if grades else 'Keine Noten',
                    f"{min(g.grade for g in grades):.1f}" if grades else 'Keine Noten',
                    f"{max(g.grade for g in grades):.1f}" if grades else 'Keine Noten', 
                    current_user.level,
                    current_user.current_streak,
                    datetime.now().strftime('%d.%m.%Y %H:%M')
                ]
            }
            
            # Übersicht-Sheet mit Formatierung
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Übersicht', index=False)
            worksheet = writer.sheets['Übersicht']
            
            # Header formatieren
            for col_num, value in enumerate(overview_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Daten formatieren
            for row_num in range(1, len(overview_df) + 1):
                for col_num in range(len(overview_df.columns)):
                    worksheet.write(row_num, col_num, overview_df.iloc[row_num-1, col_num], cell_format)
            
            # Spaltenbreite anpassen
            worksheet.set_column('A:A', 25)
            worksheet.set_column('B:B', 20)
            
            # Aufgaben-Sheet
            if tasks_data:
                tasks_df = pd.DataFrame(tasks_data)
                tasks_df.to_excel(writer, sheet_name='Aufgaben', index=False)
                tasks_worksheet = writer.sheets['Aufgaben']
                
                # Header formatieren
                for col_num, value in enumerate(tasks_df.columns.values):
                    tasks_worksheet.write(0, col_num, value, header_format)
                
                # Spaltenbreiten anpassen
                tasks_worksheet.set_column('A:A', 30)  # Titel
                tasks_worksheet.set_column('B:B', 15)  # Fach
                tasks_worksheet.set_column('C:C', 12)  # Typ
                tasks_worksheet.set_column('D:D', 25)  # Priorität
                tasks_worksheet.set_column('E:E', 40)  # Beschreibung
                tasks_worksheet.set_column('F:F', 15)  # Fälligkeitsdatum
                tasks_worksheet.set_column('G:G', 12)  # Status
                tasks_worksheet.set_column('H:H', 18)  # Erledigt am
                tasks_worksheet.set_column('I:I', 18)  # Erstellt am
            
            # Noten-Sheet  
            if grades_data:
                grades_df = pd.DataFrame(grades_data)
                grades_df.to_excel(writer, sheet_name='Noten', index=False)
                grades_worksheet = writer.sheets['Noten']
                
                # Header formatieren
                for col_num, value in enumerate(grades_df.columns.values):
                    grades_worksheet.write(0, col_num, value, header_format)
                
                # Spaltenbreiten anpassen
                grades_worksheet.set_column('A:A', 30)  # Beschreibung
                grades_worksheet.set_column('B:B', 15)  # Fach
                grades_worksheet.set_column('C:C', 8)   # Note
                grades_worksheet.set_column('D:D', 18)  # Notentyp
                grades_worksheet.set_column('E:E', 12)  # Gewichtung
                grades_worksheet.set_column('F:F', 12)  # Datum
                grades_worksheet.set_column('G:G', 18)  # Notiert am
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'schulbuddy_export_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ImportError as e:
        flash(f"Fehlende Bibliothek für Excel-Export: {str(e)}. Bitte installieren Sie pandas und xlsxwriter.", "error")
        return redirect(url_for('statistics.export_data'))
    except Exception as e:
        flash(f"Fehler beim Excel-Export: {str(e)}", "error")
        return redirect(url_for('statistics.export_data'))

@statistics_bp.route('/export_pdf')
@login_required  
def export_pdf():
    """Daten als schön formatierte PDF exportieren"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from config import Config
        
        buffer = io.BytesIO()
        
        # PDF-Dokument erstellen
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            topMargin=2*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=0.5*inch,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'], 
            fontSize=16,
            textColor=colors.darkblue,
            spaceAfter=0.3*inch,
            spaceBefore=0.3*inch
        )
        
        content = []
        
        # Titel
        content.append(Paragraph("📚 SchulBuddy Datenexport", title_style))
        content.append(Paragraph(f"Benutzer: {current_user.username}", styles['Normal']))
        content.append(Paragraph(f"Export-Datum: {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}", styles['Normal']))
        content.append(Spacer(1, 0.5*inch))
        
        # Übersicht
        content.append(Paragraph("📊 Übersicht", heading_style))
        
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        grades = Grade.query.filter_by(user_id=current_user.id).all()
        completed_tasks = [t for t in tasks if t.completed]
        open_tasks = [t for t in tasks if not t.completed]
        overdue_tasks = [t for t in open_tasks if t.due_date and t.due_date < datetime.now().date()]
        
        overview_data = [
            ['📝 Aufgaben gesamt:', str(len(tasks))],
            ['✅ Erledigt:', str(len(completed_tasks))],
            ['⏳ Offen:', str(len(open_tasks))],
            ['⚠️ Überfällig:', str(len(overdue_tasks))],
            ['📊 Noten gesamt:', str(len(grades))],
            ['🎯 Durchschnitt:', f"{sum(g.grade for g in grades)/len(grades):.2f}" if grades else 'Keine Noten'],
            ['🏆 Level:', str(current_user.level)],
            ['🔥 Streak:', str(current_user.current_streak)]
        ]
        
        overview_table = Table(overview_data, colWidths=[3*inch, 1*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        content.append(overview_table)
        content.append(Spacer(1, 0.3*inch))
        
        # Aufgaben
        if tasks:
            content.append(Paragraph("📝 Aufgaben", heading_style))
            
            tasks_data = [['Titel', 'Fach', 'Typ', 'Status', 'Fällig am']]
            for task in sorted(tasks, key=lambda x: x.due_date or datetime(2099, 12, 31).date(), reverse=True)[:20]:  # Nur die neuesten 20
                priority_icon = {
                    'exam': '🔴',
                    'test': '🟡', 
                    'project': '🟠',
                    'homework': '🟢',
                    'other': '⚪'
                }.get(task.task_type, '⚪')
                
                tasks_data.append([
                    f"{priority_icon} {task.title[:30]}{'...' if len(task.title) > 30 else ''}",
                    Config.SUBJECTS.get(task.subject, task.subject)[:15],
                    task.task_type.capitalize(),
                    '✅ Erledigt' if task.completed else '⏳ Offen',
                    task.due_date.strftime('%d.%m.%Y') if task.due_date else '-'
                ])
            
            tasks_table = Table(tasks_data, colWidths=[2.5*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
            tasks_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            content.append(tasks_table)
        
        content.append(PageBreak())
        
        # Noten
        if grades:
            content.append(Paragraph("📊 Noten", heading_style))
            
            grades_data = [['Beschreibung', 'Fach', 'Note', 'Typ', 'Datum']]
            for grade in sorted(grades, key=lambda x: x.timestamp, reverse=True)[:25]:  # Nur die neuesten 25
                grade_emoji = '🟢' if grade.grade <= 2.0 else '🟡' if grade.grade <= 3.0 else '🟠' if grade.grade <= 4.0 else '🔴'
                
                grades_data.append([
                    f"{grade.description[:25]}{'...' if len(grade.description) > 25 else ''}",
                    Config.SUBJECTS.get(grade.subject, grade.subject)[:12],
                    f"{grade_emoji} {grade.grade}",
                    grade.grade_type.capitalize(),
                    grade.timestamp.strftime('%d.%m.%Y')
                ])
            
            grades_table = Table(grades_data, colWidths=[2.2*inch, 1.2*inch, 0.8*inch, 1*inch, 0.9*inch])
            grades_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            content.append(grades_table)
        
        # Footer
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph("Erstellt mit SchulBuddy 📚", styles['Normal']))
        
        # PDF generieren
        doc.build(content)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'schulbuddy_export_{current_user.username}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f"Fehler beim PDF-Export: {str(e)}", "error")
        return redirect(url_for('statistics.export_data'))

@statistics_bp.route('/streaks')
@login_required
def streaks():
    """Lernstreak-Seite wie bei Duolingo"""
    try:
        # Aktualisiere Streak vor der Anzeige
        current_user.update_streak()
        
        # Basis-Streak-Daten
        current_streak = current_user.current_streak
        longest_streak = current_user.longest_streak
        
        # Berechne Streak-Kalender für die letzten 365 Tage
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        # Sammle alle Aktivitätstage aus UserStatistic (statt Task/ActivityLog)
        activity_days = set()
        stats = UserStatistic.query.filter(
            UserStatistic.user_id == current_user.id,
            UserStatistic.date >= start_date
        ).all()
        
        for stat in stats:
            # Ein Tag gilt als aktiv, wenn Aufgaben abgeschlossen oder Noten hinzugefügt wurden
            if stat.tasks_completed > 0 or stat.grades_added > 0:
                activity_days.add(stat.date)
        
        # Fallback: Füge auch ActivityLog-Daten hinzu (für Rückwärtskompatibilität)
        activities = ActivityLog.query.filter(
            ActivityLog.user_id == current_user.id,
            ActivityLog.created_at >= start_date
        ).all()
        
        for activity in activities:
            activity_days.add(activity.created_at.date())
        
        # Erstelle Kalender-Daten für die letzten 365 Tage
        calendar_data = []
        current_date = start_date
        
        while current_date <= end_date:
            is_active = current_date in activity_days
            calendar_data.append({
                'date': current_date.isoformat(),
                'active': is_active,
                'day_of_week': current_date.weekday(),
                'is_today': current_date == end_date,
                'is_weekend': current_date.weekday() >= 5
            })
            current_date += timedelta(days=1)
        
        # Berechne Streak-Statistiken
        streak_stats = calculate_streak_stats(activity_days, end_date)
        
        # Streak-Ziele und Belohnungen
        streak_goals = [
            {'days': 3, 'title': 'Erste Schritte', 'icon': '🔥', 'reward': '10 Punkte'},
            {'days': 7, 'title': 'Woche geschafft!', 'icon': '⚡', 'reward': '25 Punkte'},
            {'days': 14, 'title': 'Zwei Wochen Disziplin', 'icon': '💪', 'reward': '50 Punkte'},
            {'days': 30, 'title': 'Ein Monat stark!', 'icon': '🏆', 'reward': '100 Punkte'},
            {'days': 60, 'title': 'Lernmaschine', 'icon': '🚀', 'reward': '200 Punkte'},
            {'days': 100, 'title': 'Jahrhundert-Streak!', 'icon': '👑', 'reward': '500 Punkte'},
            {'days': 365, 'title': 'Ein ganzes Jahr!', 'icon': '🌟', 'reward': '1000 Punkte'}
        ]
        
        # Markiere erreichte Ziele
        for goal in streak_goals:
            goal['achieved'] = longest_streak >= goal['days']
            goal['current_achieved'] = current_streak >= goal['days']
        
        # Wöchentliche Streak-Übersicht
        weekly_streaks = []
        for i in range(12):  # Letzte 12 Wochen
            week_start = end_date - timedelta(weeks=i, days=end_date.weekday())
            week_end = week_start + timedelta(days=6)
            
            week_days = []
            for j in range(7):
                check_date = week_start + timedelta(days=j)
                if check_date <= end_date:
                    week_days.append({
                        'date': check_date,
                        'active': check_date in activity_days
                    })
            
            weekly_streaks.insert(0, {
                'week_start': week_start,
                'days': week_days
            })
        
        return render_template('streaks.html',
                             current_streak=current_streak,
                             longest_streak=longest_streak,
                             calendar_data=calendar_data,
                             streak_stats=streak_stats,
                             streak_goals=streak_goals,
                             weekly_streaks=weekly_streaks,
                             total_active_days=len(activity_days),
                             user=current_user,
                             date=date)
        
    except Exception as e:
        flash(f"Fehler beim Laden der Streak-Daten: {str(e)}", "error")
        return redirect(url_for('statistics.statistics'))

def calculate_streak_stats(activity_days, end_date):
    """Berechne erweiterte Streak-Statistiken"""
    stats = {
        'current_month_days': 0,
        'last_month_days': 0,
        'average_weekly_days': 0,
        'best_week_days': 0,
        'total_weeks_active': 0
    }
    
    # Aktueller Monat
    month_start = end_date.replace(day=1)
    current_month_days = [d for d in activity_days if d >= month_start and d <= end_date]
    stats['current_month_days'] = len(current_month_days)
    
    # Letzter Monat
    if month_start.month == 1:
        last_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        last_month_start = month_start.replace(month=month_start.month - 1)
    last_month_end = month_start - timedelta(days=1)
    
    last_month_days = [d for d in activity_days if d >= last_month_start and d <= last_month_end]
    stats['last_month_days'] = len(last_month_days)
    
    # Wöchentliche Statistiken
    week_counts = []
    for i in range(52):  # Letzte 52 Wochen
        week_start = end_date - timedelta(weeks=i, days=end_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        week_days = [d for d in activity_days if d >= week_start and d <= week_end]
        if week_days:
            week_counts.append(len(week_days))
            stats['total_weeks_active'] += 1
    
    if week_counts:
        stats['average_weekly_days'] = round(sum(week_counts) / len(week_counts), 1)
        stats['best_week_days'] = max(week_counts)
    
    return stats
