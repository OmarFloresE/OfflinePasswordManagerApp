# OfflineGuardian - Password Manager

## Description
OfflineGuardian is a secure password management application designed to store, manage, and protect your sensitive information. It utilizes robust encryption and hashing techniques to ensure that your data remains secure, while providing a user-friendly interface for easy management of your passwords.

### Key Features
- **Secure Storage:** Passwords are securely encrypted using modern cryptography standards.
- **Hashed Master Password:** Master passwords are hashed for an extra layer of security.
- **Local Storage:** All data is stored locally, ensuring complete control and privacy.
- **User-Friendly Interface:** Easy-to-use interface for managing your passwords efficiently.
- **Sorting and Searching:** Quickly find your passwords with sorting and search functionalities.

### Technologies Used
- **Frontend:** HTML, CSS, JavaScript (Electron Framework)
- **Backend:** Python, SQLite3 for database management
- **Cryptography:** Utilizes Fernet symmetric encryption from the `cryptography` library in Python for password encryption.
- **Hashing:** Implements `bcrypt` for secure hashing of master passwords.
- **IPC Communication:** Uses Electron's IPC (Inter-Process Communication) for secure and efficient communication between frontend and backend.

## Encryption and Hashing
### Backend
- **Password Encryption:** Each user's password is encrypted using a symmetric key before storing in the database. The Fernet encryption scheme is used, which is built on AES in CBC mode with a 128-bit key, and uses PKCS7 padding.
- **Master Password Hashing:** User's master passwords are hashed using `bcrypt` before storing. `bcrypt` is a key derivation function which adds salt to prevent rainbow table attacks and is computationally intensive, thereby slowing down brute-force attacks.

## IPC Communication
Inter-Process Communication (IPC) is used to securely pass messages between the frontend (render process) and the backend (main process) in Electron. This method ensures that frontend JavaScript cannot directly access the backend logic or the database, thus adding a layer of security.

### How IPC is used:
- **Authentication:** Sending login and signup requests from the frontend to the backend.
- **Password Management:** Requests for storing, modifying, and deleting passwords are sent from the frontend to the backend.
- **Data Retrieval:** Frontend requests the backend for fetching the stored passwords.

## Setup and Installation
*Instructions on how to set up and install your application.*

## Usage
*Instructions on how to use the application, including any necessary setup steps.*

## Contributing
*Information on how others can contribute to the project.*

## License
*State the license under which this project is available. Common choices include MIT, GPL, or Apache.*

---

This project is developed and maintained by [Your Name or Organization].

For more information or support, please contact [Your Contact Information].
