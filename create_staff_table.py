import sqlite3
import os
from datetime import datetime

# Get database path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")

def initialize_staff_table():
    """Create the staff table if it doesn't exist"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if staff table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Creating staff table...")

        # Create the staff table
        cursor.execute("""
        CREATE TABLE staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            position TEXT,
            department TEXT,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            last_login TEXT
        )
        """)

        # Insert a sample staff member (non-admin)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO staff (username, password, first_name, last_name, email, position, department, is_admin, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("staff1", "password123", "John", "Doe", "john.doe@school.edu", "Teacher", "STEM", 0, current_time))

        print("Staff table created and sample staff added.")
    else:
        print("Staff table already exists.")

        # Check if the table has the right structure
        cursor.execute("PRAGMA table_info(staff)")
        columns = {column[1] for column in cursor.fetchall()}

        required_columns = {"staff_id", "username", "password", "first_name", "last_name",
                           "email", "position", "department", "is_admin", "is_active",
                           "created_at", "last_login"}

        missing_columns = required_columns - columns
        if missing_columns:
            print(f"Missing columns in staff table: {missing_columns}")

            # Add missing columns
            for column in missing_columns:
                print(f"Adding column: {column}")
                data_type = "INTEGER" if column in ["is_admin", "is_active"] else "TEXT"
                cursor.execute(f"ALTER TABLE staff ADD COLUMN {column} {data_type}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_staff_table()
    print("Done.")
