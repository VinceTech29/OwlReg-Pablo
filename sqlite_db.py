"""
Simple SQLite database connector for OwlReg
Uses built-in sqlite3 module for SQLite database operations
Works independently from MySQL operations
"""
import sqlite3
import os
import random
import string
from datetime import datetime
import traceback

# Database file path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")

def create_database():
    """Create SQLite database and tables"""
    try:
        # Connect to SQLite database (creates file if it doesn't exist)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference_code TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            middle_name TEXT,
            extension TEXT,
            lrn TEXT,
            enrollment_type TEXT,
            strand TEXT,
            preferred_session TEXT,
            birthday TEXT,
            civil_status TEXT,
            religion TEXT,
            mobile_no TEXT,
            telephone_no TEXT,
            ethnicity TEXT,
            address TEXT,
            registration_date TEXT
        )
        ''')

        # Create staff table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            position TEXT,
            department TEXT,
            is_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            last_login TEXT
        )
        ''')

        # Create family_background table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS family_background (
            family_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            father_name TEXT,
            father_age INTEGER,
            father_ethnicity TEXT,
            father_occupation TEXT,
            father_education TEXT,
            mother_name TEXT,
            mother_age INTEGER,
            mother_ethnicity TEXT,
            mother_occupation TEXT,
            mother_education TEXT,
            guardian_name TEXT,
            guardian_age INTEGER,
            guardian_ethnicity TEXT,
            guardian_occupation TEXT,
            guardian_education TEXT,
            guardian_contact TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')

        # Create academic_profile table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS academic_profile (
            academic_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            elementary_school TEXT,
            elem_year_graduated TEXT,
            elem_honors TEXT,
            juniorhs_school TEXT,
            jhs_year_graduated TEXT,
            jhs_honors TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')

        # Create emergency_contacts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            emergency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            contact_name TEXT,
            relationship TEXT,
            address TEXT,
            contact_no TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
        ''')

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database creation error: {e}")
        return False

def generate_reference_code():
    """Generate a unique reference code"""
    # Format for Reference code
    code = "REF"
    # Add random characters
    code += ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return code

def test_connection():
    """Test SQLite connection and database accessibility"""
    conn = None
    try:
        # Test if we can connect to the database and perform a simple query
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()
        print(f"SQLite connection successful. Version: {version[0]}")

        # Check if essential tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        if not cursor.fetchone():
            print("Students table doesn't exist. Database may be empty.")
            # Try to create the database
            create_database()

        return True
    except Exception as e:
        print(f"SQLite connection test failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def save_registration(form_data):
    """Save registration data to SQLite database"""
    conn = None
    try:
        print("Attempting to save student data to SQLite...")

        # Test connection before proceeding
        if not test_connection():
            return False, "Could not connect to SQLite database", None

        # Ensure database is ready
        if not create_database():
            return False, "Could not create database", None

        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Generate reference code
        ref_code = form_data.get("personal", {}).get("reference_code")
        if not ref_code:
            ref_code = generate_reference_code()
            print(f"Generated new reference code for SQLite: {ref_code}")
        else:
            print(f"Using provided reference code: {ref_code}")

        # Get data from form
        personal = form_data.get("personal", {})
        family = form_data.get("family", {})
        academic = form_data.get("academic", {})
        emergency = form_data.get("emergency", {})

        try:
            # Start transaction
            conn.execute("BEGIN TRANSACTION")

            # Insert into students table
            query = '''
            INSERT INTO students (
                reference_code, first_name, last_name, middle_name, extension,
                lrn, enrollment_type, strand, preferred_session,
                birthday, civil_status, religion, mobile_no, telephone_no,
                ethnicity, address, registration_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            # Determine enrollment type (transferee status) based on grade level
            enrollment_type = "Transferee" if personal.get("is_transferee", False) else "Freshmen"

            # Set values with defaults
            values = (
                ref_code,
                personal.get("first_name", ""),
                personal.get("last_name", ""),
                personal.get("middle_name", ""),
                personal.get("extension", ""),
                personal.get("lrn", ""),
                enrollment_type,  # Use the determined enrollment type
                personal.get("strand", ""),
                personal.get("session", "Morning"),
                personal.get("birth_date", ""),
                personal.get("civil_status", "Single"),
                personal.get("religion", ""),
                personal.get("mobile", ""),
                personal.get("telephone", ""),
                personal.get("ethnicity", ""),
                f"{personal.get('street_address', '')}, {personal.get('barangay', '')}, {personal.get('city', '')}, {personal.get('province', '')}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            cursor.execute(query, values)
            student_id = cursor.lastrowid
            print(f"Inserted student record in SQLite with ID: {student_id}")

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
            INSERT INTO family_background (
                student_id, father_name, father_age, father_ethnicity, 
                father_occupation, father_education, mother_name, 
                mother_age, mother_ethnicity, mother_occupation, 
                mother_education, guardian_name, guardian_age, 
                guardian_ethnicity, guardian_occupation, guardian_education,
                guardian_contact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

            # Insert into academic_profile table
            query = '''
            INSERT INTO academic_profile (
                student_id, elementary_school, elem_year_graduated,
                elem_honors, juniorhs_school, jhs_year_graduated, jhs_honors
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            '''

            values = (
                student_id,
                academic.get("elementary_school", ""),
                academic.get("elementary_year", ""),
                academic.get("elementary_honors", ""),
                academic.get("juniorhs_school", ""),
                academic.get("juniorhs_year", ""),
                academic.get("juniorhs_honors", "")
            )

            cursor.execute(query, values)

            # Insert into emergency_contacts table
            query = '''
            INSERT INTO emergency_contacts (
                student_id, contact_name, relationship, address, contact_no
            ) VALUES (?, ?, ?, ?, ?)
            '''

            values = (
                student_id,
                emergency.get("contact_name", ""),
                emergency.get("relationship", ""),
                emergency.get("address", ""),
                emergency.get("contact_no", "")
            )

            cursor.execute(query, values)

            # Commit all changes
            conn.commit()
            print(f"Successfully saved student data to SQLite. Reference code: {ref_code}, Student ID: {student_id}")
            return True, ref_code, student_id

        except Exception as e:
            # Rollback if error
            conn.rollback()
            print(f"Error saving registration to SQLite: {e}")
            traceback.print_exc()
            return False, str(e), None
    except Exception as e:
        print(f"Unexpected SQLite error: {e}")
        traceback.print_exc()
        return False, str(e), None
    finally:
        # Always close the connection
        if conn:
            try:
                conn.close()
                print("SQLite connection closed")
            except Exception as e:
                print(f"Error closing SQLite connection: {e}")
