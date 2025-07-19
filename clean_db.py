"""
Datenbank-Bereinigungsskript für SchulBuddy
Kann direkt in Python ausgeführt werden
"""

import os
import sqlite3
import shutil
from datetime import datetime
import sys

def create_backup(db_path, backup_dir="backups"):
    """Erstellt ein Backup der Datenbank"""
    if not os.path.exists(db_path):
        print("❌ Keine Datenbank gefunden zum Backup!")
        return None
    
    # Backup-Verzeichnis erstellen
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup-Name mit Zeitstempel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"schulbuddy_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Kopieren
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup erstellt: {backup_path}")
    return backup_path

def get_db_info(db_path):
    """Zeigt Informationen über die Datenbank"""
    if not os.path.exists(db_path):
        print("❌ Datenbank nicht gefunden!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Datei-Info
        size = os.path.getsize(db_path)
        size_mb = size / (1024 * 1024)
        print(f"📊 Datenbank: {db_path}")
        print(f"📏 Größe: {size_mb:.2f} MB ({size} Bytes)")
        
        # Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tabellen ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  • {table_name}: {count} Einträge")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Lesen der Datenbank: {e}")

def clean_database(db_path, create_backup_first=True):
    """Bereinigt die Datenbank komplett"""
    
    if create_backup_first:
        create_backup(db_path)
    
    # Datenbank löschen
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Datenbank gelöscht: {db_path}")
    
    # Verzeichnis bereinigen
    db_dir = os.path.dirname(db_path)
    if db_dir and os.path.exists(db_dir):
        # Nur .db Dateien löschen, nicht das ganze Verzeichnis
        for file in os.listdir(db_dir):
            if file.endswith('.db') or file.endswith('.db-journal'):
                file_path = os.path.join(db_dir, file)
                os.remove(file_path)
                print(f"🗑️ Gelöscht: {file_path}")

def clean_temp_files():
    """Bereinigt temporäre Dateien"""
    
    # Python Cache
    for root, dirs, files in os.walk('.'):
        # __pycache__ Verzeichnisse
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path, ignore_errors=True)
            print(f"🧹 Gelöscht: {pycache_path}")
        
        # .pyc Dateien
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                os.remove(pyc_path)
                print(f"🧹 Gelöscht: {pyc_path}")
    
    # Log-Dateien
    for file in os.listdir('.'):
        if file.endswith('.log'):
            os.remove(file)
            print(f"🧹 Gelöscht: {file}")

def main():
    """Hauptfunktion mit Menü"""
    
    db_path = "instance/schulbuddy.db"
    
    print("🧹 SchulBuddy Datenbank-Bereinigung (Python)")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Kommandozeilen-Argument
        action = sys.argv[1]
        
        if action == "clean":
            print("🗑️ Bereinige Datenbank...")
            clean_database(db_path)
            clean_temp_files()
            print("✅ Bereinigung abgeschlossen!")
            
        elif action == "info":
            get_db_info(db_path)
            
        elif action == "backup":
            create_backup(db_path)
            
        elif action == "temp":
            print("🧹 Bereinige temporäre Dateien...")
            clean_temp_files()
            print("✅ Temporäre Dateien bereinigt!")
            
        else:
            print("❌ Unbekannte Aktion!")
            print("Verfügbare Aktionen: clean, info, backup, temp")
    else:
        # Interaktives Menü
        print("Optionen:")
        print("1. 📊 Datenbank-Info anzeigen")
        print("2. 💾 Backup erstellen")
        print("3. 🧹 Temporäre Dateien bereinigen")
        print("4. 🗑️ Datenbank komplett löschen")
        print("5. 🔄 Alles bereinigen (mit Backup)")
        
        try:
            choice = input("\nWähle eine Option (1-5): ").strip()
            
            if choice == "1":
                get_db_info(db_path)
                
            elif choice == "2":
                create_backup(db_path)
                
            elif choice == "3":
                clean_temp_files()
                
            elif choice == "4":
                confirm = input("⚠️ ACHTUNG: Alle Daten gehen verloren! Fortfahren? (j/N): ")
                if confirm.lower() in ['j', 'ja', 'y', 'yes']:
                    clean_database(db_path)
                    
            elif choice == "5":
                confirm = input("⚠️ Dies löscht die Datenbank und erstellt ein Backup. Fortfahren? (j/N): ")
                if confirm.lower() in ['j', 'ja', 'y', 'yes']:
                    clean_database(db_path, create_backup_first=True)
                    clean_temp_files()
                    print("✅ Vollständige Bereinigung abgeschlossen!")
                    
            else:
                print("❌ Ungültige Option!")
                
        except KeyboardInterrupt:
            print("\n\n👋 Abgebrochen.")

if __name__ == "__main__":
    main()
