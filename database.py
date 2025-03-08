import sqlite3
import json
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = "browser.db"
        self.create_tables()
        self.migrate_from_json()

    def create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Create bookmarks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmark_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    url TEXT,
                    folder_id INTEGER,
                    FOREIGN KEY (folder_id) REFERENCES bookmark_folders (id)
                )
            ''')
            
            # Create history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    url TEXT,
                    visit_date TIMESTAMP
                )
            ''')
            
            conn.commit()

    def migrate_from_json(self):
        """Migrate existing JSON data to SQLite"""
        # Migrate settings
        if os.path.exists("browser_settings.json"):
            with open("browser_settings.json", "r") as f:
                settings = json.load(f)
                self.save_settings(settings)
            os.rename("browser_settings.json", "browser_settings.json.bak")

        # Migrate bookmarks
        if os.path.exists("browser_bookmarks.json"):
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
                # First create folders
                folder_ids = {}
                for folder in bookmarks.get("folders", []):
                    folder_id = self.add_bookmark_folder(folder["name"])
                    folder_ids[folder["name"]] = folder_id
                
                # Then add bookmarks
                for bookmark in bookmarks.get("bookmarks", []):
                    folder_name = bookmark.get("folder", "No Folder")
                    folder_id = folder_ids.get(folder_name) if folder_name != "No Folder" else None
                    self.add_bookmark(bookmark["title"], bookmark["url"], folder_id)
            os.rename("browser_bookmarks.json", "browser_bookmarks.json.bak")

        # Migrate history
        if os.path.exists("browser_history.json"):
            with open("browser_history.json", "r") as f:
                history = json.load(f)
                for entry in history:
                    self.add_history_entry(entry["title"], entry["url"], entry["date"])
            os.rename("browser_history.json", "browser_history.json.bak")

    # Settings methods
    def save_settings(self, settings):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for key, value in settings.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, json.dumps(value))
                )
            conn.commit()

    def load_settings(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {key: json.loads(value) for key, value in cursor.fetchall()}

    # Bookmark methods
    def add_bookmark_folder(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO bookmark_folders (name) VALUES (?)", (name,))
            conn.commit()
            cursor.execute("SELECT id FROM bookmark_folders WHERE name = ?", (name,))
            return cursor.fetchone()[0]

    def delete_bookmark_folder(self, folder_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmark_folders WHERE name = ?", (folder_name,))
            conn.commit()

    def add_bookmark(self, title, url, folder_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookmarks (title, url, folder_id) VALUES (?, ?, ?)",
                (title, url, folder_id)
            )
            conn.commit()

    def get_bookmarks(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.title, b.url, f.name 
                FROM bookmarks b 
                LEFT JOIN bookmark_folders f ON b.folder_id = f.id
            """)
            return [{"title": title, "url": url, "folder": folder or "No Folder"}
                   for title, url, folder in cursor.fetchall()]

    def get_folders(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM bookmark_folders")
            return [{"name": row[0]} for row in cursor.fetchall()]

    def delete_bookmark(self, title, url):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM bookmarks WHERE title = ? AND url = ?",
                (title, url)
            )
            conn.commit()

    def update_bookmark_folder(self, title, url, new_folder):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if new_folder == "No Folder":
                folder_id = None
            else:
                cursor.execute("SELECT id FROM bookmark_folders WHERE name = ?", (new_folder,))
                result = cursor.fetchone()
                folder_id = result[0] if result else None
            
            cursor.execute(
                "UPDATE bookmarks SET folder_id = ? WHERE title = ? AND url = ?",
                (folder_id, title, url)
            )
            conn.commit()

    # History methods
    def add_history_entry(self, title, url, visit_date=None):
        if visit_date is None:
            visit_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (title, url, visit_date) VALUES (?, ?, ?)",
                (title, url, visit_date)
            )
            conn.commit()

    def get_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, url, visit_date FROM history ORDER BY visit_date DESC")
            return [{"title": title, "url": url, "date": date}
                   for title, url, date in cursor.fetchall()]

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
