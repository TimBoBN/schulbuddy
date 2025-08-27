import os
import sqlite3

# Pfad zur DB (relativ zum Repo root)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'schulbuddy.db'))

print('Using DB:', DB_PATH)
if not os.path.exists(DB_PATH):
    print('ERROR: Database file not found at', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("PRAGMA table_info('study_sessions')")
cols = [row[1] for row in cur.fetchall()]
print('Existing columns:', cols)

changes = []

if 'is_paused' not in cols:
    cur.execute("ALTER TABLE study_sessions ADD COLUMN is_paused INTEGER DEFAULT 0")
    changes.append('is_paused')
if 'paused_at' not in cols:
    cur.execute("ALTER TABLE study_sessions ADD COLUMN paused_at DATETIME NULL")
    changes.append('paused_at')
if 'accumulated_seconds' not in cols:
    cur.execute("ALTER TABLE study_sessions ADD COLUMN accumulated_seconds INTEGER DEFAULT 0")
    changes.append('accumulated_seconds')

conn.commit()

if changes:
    print('Added columns:', changes)
else:
    print('No changes required; all columns present.')

conn.close()
