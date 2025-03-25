import sqlite3

class DatabaseManager:
    def __init__(self, db_name='osu_manager.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._initialize_database()
    
    def _initialize_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY,
            osu_path TEXT,
            last_backup_path TEXT
        )
        ''')
        self.conn.commit()
    
    def save_config(self, osu_path, last_backup_path):
        self.cursor.execute("DELETE FROM config")
        self.cursor.execute("INSERT INTO config (osu_path, last_backup_path) VALUES (?, ?)", 
                        (osu_path, last_backup_path))
        self.conn.commit()
    
    def load_config(self):
        self.cursor.execute("SELECT osu_path, last_backup_path FROM config LIMIT 1")
        return self.cursor.fetchone()
    
    def update_backup_path(self, backup_path):
        self.cursor.execute("UPDATE config SET last_backup_path = ?", (backup_path,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()