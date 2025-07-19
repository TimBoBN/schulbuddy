#!/usr/bin/env python3
"""
Debug-Script zum Überprüfen der Template-Variablen
"""

from app import app, db
from models import Task, User
from config import Config
from flask import render_template_string

def debug_template_vars():
    with app.app_context():
        # Einen User und Task abrufen
        user = User.query.first()
        if not user:
            print("Kein User gefunden!")
            return
            
        task = Task.query.filter_by(user_id=user.id).first()
        if not task:
            print("Keine Task gefunden!")
            return
            
        print("=== DEBUG OUTPUT ===")
        print(f"Config.SUBJECTS: {Config.SUBJECTS}")
        print(f"task.subject: '{task.subject}'")
        print(f"task.subject type: {type(task.subject)}")
        
        # Test subject anzeige
        if task.subject in Config.SUBJECTS:
            print(f"✅ task.subject '{task.subject}' ist in Config.SUBJECTS")
            print(f"Color code: {Config.SUBJECTS[task.subject]}")
        else:
            print(f"❌ task.subject '{task.subject}' ist NICHT in Config.SUBJECTS")
            print(f"Verfügbare Subjects: {list(Config.SUBJECTS.keys())}")
        
        # Template test
        template = """
Subject name: {{ task.subject }}
Subject in subjects: {{ task.subject in subjects }}
{% if task.subject in subjects %}
Color: {{ subjects[task.subject] }}
{% endif %}

Subjects loop:
{% for name, color in subjects.items() %}
- {{ name }}: {{ color }}
{% endfor %}
        """
        
        rendered = render_template_string(template, task=task, subjects=Config.SUBJECTS)
        print("=== TEMPLATE RENDER ===")
        print(rendered)

if __name__ == "__main__":
    debug_template_vars()
