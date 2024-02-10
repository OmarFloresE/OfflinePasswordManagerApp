import sys
import json
import argparse
import sqlite3
import bcrypt
from cryptography.fernet import Fernet
from datetime import datetime

# Establish connection
conn = sqlite3.connect('pm.db')
c = conn.cursor()

# Create tables if not exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        master_password TEXT NOT NULL,
        master_salt TEXT NOT NULL
    )
''')

# Updated passwords table schema
c.execute('''
    CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        encrypted_password TEXT NOT NULL,
        url TEXT,
        description TEXT,
        category TEXT,
        date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()

# Database Manager
class DatabaseManager:
    def __init__(self, db_path='pm.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.conn.close()

# Encryption Utilities
def load_or_generate_key(key_file='password_key.key'):
    try:
        with open(key_file, 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as key_file:
            key_file.write(key)
    return key

def encrypt_password(password, cipher_suite):
    return cipher_suite.encrypt(password.encode('utf-8'))

def decrypt_password(encrypted_password, cipher_suite):
    return cipher_suite.decrypt(encrypted_password).decode('utf-8')

# User Authentication
def register_user(username, master_password, cursor):
    master_salt = bcrypt.gensalt()
    hashed_master_password = bcrypt.hashpw(master_password.encode('utf-8'), master_salt)
    cursor.execute('INSERT INTO users (username, master_password, master_salt) VALUES(?,?,?)', (username, hashed_master_password, master_salt))
    user_id = cursor.lastrowid  # Get the last inserted row ID
    return {"message": "User registered successfully", "user_id": user_id}

def login_user(username, password, cursor):
    cursor.execute('SELECT id, master_salt, master_password FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    if user_data:
        user_id, master_salt, hashed_password = user_data
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return {"message": "Login successful", "user_id": user_id}
        else:
            return {"error"}
    else:
        return {"error"}
    
def delete_account(user_id, cursor):
    cursor.execute('DELETE FROM passwords WHERE user_id = ?', (user_id,))
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    return {"success": True, "message": "Account deleted successfully"}

# Password Management
def store_password(user_id, website, username, password, url, description, category, cursor, cipher_suite):
    encrypted_password = encrypt_password(password, cipher_suite)
    cursor.execute('''
        INSERT INTO passwords (user_id, website, username, encrypted_password, url, description, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, website, username, encrypted_password, url, description, category))
    return {"message": "Password stored successfully"}

def get_user_passwords(user_id, cursor, cipher_suite):
    cursor.execute('''
        SELECT id, website, username, encrypted_password, url, description, category, date_created, last_modified 
        FROM passwords WHERE user_id = ?
    ''', (user_id,))
    password_records = cursor.fetchall()
    return [
        {
            "id": record[0], 
            "website": record[1], 
            "username": record[2], 
            "password": decrypt_password(record[3], cipher_suite),
            "url": record[4],
            "description": record[5],
            "category": record[6],
            "date_created": record[7],
            "last_modified": record[8]
        } 
        for record in password_records
    ]

def modify_password(entry_id, user_id, website, username, password, url, description, category, cursor, cipher_suite):
    encrypted_password = encrypt_password(password, cipher_suite)
    cursor.execute('''
        UPDATE passwords
        SET website = ?, username = ?, encrypted_password = ?, url = ?, description = ?, category = ?, last_modified = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (website, username, encrypted_password, url, description, category, entry_id, user_id))
    return {"message": "Password modified successfully"}

def delete_password(user_id, entry_id, cursor):
    cursor.execute('DELETE FROM passwords WHERE user_id = ? AND id = ?', (user_id, entry_id))
    return {"message": "Password deleted successfully" if cursor.rowcount > 0 else "No matching record found"}

# Main Function
def main(args):
    password_key = load_or_generate_key()
    password_cipher_suite = Fernet(password_key)

    with DatabaseManager() as db_manager:
        if args.auth_type == "login":
            result = login_user(args.username, args.password, db_manager.cursor)
        elif args.auth_type == "signup":
            result = register_user(args.username, args.password, db_manager.cursor)
        elif args.auth_type == "store":
            result = store_password(args.user_id, args.website, args.username, args.password, args.url, args.description, args.category, db_manager.cursor, password_cipher_suite)
        elif args.auth_type == "modify":
            result = modify_password(args.entry_id, args.user_id, args.website, args.username, args.password, args.url, args.description, args.category, db_manager.cursor, password_cipher_suite)
        elif args.auth_type == "view":
            result = get_user_passwords(args.user_id, db_manager.cursor, password_cipher_suite)
        elif args.auth_type == "delete":
            result = delete_password(args.user_id, args.entry_id, db_manager.cursor)
        elif args.auth_type == "deleteAccount":
            result = delete_account(args.user_id, db_manager.cursor)
        else:
            result = {"error": "Invalid request type"}

        print(json.dumps(result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--auth_type", required=True, choices=["login", "signup", "store", "view", "delete", "modify", "deleteAccount"])
    parser.add_argument("--user_id", type=int, help="User ID for password management")
    parser.add_argument("--entry_id", help="Entry ID for storing or deleting password")
    parser.add_argument("--website", help="Website for storing or deleting password")

    # Add these new arguments
    parser.add_argument("--url", help="URL associated with the password entry")
    parser.add_argument("--description", help="Description for the password entry")
    parser.add_argument("--category", help="Category for the password entry")

    args = parser.parse_args()
    main(args)