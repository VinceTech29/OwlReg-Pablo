"""
Create admin and staff accounts directly in MySQL database
For use with OwlReg system
"""
import pymysql
from password_utils import hash_password
from datetime import datetime

# MySQL configuration
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "pabloregistrationsystem"
}

def create_mysql_accounts():
    """Create default admin and staff accounts in MySQL if they don't exist"""
    try:
        # Connect to MySQL
        connection = pymysql.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("Checking if admin table exists...")
        cursor.execute("SHOW TABLES LIKE 'admin'")
        if not cursor.fetchone():
            print("Creating admin table...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                admin_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            connection.commit()

        print("Checking if staff table exists...")
        cursor.execute("SHOW TABLES LIKE 'staff'")
        if not cursor.fetchone():
            print("Creating staff table...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS staff (
                staff_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                position VARCHAR(50) DEFAULT 'Teacher',
                department VARCHAR(50) DEFAULT 'General',
                is_admin TINYINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            connection.commit()

        # Check if admin exists
        cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
        admin = cursor.fetchone()

        if not admin:
            print("Creating default admin account...")
            # Hash the password for admin (password: 123)
            hashed_password = hash_password("123")

            cursor.execute("""
            INSERT INTO admin (username, password_hash, first_name, last_name, email, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, ("admin", hashed_password, "System", "Administrator", "admin@school.edu", current_time))

            connection.commit()
            print("Admin account created successfully.")
        else:
            print("Admin account already exists.")

        # Check if staff exists
        cursor.execute("SELECT * FROM staff WHERE username = 'staff1'")
        staff = cursor.fetchone()

        if not staff:
            print("Creating default staff account...")
            # Hash the password for staff (password: password123)
            hashed_password = hash_password("password123")

            cursor.execute("""
            INSERT INTO staff (username, password_hash, first_name, last_name, email, position, department, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, ("staff1", hashed_password, "John", "Doe", "john.doe@school.edu", "Teacher", "STEM", current_time))

            connection.commit()
            print("Staff account created successfully.")
        else:
            print("Staff account already exists.")

        print("Default accounts setup complete.")
        connection.close()
        return True

    except Exception as e:
        print(f"Error creating MySQL accounts: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_mysql_accounts()
    print("Done.")
