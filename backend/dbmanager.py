import sys
import sqlite3

conn = sqlite3.connect('pm.db')

c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        master_password TEXT NOT NULL,
        master_salt TEXT NOT NULL
    )
''')

# Create the passwords table
c.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        encrypted_password TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

class DatabaseManager:
    def __init__(self, db_path='pm.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()