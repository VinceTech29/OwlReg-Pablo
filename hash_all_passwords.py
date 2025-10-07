import sqlite3
import os
import sys
from datetime import datetime
from password_utils import hash_password

# Get database path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")

def hash_all_passwords():
    """
    Convert all plain text passwords in the database to hashed passwords
    """
    try:
        print("Starting password hashing process...")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # First check if the database exists and has the staff table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='staff'")
        if not cursor.fetchone():
            print("Error: Staff table does not exist in the database.")
            conn.close()
            return False

        # Get all staff accounts with plain text passwords
        cursor.execute("SELECT staff_id, username, password FROM staff")
        staff_accounts = cursor.fetchall()

        if not staff_accounts:
            print("No staff accounts found in the database.")
            conn.close()
            return False

        print(f"Found {len(staff_accounts)} staff account(s)")

        # Count of passwords updated
        updated_count = 0

        # Update each password to hashed version
        for staff_id, username, password in staff_accounts:
            # Skip already hashed passwords (if they're in bytes format)
            if isinstance(password, bytes):
                print(f"Staff '{username}' (ID: {staff_id}) already has a hashed password. Skipping.")
                continue

            # Hash the password
            try:
                hashed_password = hash_password(password)

                # Update the database with the hashed password
                cursor.execute(
                    "UPDATE staff SET password = ? WHERE staff_id = ?",
                    (hashed_password, staff_id)
                )

                updated_count += 1
                print(f"Hashed password for staff '{username}' (ID: {staff_id})")
            except Exception as e:
                print(f"Error hashing password for staff '{username}' (ID: {staff_id}): {e}")

        # Commit changes
        conn.commit()
        conn.close()

        print(f"\nPassword hashing complete. Updated {updated_count} staff account(s).")
        print("All passwords are now securely hashed using SHA-256.")

        # Update timestamp file to record when this was done
        with open("passwords_hashed.txt", "w") as f:
            f.write(f"Passwords were hashed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Number of passwords hashed: {updated_count}\n")

        return True

    except Exception as e:
        print(f"Error during password hashing: {e}")
        return False

if __name__ == "__main__":
    print("Password Hashing Utility")
    print("-----------------------\n")

    # Confirm action
    confirm = input("This will hash all plain text passwords in the database. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)

    success = hash_all_passwords()

    if success:
        print("\nOperation completed successfully.")
    else:
        print("\nOperation completed with errors. See messages above.")
