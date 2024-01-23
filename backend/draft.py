import sys
import getpass
import sqlite3
import bcrypt
from cryptography.fernet import Fernet

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

def register_user(username, master_password, cursor):
    master_salt = bcrypt.gensalt()
    hashed_master_password = bcrypt.hashpw(master_password.encode('utf-8'), master_salt)
    cursor.execute('INSERT INTO users (username, master_password, master_salt) VALUES(?,?,?)', (username, hashed_master_password, master_salt))
    return cursor.lastrowid

def create_account(cursor):
    username = input("Enter your desired username: ")
    master_password = getpass.getpass("Enter desired master password: ")
    if master_password == getpass.getpass("Enter Master Password Again: ") and master_password != "":
        print("Passwords Match.")
        user_id = register_user(username, master_password, cursor)
        print("Account Initialized.")
        return user_id
    else:
        print("Passwords do not match.")
        return None

def load_or_generate_key(key_file='password_key.key'):
    try:
        # Load the key from the file
        with open(key_file, 'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        # If the file doesn't exist, generate a new key and save it
        key = Fernet.generate_key()
        with open(key_file, 'wb') as key_file:
            key_file.write(key)
    return key

def encrypt_password(password, cipher_suite):
    return cipher_suite.encrypt(password.encode('utf-8'))

def decrypt_password(encrypted_password, cipher_suite):
    return cipher_suite.decrypt(encrypted_password).decode('utf-8')

def store_password(user_id, website, username, password, cursor, cipher_suite):
    encrypted_password = encrypt_password(password, cipher_suite)
    cursor.execute('INSERT INTO passwords (user_id, website, username, encrypted_password) VALUES(?,?,?,?)', (user_id, website, username, encrypted_password))
    print("ENTRY SAVED.")

def view_passwords(user_id, cursor, cipher_suite):
    cursor.execute('SELECT website, username, encrypted_password FROM passwords WHERE user_id = ?', (user_id,))
    password_records = cursor.fetchall()

    if not password_records:
        print("No passwords found.")
        return

    print("Stored Passwords:")
    for record in password_records:
        website, username, encrypted_password = record
        decrypted_password = decrypt_password(encrypted_password, cipher_suite)
        print(f"Website: {website}, Username: {username}, Password: {decrypted_password}")

def login_user(username, password, cursor):
    cursor.execute('SELECT id, master_salt, master_password FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        user_id, master_salt, hashed_password = user_data
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print("Login Successful")
            return user_id
        else:
            print("Invalid Password")
    else:
        print("User Not Found")

def login(cursor):
    username = input("Enter your username: \t")
    password = getpass.getpass("Enter your password: \t")
    user_id = login_user(username, password, cursor)
    return user_id

def menu(user_id, cursor, cipher_suite):
    while True:
        option = input("Enter 1 to Store Passwords. 2 to View Passwords. 0 to eject: ")
        if option == '1':
            website = input("Website: ")
            username = input("Username: ")
            password = input("Password: ")
            store_password(user_id, website, username, password, cursor, cipher_suite)
        elif option == '2':
            view_passwords(user_id, cursor, cipher_suite)
        elif option == '0':
            print("Goodbye!")
            break
        else:
            print("ERROR")

def main():
    password_key = load_or_generate_key()
    password_cipher_suite = Fernet(password_key)

    with DatabaseManager() as db_manager:
        while True:
            choice = input("Enter 1 to create an account. 2 to login, 0 to exit: ")
            if choice == '1':
                user_id = create_account(db_manager.cursor)
                if user_id:
                    menu(user_id, db_manager.cursor, password_cipher_suite)
            elif choice == '2':
                user_id = login(db_manager.cursor)
                if user_id:
                    menu(user_id, db_manager.cursor, password_cipher_suite)
            elif choice == '0':
                print("Goodbye!")
                break
            else:
                print("Invalid.")

if __name__ == "__main__":
    main()
