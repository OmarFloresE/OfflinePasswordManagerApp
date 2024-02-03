import sys
import getpass
import sqlite3
import bcrypt
from cryptography.fernet import Fernet

print("Python Version:", sys.version)

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

def main():                                 # Main function refactored for the frontend inputs.
    password_key = load_or_generate_key()
    password_cipher_suite = Fernet(password_key)

    with DatabaseManager() as db_manager:
        print("Initiating..")
        if len(sys.argv) == 4:
            username_or_newUsername = sys.argv[1]
            password_or_newPassword = sys.argv[2]
            auth_type = sys.argv[3]
            print('Received arguments - Username:', username_or_newUsername)
            print('Received arguments - Password:', password_or_newPassword)
            print('Received arguments - Type:', auth_type)
            print("Starting main function...")

            if auth_type == "login":
                # Improve Login logic soon
                # Add these print statements in the login_user function
                print("Checking user data...")
                print("received login request by {} --- {}".format(username_or_newUsername, password_or_newPassword))
                user_id = login_user(username_or_newUsername, password_or_newPassword, db_manager.cursor)
                if user_id:
                    menu(user_id, db_manager.cursor, password_cipher_suite)
            elif auth_type == "signup":
                print("received sign up request by {} --- {}".format(username_or_newUsername, password_or_newPassword))
                user_id = register_user(username_or_newUsername, password_or_newPassword, db_manager.cursor)
                if user_id:
                    menu(user_id, db_manager.cursor, password_cipher_suite)
            else:
                print("Invalid request type ERROR")

if __name__ == "__main__":
    main()
