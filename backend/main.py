import sys
# import hashlib
import getpass
import random
import string
import sqlite3

import bcrypt
from cryptography.fernet import Fernet

# from user import User
# from encryption import hash_this

# For using a fresh DATABASE that lives on the RAM
# conn = sqlite3.connect(':memory:')


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

def register_user(username, master_password):
    conn = sqlite3.connect("pm.db")
    c = conn.cursor()
    # Generate a random salt for the master password 
    master_salt = bcrypt.gensalt()

    # Hash the master password with Salt 
    hashed_master_password = bcrypt.hashpw(master_password.encode('utf-8'), master_salt)

    # Store the user in the users table
    c.execute('INSERT INTO users (username, master_password, master_salt) VALUES(?,?,?)', (username, hashed_master_password, master_salt))

    # Get the user_id of the newly registered user
    user_id = c.lastrowid

    conn.commit()
    # conn.close()
    return user_id

def create_account():
    username = input("Enter your desired username: ")
    master_password = getpass.getpass("Enter desired master password: ")
    if master_password == getpass.getpass("Enter Master Password Again: ") and master_password != "":
        print("Passwords Match.")
        user_id = register_user(username, master_password)
    else:
        print("DOES NOT MATCH.")
        create_account()
    # DB FUNCTIONS HERE

    conn.commit()
    # conn.close()
    print("Account Initialized.")
    return user_id


# Assume you already have the user_id from the reg process.
# user_id = register_user('OmarOmar', "PasswordPassword")
# Generate a key for password encryption
password_key = Fernet.generate_key()
password_cipher_suite = Fernet(password_key)
# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_password(password):
    encrypted_password = cipher_suite.encrypt(password.encode('utf-8'))
    return encrypted_password

def decrypt_password(encrypted_password):
    decrypted_password = cipher_suite.decrypt(encrypted_password).decode('utf-8')
    return decrypted_password



def store_password(user_id, website, username, password):
    # Encrypt the password with the unique key for this user
    encrypted_password = password_cipher_suite.encrypt(password.encode('utf-8'))

    # Store the password in the passwords table 
    conn = sqlite3.connect('pm.db')
    c = conn.cursor()
    c.execute('INSERT INTO passwords (user_id, website, username, encrypted_password) VALUES(?,?,?,?)', (user_id, website, username, encrypted_password))
    print("ENTRY SAVED.")
    conn.commit()
    conn.close()

def view_passwords(user_id):
    conn = sqlite3.connect('pm.db')
    cursor = conn.cursor()
    password_key = Fernet.generate_key()
    password_cipher_suite = Fernet(password_key)
    # Retrieve encrypted passwords for the user
    cursor.execute('SELECT website, username, encrypted_password FROM passwords WHERE user_id = ?', (user_id,))
    password_records = cursor.fetchall()

    # Close the database connection
    conn.close()

    if not password_records:
        print("No passwords found.")
        return

    # Assuming you have the password cipher suite initialized
    password_cipher_suite = Fernet(password_key)

    # Display decrypted passwords
    print("Stored Passwords:")
    for record in password_records:
        website, username, encrypted_password = record
        decrypted_password = password_cipher_suite.decrypt(encrypted_password).decode('utf-8')
        print(f"Website: {website}, Username: {username}, Password: {decrypted_password}")



def login_user(username, password):
    conn = sqlite3.connect('pm.db')
    cursor = conn.cursor()

    # Retrieve the user's salt and hashed password
    cursor.execute('SELECT id, master_salt, master_password FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()

    if user_data:
        id, master_salt, hashed_password = user_data
        # Verify the entered password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            print("Login Successful")
            print(id)
            return id
        else:
            print("Invalid Password")
    else:
        print("User Not Found")

    # conn.close()

def login():
    username = input("Enter your username: \t")
    password = getpass.getpass("Enter your password: \t")

    id = login_user(username, password)
    return id

def menu(user_id):
    while True:
        option = input("Enter 1 to Store Passwords. 2 to View Passwords. 0 to eject: ")
        if option == '1':
            website = input("website: ")
            username = input("username: ")
            password = input("password: ")
            store_password(user_id, website, username, password)
        elif option == '2':
            view_passwords(user_id)
        elif option == '0':
            print("Chao Chao")
            break
        else:
            print("ERROR")
            break
def main():
    while True:
        choice = input("Enter 1 to create an account. 2 to login, 0 to exit: ")
        if choice == '1':
            user_id = create_account()
            if user_id:
                menu(user_id)
        elif choice == '2':
            user_id = login()
            if user_id:
                menu(user_id)
        elif choice == '0':
            print("Goodbye!")
            break;
        else:
            print("Invalid.")


if __name__ == "__main__":
    main()
    conn.close()