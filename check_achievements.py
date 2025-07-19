from app import app
from models import db, Achievement, init_achievements

with app.app_context():
    count = Achievement.query.count()
    print(f"Achievements in DB: {count}")
    if count == 0:
        print("Initialisiere Achievements...")
        init_achievements()
        print("Achievements wurden erstellt!")
    else:
        print("Achievements sind bereits vorhanden.")
