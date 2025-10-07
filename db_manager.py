"""
Database manager for OwlReg
Provides unified interface for both SQLite and MySQL databases
"""

# Import both database modules - but handle imports separately to allow working
# with just one database if the other has issues
try:
    import sqlite_db
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    print("SQLite module not available")

try:
    # Use the standard MySQL module (not simplified)
    import mysql_db
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL module not available")

import traceback
import time

class DatabaseManager:
    """
    Manages database operations for both SQLite and MySQL
    Allows using either or both databases independently
    """
    def __init__(self, use_sqlite=True, use_mysql=True):
        """Initialize database manager with selected databases"""
        self.use_sqlite = use_sqlite and SQLITE_AVAILABLE
        self.use_mysql = use_mysql and MYSQL_AVAILABLE

        if not (self.use_sqlite or self.use_mysql):
            print("WARNING: No database is available for use!")

        # Force MySQL to be used
        if MYSQL_AVAILABLE:
            self.use_mysql = True
            print("MySQL module is available - will be used for storage")
        else:
            print("WARNING: MySQL module not available, using SQLite only")

        # Test connections at initialization
        self.test_connections()

    def create_databases(self):
        """Create tables in all configured databases"""
        results = {}

        if self.use_sqlite:
            try:
                print("Creating SQLite database and tables...")
                sqlite_result = sqlite_db.create_database()
                results['sqlite'] = sqlite_result
                print(f"SQLite database creation result: {sqlite_result}")
            except Exception as e:
                print(f"SQLite database creation error: {e}")
                traceback.print_exc()
                results['sqlite'] = False

        if self.use_mysql:
            try:
                print("Creating MySQL database and tables...")
                mysql_result = mysql_db.create_database()
                results['mysql'] = mysql_result
                print(f"MySQL database creation result: {mysql_result}")
            except Exception as e:
                print(f"MySQL database creation error: {e}")
                traceback.print_exc()
                results['mysql'] = False

        return results

    def save_registration(self, form_data):
        """
        Save registration data to configured databases
        Returns a tuple containing:
        - Success status (True if at least one database save succeeded)
        - Reference code (from first successful save)
        - Student ID (from first successful save)
        - Dictionary with detailed results from each database
        """
        results = {}
        success = False
        ref_code = None
        student_id = None

        # Save a timestamp to help with debugging
        print(f"Starting registration process at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Save to both databases, starting with SQLite
        if self.use_sqlite:
            try:
                print("Saving to SQLite database...")
                sqlite_success, sqlite_ref_code, sqlite_student_id = sqlite_db.save_registration(form_data)
                results['sqlite'] = {
                    'success': sqlite_success,
                    'reference_code': sqlite_ref_code,
                    'student_id': sqlite_student_id
                }
                print(f"SQLite save result: {sqlite_success}")

                if sqlite_success and not ref_code:
                    ref_code = sqlite_ref_code
                    student_id = sqlite_student_id
                    success = True
                    print(f"Using reference code from SQLite: {ref_code}")

                    # Update the form data with the reference code for MySQL
                    if "personal" not in form_data:
                        form_data["personal"] = {}
                    form_data["personal"]["reference_code"] = ref_code

            except Exception as e:
                print(f"SQLite registration error: {e}")
                traceback.print_exc()
                results['sqlite'] = {'success': False, 'error': str(e)}

        # Then try MySQL with the same reference code if we got one from SQLite
        if self.use_mysql:
            try:
                print("Saving to MySQL database...")
                mysql_success, mysql_ref_code, mysql_student_id = mysql_db.save_registration(form_data)
                results['mysql'] = {
                    'success': mysql_success,
                    'reference_code': mysql_ref_code,
                    'student_id': mysql_student_id
                }
                print(f"MySQL save result: {mysql_success}")

                if mysql_success and not ref_code:
                    ref_code = mysql_ref_code
                    student_id = mysql_student_id
                    success = True
                    print(f"Using reference code from MySQL: {ref_code}")

            except Exception as e:
                print(f"MySQL registration error: {e}")
                traceback.print_exc()
                results['mysql'] = {'success': False, 'error': str(e)}

        # Final check if any database save succeeded
        if success:
            print(f"Registration completed successfully with reference code: {ref_code}")
        else:
            print("Registration failed on all configured databases")

        return success, ref_code, student_id, results

    def test_connections(self):
        """Test connections to all configured databases"""
        results = {}

        if self.use_sqlite:
            try:
                print("Testing SQLite connection...")
                sqlite_result = sqlite_db.test_connection()
                results['sqlite'] = sqlite_result
                print(f"SQLite connection test result: {sqlite_result}")

                if not sqlite_result:
                    print("WARNING: SQLite database is not accessible. Storage to SQLite will not work.")
                    # Attempt to create database tables as a recovery step
                    print("Attempting to create SQLite database tables...")
                    sqlite_db.create_database()

            except Exception as e:
                print(f"SQLite connection test error: {e}")
                traceback.print_exc()
                results['sqlite'] = False

        if self.use_mysql:
            try:
                print("Testing MySQL connection...")
                # Try multiple times to establish MySQL connection
                for attempt in range(3):
                    print(f"MySQL connection attempt {attempt+1}/3")
                    mysql_result = mysql_db.test_mysql_connection()
                    results['mysql'] = mysql_result
                    print(f"MySQL connection test result: {mysql_result}")

                    if mysql_result:
                        print("MySQL connection successful!")
                        break
                    else:
                        print(f"MySQL connection attempt {attempt+1} failed")
                        if attempt < 2:
                            print("Waiting 2 seconds before retrying...")
                            time.sleep(2)

                # Additional attempt to create database if connection test failed
                if not mysql_result:
                    print("WARNING: MySQL database is not accessible. Attempting to create/repair...")
                    # Force database creation as a recovery step
                    mysql_result = mysql_db.create_database()
                    results['mysql'] = mysql_result

                # If still not successful after attempts, warn user
                if not results.get('mysql', False):
                    print("\n⚠️ WARNING: MySQL database connection failed after multiple attempts.")
                    print("Data will only be saved to SQLite database.")
                    print("Make sure XAMPP MySQL service is running if you want MySQL storage.")

            except Exception as e:
                print(f"MySQL connection test error: {e}")
                traceback.print_exc()
                results['mysql'] = False

        return results

# Create default instance for module-level access
db_manager = DatabaseManager(use_sqlite=True, use_mysql=True)

# Functions for direct use
def create_databases():
    """Create tables in all configured databases"""
    return db_manager.create_databases()

def save_registration(form_data):
    """Save registration data to configured databases"""
    return db_manager.save_registration(form_data)

def test_connections():
    """Test connections to all configured databases"""
    return db_manager.test_connections()
