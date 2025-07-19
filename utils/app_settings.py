"""
Utility-Funktionen für SchulBuddy
"""

def get_current_school_year():
    """Hole das aktuelle Schuljahr aus den App-Einstellungen"""
    try:
        from models import AppSettings
        return AppSettings.get_setting('current_school_year', '2025/26')
    except:
        return '2025/26'

def get_current_semester():
    """Hole das aktuelle Semester aus den App-Einstellungen"""
    try:
        from models import AppSettings
        return int(AppSettings.get_setting('current_semester', '1'))
    except:
        return 1

def get_school_year_options():
    """Generiere Schuljahr-Optionen für Dropdowns"""
    current_year = get_current_school_year()
    
    # Generiere 5 Jahre zurück und 3 Jahre voraus
    import datetime
    try:
        start_year = int(current_year.split('/')[0])
    except:
        start_year = 2025
    
    options = []
    for year in range(start_year - 2, start_year + 4):
        year_str = f"{year}/{str(year+1)[-2:]}"
        options.append(year_str)
    
    return options

def get_app_setting(key, default=None):
    """Hole eine App-Einstellung"""
    try:
        from models import AppSettings
        return AppSettings.get_setting(key, default)
    except:
        return default
