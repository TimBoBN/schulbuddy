"""
API Security Decorators für SchulBuddy
"""

from functools import wraps
from flask import request, jsonify, current_app
from flask_login import current_user
from models import User


def api_key_required(f):
    """Decorator für API-Key-Authentifizierung"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prüfe API-Key in verschiedenen Formaten
        api_key = None

        # 1. Authorization Header (Bearer Token)
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.split(" ")[1]

        # 2. Query Parameter
        if not api_key:
            api_key = request.args.get("api_key")

        # 3. JSON Body
        if not api_key and request.is_json:
            api_key = request.json.get("api_key")

        # 4. Form Data
        if not api_key:
            api_key = request.form.get("api_key")

        if not api_key:
            return (
                jsonify(
                    {
                        "error": "API-Key erforderlich",
                        "message": "Bitte geben Sie einen gültigen API-Key an",
                        "formats": [
                            "Header: Authorization: Bearer <api_key>",
                            "Query: ?api_key=<api_key>",
                            'JSON: {"api_key": "<api_key>"}',
                            "Form: api_key=<api_key>",
                        ],
                    }
                ),
                401,
            )

        # Suche User mit diesem API-Key
        user = User.query.filter_by(api_key=api_key).first()
        if not user or not user.verify_api_key(api_key):
            return (
                jsonify(
                    {
                        "error": "Ungültiger API-Key",
                        "message": "Der angegebene API-Key ist ungültig oder abgelaufen",
                    }
                ),
                401,
            )

        # Setze User für Request
        request.api_user = user
        return f(*args, **kwargs)

    return decorated_function


def api_key_or_login_required(f):
    """Decorator für API-Key ODER Login-Authentifizierung"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Prüfe zuerst ob User eingeloggt ist
        if current_user.is_authenticated:
            request.api_user = current_user
            return f(*args, **kwargs)

        # Ansonsten API-Key prüfen
        return api_key_required(f)(*args, **kwargs)

    return decorated_function
