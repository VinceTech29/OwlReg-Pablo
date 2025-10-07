import sqlite3
import os
from datetime import datetime
from password_utils import hash_password  # Import the password hashing function

# Get database path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")

def create_admin_account():
    """Create the default admin account if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT * FROM staff WHERE username = 'admin' AND is_admin = 1")
    admin = cursor.fetchone()

    if not admin:
        print("Creating default admin account...")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Hash the password before storing it
        hashed_password = hash_password("123")

        # Create default admin account with username: admin, password: 123 (hashed)
        cursor.execute("""
        INSERT INTO staff (username, password, first_name, last_name, email, position, department, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin", hashed_password, "System", "Administrator", "admin@school.edu", "Administrator", "IT", 1, current_time))

        conn.commit()
        print("Default admin account created successfully with secure password hashing.")
    else:
        print("Admin account already exists.")

    conn.close()

if __name__ == "__main__":
    create_admin_account()
    print("Done.")
