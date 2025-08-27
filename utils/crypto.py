from cryptography.fernet import Fernet
import base64
import hashlib
from flask import current_app


def _derive_key(secret_key: str) -> bytes:
    """Leitet aus Flask SECRET_KEY einen 32-Byte key für Fernet ab (base64-url-safe)."""
    if not secret_key:
        raise RuntimeError('Flask SECRET_KEY is not set')
    # SHA256 und base64-url-safe
    digest = hashlib.sha256(secret_key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(plaintext: str) -> str:
    key = _derive_key(current_app.config.get('SECRET_KEY', ''))
    f = Fernet(key)
    token = f.encrypt(plaintext.encode('utf-8'))
    return token.decode('utf-8')


def decrypt_text(token: str) -> str:
    key = _derive_key(current_app.config.get('SECRET_KEY', ''))
    f = Fernet(key)
    return f.decrypt(token.encode('utf-8')).decode('utf-8')
