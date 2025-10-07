"""
MySQL database connector for OwlReg
Uses pymysql module for MySQL database operations
Works independently of SQLite operations
"""
import pymysql
import random
import string
import time
import traceback
import socket
from datetime import datetime

# MySQL configuration - updated to match XAMPP defaults
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",        # default MySQL user
    "password": "",        # default empty password for XAMPP
    "database": "pabloregistrationsystem",
    "connect_timeout": 10  # increased timeout
}

# MySQL configuration without database (for creating the database)
MYSQL_CONFIG_NO_DB = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "connect_timeout": 10  # increased timeout
}

def check_mysql_running():
    """Check if MySQL is accepting connections on default port"""
    print(f"Checking if MySQL is running on {MYSQL_CONFIG['host']}:3306...")

    try:
        # Try to create a socket connection to the MySQL port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((MYSQL_CONFIG['host'], 3306))
        sock.close()

        if result == 0:
            print("✓ MySQL server appears to be running and accepting connections.")
            return True
        else:
            print("❌ MySQL server is not running or not accepting connections on port 3306.")
            return False
    except Exception as e:
        print(f"Error checking MySQL: {e}")
        return False

def test_mysql_connection():
    """Test MySQL connection with retries"""
    print("Testing MySQL connection...")

    # First check if MySQL server is running
    if not check_mysql_running():
        print("MySQL server is not running. Please start your XAMPP MySQL service.")
        return False

    for attempt in range(3):  # Try 3 times
        try:
            # Use a clean config copy with explicit timeout
            temp_config = MYSQL_CONFIG.copy()
            temp_config['connect_timeout'] = 10

            print(f"Connection attempt {attempt+1}/3 to MySQL database...")
            connection = pymysql.connect(**temp_config)
            connection.ping()  # Verify connection is alive
            connection.close()
            print("✓ Successfully connected to MySQL database")
            return True
        except pymysql.err.OperationalError as e:
            error_code = e.args[0] if e.args else None

            if error_code == 1049:  # Unknown database
                print(f"Database '{MYSQL_CONFIG['database']}' does not exist. Attempting to create...")
                return create_database()
            else:
                print(f"MySQL connection error (code {error_code}): {e}")

                # Try to connect without specifying the database
                try:
                    print("Attempting to connect without database...")
                    connection = pymysql.connect(**MYSQL_CONFIG_NO_DB)
                    connection.ping()
                    connection.close()
                    print("Connected to MySQL server without database - will try to create database")
                    return create_database()
                except Exception as nested_e:
                    print(f"Failed to connect even without database: {nested_e}")

            if attempt < 2:
                time.sleep(2)  # Increased delay between attempts

        except Exception as e:
            print(f"Unexpected connection error: {e}")
            traceback.print_exc()
            if attempt < 2:
                time.sleep(2)  # Increased delay between attempts

    print("Failed to connect to MySQL after multiple attempts.")
    return False

def create_database():
    """Create MySQL database and tables"""
    try:
        print("Starting MySQL database creation/verification process...")
        # First connect to MySQL without specifying a database
        try:
            connection = pymysql.connect(**MYSQL_CONFIG_NO_DB, connect_timeout=10)
            print("✓ Connected to MySQL server")
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            return False

        cursor = connection.cursor()

        # Create database if it doesn't exist
        db_name = MYSQL_CONFIG["database"]
        print(f"Creating database {db_name} if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        print(f"✓ Database '{db_name}' created or verified")

        # Close this connection
        cursor.close()
        connection.close()

        # Now connect with the database selected
        try:
            connection = pymysql.connect(**MYSQL_CONFIG, connect_timeout=10)
            print(f"✓ Connected to database '{db_name}'")
        except Exception as e:
            print(f"Error connecting to database '{db_name}': {e}")
            return False

        cursor = connection.cursor()

        print("Creating/verifying required tables...")

        # Create students table with expanded VARCHAR sizes to avoid data truncation
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INT AUTO_INCREMENT PRIMARY KEY,
            reference_code VARCHAR(50) DEFAULT NULL UNIQUE,
            enrollment_type ENUM('Freshmen','Transferee') NOT NULL,
            strand VARCHAR(50) NOT NULL,
            lrn VARCHAR(100) NOT NULL UNIQUE,
            preferred_session ENUM('Morning','Afternoon') NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50) DEFAULT NULL,
            last_name VARCHAR(50) NOT NULL,
            extension VARCHAR(10) DEFAULT NULL,
            birthday DATE NOT NULL,
            civil_status ENUM('Single','Married','Other') DEFAULT 'Single',
            religion VARCHAR(50) DEFAULT NULL,
            mobile_no VARCHAR(20) NOT NULL,
            telephone_no VARCHAR(20) DEFAULT NULL,
            ethnicity VARCHAR(50) DEFAULT NULL,
            home_address TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create family_background table - match existing schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_background (
            family_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            father_name VARCHAR(100) DEFAULT NULL,
            father_age INT DEFAULT NULL,
            father_ethnicity VARCHAR(50) DEFAULT NULL,
            father_occupation VARCHAR(100) DEFAULT NULL,
            father_education VARCHAR(100) DEFAULT NULL,
            mother_name VARCHAR(100) DEFAULT NULL,
            mother_age INT DEFAULT NULL,
            mother_ethnicity VARCHAR(50) DEFAULT NULL,
            mother_occupation VARCHAR(100) DEFAULT NULL,
            mother_education VARCHAR(100) DEFAULT NULL,
            guardian_name VARCHAR(100) DEFAULT NULL,
            guardian_age INT DEFAULT NULL,
            guardian_ethnicity VARCHAR(50) DEFAULT NULL,
            guardian_occupation VARCHAR(100) DEFAULT NULL,
            guardian_education VARCHAR(100) DEFAULT NULL,
            guardian_contact VARCHAR(20) DEFAULT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
        ''')

        # Create academic_profile table - match existing schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS academic_profile (
            academic_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            elementary_school VARCHAR(150) DEFAULT NULL,
            elem_year_graduated YEAR DEFAULT NULL,
            elem_honors VARCHAR(100) DEFAULT NULL,
            juniorhs_school VARCHAR(150) DEFAULT NULL,
            jhs_year_graduated YEAR DEFAULT NULL,
            jhs_honors VARCHAR(100) DEFAULT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
        ''')

        # Create emergency_contacts table - match existing schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            emergency_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            contact_name VARCHAR(100) NOT NULL,
            relationship VARCHAR(50) NOT NULL,
            address TEXT NOT NULL,
            contact_no VARCHAR(20) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
        ''')

        # Create admin table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create staff table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL,
            department VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        connection.commit()
        cursor.close()
        connection.close()
        print("Database and tables created successfully!")
        return True
    except pymysql.Error as e:
        print(f"MySQL database creation error: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"General error: {e}")
        traceback.print_exc()
        return False

def generate_reference_code():
    """Generate a unique reference code that's compatible with MySQL"""
    # Create a unique identifier with timestamp and random characters
    timestamp = int(time.time())
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    code = f"R{timestamp}{random_chars}"

    # Ensure it fits in our VARCHAR field by taking a subset
    # Use the middle portion to ensure uniqueness while keeping a consistent format
    if len(code) > 10:
        code = f"R{code[5:14]}"

    return code

def save_registration(form_data):
    """Save registration data to MySQL database"""
    try:
        print("\n===== MySQL SAVE REGISTRATION - START =====")
        print("Attempting to save student data to MySQL...")
        print(f"Form data received with keys: {list(form_data.keys())}")

        try:
            # First try to check if MySQL server is running
            mysql_running = check_mysql_running()
            if not mysql_running:
                print("ERROR: MySQL server is not running. Please start your MySQL/XAMPP service.")
                return False, "MySQL server not running", None

            # Try to test database existence
            print("Testing database existence...")
            try:
                conn = pymysql.connect(
                    host=MYSQL_CONFIG["host"],
                    port=3306,
                    user=MYSQL_CONFIG["user"],
                    password=MYSQL_CONFIG["password"],
                    connect_timeout=10
                )
                cursor = conn.cursor()
                cursor.execute(f"SHOW DATABASES LIKE '{MYSQL_CONFIG['database']}'")
                result = cursor.fetchone()
                if not result:
                    print(f"ERROR: Database '{MYSQL_CONFIG['database']}' does not exist!")
                    print("Attempting to create database...")
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
                    conn.commit()
                    print(f"Database '{MYSQL_CONFIG['database']}' created successfully.")
                cursor.close()
                conn.close()
            except Exception as db_check_error:
                print(f"ERROR checking database existence: {db_check_error}")
        except Exception as conn_error:
            print(f"ERROR during connection check: {conn_error}")

        # Connect to MySQL with explicit parameters and force autocommit
        print(f"Connecting to MySQL with: host={MYSQL_CONFIG['host']}, user={MYSQL_CONFIG['user']}, db={MYSQL_CONFIG['database']}")
        connection = pymysql.connect(
            host=MYSQL_CONFIG["host"],
            port=3306,  # Explicitly set port
            user=MYSQL_CONFIG["user"],
            password=MYSQL_CONFIG["password"],
            database=MYSQL_CONFIG["database"],
            charset='utf8mb4',
            connect_timeout=30,  # Increase timeout
            autocommit=True  # Enable autocommit mode
        )
        print("✓ Connected to MySQL database")
        cursor = connection.cursor()

        # Get data from form
        personal = form_data.get("personal", {})
        family = form_data.get("family", {})
        academic = form_data.get("academic", {})
        emergency = form_data.get("emergency", {})

        # Generate reference code
        ref_code = personal.get("reference_code", "")
        if not ref_code:
            ref_code = generate_reference_code()
        print(f"Using reference code: {ref_code}")

        # Generate unique LRN with timestamp
        timestamp = int(time.time())
        lrn = personal.get("lrn", "")
        if not lrn:
            lrn = f"LRN{timestamp}"
        else:
            lrn = f"{lrn}_{timestamp}"
        print(f"Using unique LRN: {lrn}")

        try:
            # Disable autocommit for transaction
            connection.autocommit(False)

            # Start transaction explicitly
            print("Beginning MySQL transaction...")
            connection.begin()

            # Insert into students table - adjusted for the MySQL schema
            query = '''
            INSERT INTO `students` (
                `reference_code`, `first_name`, `last_name`, `middle_name`, `extension`,
                `lrn`, `enrollment_type`, `strand`, `preferred_session`,
                `birthday`, `civil_status`, `religion`, `mobile_no`, `telephone_no`,
                `ethnicity`, `home_address`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

            # Determine enrollment type (transferee status) based on grade level
            enrollment_type = "Transferee" if personal.get("is_transferee", False) else "Freshmen"

            # Format the birth date as YYYY-MM-DD for MySQL DATE type
            birth_date = personal.get("birth_date", "")
            if birth_date:
                try:
                    # Try to parse the date and format it for MySQL
                    date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
                    birth_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # If date can't be parsed, use a default
                    birth_date = "2000-01-01"
            else:
                birth_date = "2000-01-01"  # Default date if not provided

            # Format address correctly
            address = f"{personal.get('street_address', '')}, {personal.get('barangay', '')}, {personal.get('city', '')}, {personal.get('province', '')}"

            # Handle missing values for required fields
            first_name = personal.get("first_name", "")
            if not first_name:
                first_name = "Unknown"

            last_name = personal.get("last_name", "")
            if not last_name:
                last_name = "Unknown"

            # Generate a unique LRN or use the provided one
            lrn = personal.get("lrn", "")
            if not lrn:
                # Use reference code as LRN if not provided
                lrn = ref_code

            # Always add timestamp to LRN to guarantee uniqueness
            # This ensures no duplicate entry errors occur
            current_time = int(time.time())
            lrn = f"{lrn}_{current_time}"
            print(f"Using unique LRN: {lrn}")

            mobile = personal.get("mobile", "")
            if not mobile:
                mobile = "00000000000"  # Default mobile number if not provided

            strand = personal.get("strand", "")
            if not strand:
                strand = "Select..."  # Default value for strand

            session = personal.get("session", "Morning")
            if not session:
                session = "Morning"  # Default session

            # Set values with defaults
            values = (
                ref_code,
                first_name,
                last_name,
                personal.get("middle_name", ""),
                personal.get("extension", ""),
                lrn,
                enrollment_type,
                strand,
                session,
                birth_date,
                personal.get("civil_status", "Single"),
                personal.get("religion", ""),
                mobile,
                personal.get("telephone", ""),
                personal.get("ethnicity", ""),
                address
            )

            print("Executing INSERT into students table...")
            cursor.execute(query, values)
            student_id = cursor.lastrowid
            print(f"Student inserted with ID {student_id} and LRN {lrn} into MySQL")

            # Insert into family_background table
            father = family.get("father", {})
            mother = family.get("mother", {})
            guardian = family.get("guardian", {})

            # Process family names
            father_name = ""
            if not father.get("skipped", True):
                father_name = f"{father.get('first_name', '')} {father.get('last_name', '')}"

            mother_name = ""
            if not mother.get("skipped", True):
                mother_name = f"{mother.get('first_name', '')} {mother.get('last_name', '')}"

            guardian_name = ""
            if not guardian.get("skipped", True):
                guardian_name = f"{guardian.get('first_name', '')} {guardian.get('last_name', '')}"

            # Convert ages to integers when possible
            try:
                father_age = int(father.get("age", 0)) if father.get("age", "").isdigit() else 0
                mother_age = int(mother.get("age", 0)) if mother.get("age", "").isdigit() else 0
                guardian_age = int(guardian.get("age", 0)) if guardian.get("age", "").isdigit() else 0
            except:
                father_age = 0
                mother_age = 0
                guardian_age = 0

            query = '''
            INSERT INTO `family_background` (
                `student_id`, `father_name`, `father_age`, `father_ethnicity`, 
                `father_occupation`, `father_education`, `mother_name`, 
                `mother_age`, `mother_ethnicity`, `mother_occupation`, 
                `mother_education`, `guardian_name`, `guardian_age`, 
                `guardian_ethnicity`, `guardian_occupation`, `guardian_education`,
                `guardian_contact`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''

            values = (
                student_id,
                father_name,
                father_age,
                father.get("ethnicity", ""),
                father.get("occupation", ""),
                father.get("education", ""),
                mother_name,
                mother_age,
                mother.get("ethnicity", ""),
                mother.get("occupation", ""),
                mother.get("education", ""),
                guardian_name,
                guardian_age,
                guardian.get("ethnicity", ""),
                guardian.get("occupation", ""),
                guardian.get("education", ""),
                guardian.get("contact", "")
            )

            cursor.execute(query, values)

            # Format years as proper YEAR type for MySQL
            elementary_year = academic.get("elementary_year", "")
            if not elementary_year or not elementary_year.isdigit():
                elementary_year = None

            juniorhs_year = academic.get("juniorhs_year", "")
            if not juniorhs_year or not juniorhs_year.isdigit():
                juniorhs_year = None

            # Insert into academic_profile table
            query = '''
            INSERT INTO `academic_profile` (
                `student_id`, `elementary_school`, `elem_year_graduated`,
                `elem_honors`, `juniorhs_school`, `jhs_year_graduated`, `jhs_honors`
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''

            values = (
                student_id,
                academic.get("elementary_school", ""),
                elementary_year,
                academic.get("elementary_honors", ""),
                academic.get("juniorhs_school", ""),
                juniorhs_year,
                academic.get("juniorhs_honors", "")
            )

            cursor.execute(query, values)

            # Insert into emergency_contacts table
            query = '''
            INSERT INTO `emergency_contacts` (
                `student_id`, `contact_name`, `relationship`, `address`, `contact_no`
            ) VALUES (%s, %s, %s, %s, %s)
            '''

            # Handle missing required fields for emergency contacts
            relationship = emergency.get("relationship", "")
            if not relationship:
                relationship = "Not specified"

            address = emergency.get("address", "")
            if not address:
                address = "Not specified"

            contact_no = emergency.get("contact_no", "")
            if not contact_no:
                contact_no = "00000000000"

            values = (
                student_id,
                emergency.get("contact_name", "Not specified"),
                relationship,
                address,
                contact_no
            )

            cursor.execute(query, values)

            # Final commit - make DOUBLE sure this happens
            print("Committing transaction to MySQL database...")
            connection.commit()

            # Explicitly flush tables to ensure data is written to disk
            print("Flushing tables to ensure data is visible...")
            cursor.execute("FLUSH TABLES")

            print(f"✅ Successfully committed all student data to MySQL with ID {student_id}")

            return True, ref_code, student_id

        except Exception as e:
            # Rollback if error
            connection.rollback()
            print(f"Error saving registration to MySQL (rolling back): {e}")
            traceback.print_exc()
            return False, str(e), None
        finally:
            # Close connection
            cursor.close()
            connection.close()
            print("MySQL connection closed")

    except Exception as e:
        print(f"MySQL database error: {e}")
        traceback.print_exc()
        return False, str(e), None

def test_connection():
    """Test if MySQL database connection works"""
    try:
        return test_mysql_connection()
    except Exception as e:
        print(f"MySQL connection error: {e}")
        return False
