"""Migration: add WebUntis credential columns to users table.

Run with: python migrations/001_add_webuntis_credentials.py

This script checks whether the columns exist and only adds the missing ones (SQLite compatible ALTER TABLE ADD COLUMN).
"""
from app import create_app
from models import db
from sqlalchemy import text


def run_migration():
    app = create_app()
    with app.app_context():
        # get existing columns
        res = db.session.execute(text("PRAGMA table_info('users');"))
        existing = [row[1] for row in res.fetchall()]

        stmts = []
        if 'webuntis_server' not in existing:
            stmts.append("ALTER TABLE users ADD COLUMN webuntis_server VARCHAR(200);")
        if 'webuntis_school' not in existing:
            stmts.append("ALTER TABLE users ADD COLUMN webuntis_school VARCHAR(200);")
        if 'webuntis_username' not in existing:
            stmts.append("ALTER TABLE users ADD COLUMN webuntis_username VARCHAR(200);")
        if 'webuntis_password_enc' not in existing:
            stmts.append("ALTER TABLE users ADD COLUMN webuntis_password_enc TEXT;")

        if not stmts:
            print('No migration needed: all columns already exist.')
            return

        print('Applying migration: adding columns to users table...')
        for s in stmts:
            print('Executing:', s)
            db.session.execute(text(s))
        db.session.commit()
        print('Migration applied. Please restart the app if running.')


if __name__ == '__main__':
    run_migration()
