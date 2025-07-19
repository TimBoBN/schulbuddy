"""
Routes package for SchulBuddy
"""
from flask import Blueprint

def register_routes(app):
    """Register all route blueprints with the app"""
    from .auth import auth_bp
    from .admin import admin_bp
    from .tasks import tasks_bp
    from .grades import grades_bp
    from .statistics import statistics_bp
    from .main import main_bp
    from .timer import timer_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(tasks_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(timer_bp)
