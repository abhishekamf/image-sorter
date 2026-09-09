import sqlite3, os, datetime, bcrypt

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), ".duplicate_photo_cleaner")
            os.makedirs(db_path, exist_ok=True)
            db_path = os.path.join(db_path, "app.db")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, action TEXT NOT NULL,
            file_path TEXT NOT NULL, hash_value TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            retention_months INTEGER DEFAULT 6,
            holding_folder TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        self.conn.commit()

    def register_user(self, username, password):
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?,?)", (username, pw_hash))
            self.conn.commit()
            uid = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO settings (user_id, retention_months) VALUES (?,6)", (uid,))
            self.conn.commit()
            return uid
        except sqlite3.IntegrityError:
            return None

    def authenticate_user(self, username, password):
        self.cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row and bcrypt.checkpw(password.encode(), row[1].encode()):
            return row[0]
        return None

    def log_action(self, user_id, action, file_path, hash_value=None):
        self.cursor.execute("INSERT INTO history (user_id, action, file_path, hash_value) VALUES (?,?,?,?)",
                          (user_id, action, file_path, hash_value))
        self.conn.commit()

    def clean_old_history(self, user_id, months):
        cutoff = datetime.datetime.now() - datetime.timedelta(days=months*30)
        self.cursor.execute("DELETE FROM history WHERE user_id=? AND timestamp<?", (user_id, cutoff))
        self.conn.commit()

    def get_history(self, user_id, limit=100):
        self.cursor.execute("SELECT action, file_path, timestamp FROM history WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
                          (user_id, limit))
        return self.cursor.fetchall()

    def get_settings(self, user_id):
        self.cursor.execute("SELECT retention_months, holding_folder FROM settings WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()

    def update_settings(self, user_id, retention_months, holding_folder):
        self.cursor.execute("UPDATE settings SET retention_months=?, holding_folder=? WHERE user_id=?",
                          (retention_months, holding_folder, user_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
