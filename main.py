from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
import sys
import traceback
from OwlReg.image_helper import load_pixmap  # Fixed import path
from datetime import datetime
from dashboard_login import DashboardLoginScreen, StaffLoginDialog, StaffDashboard, AdminLoginDialog
from student_email import StudentEmailScreen
from personal_info import StudentGeneralInfoScreen
from form2_family import FamilyForm
from form3_academic import Form3Academic
from form4_emergency import EmergencyForm
from form5_confirmation import ConfirmationForm
from success_screen import SuccessScreen
from admin_list import AdminDashboard
from reference_code_screen import ReferenceCodeScreen

# Import database manager that handles both SQLite and MySQL
import db_manager

# Import MySQL functionality for staff/admin operations
try:
    from mysql_db import test_mysql_connection
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL functionality not available for staff/admin - will use SQLite only")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OwlReg - Student Registration")
        self.setMinimumSize(1080, 768)

        # Store form data
        self.form_data = {}

        # Create the stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create instances of all form pages
        self.dashboard_page = DashboardLoginScreen()
        self.email_page = StudentEmailScreen()
        self.personal_info_page = StudentGeneralInfoScreen()
        self.family_page = FamilyForm()
        self.academic_page = Form3Academic()
        self.emergency_page = EmergencyForm()
        self.confirmation_page = ConfirmationForm()
        self.success_page = SuccessScreen()
        self.reference_screen = ReferenceCodeScreen()

        # Add all pages to the stack
        self.stack.addWidget(self.dashboard_page)      # index 0
        self.stack.addWidget(self.email_page)          # index 1
        self.stack.addWidget(self.personal_info_page)  # index 2
        self.stack.addWidget(self.family_page)         # index 3
        self.stack.addWidget(self.academic_page)       # index 4
        self.stack.addWidget(self.emergency_page)      # index 5
        self.stack.addWidget(self.confirmation_page)   # index 6
        self.stack.addWidget(self.success_page)        # index 7
        self.stack.addWidget(self.reference_screen)    # index 8

        # Admin
        self.admin_dashboard = AdminDashboard()
        self.stack.addWidget(self.admin_dashboard)     # index 9

        # ---------------- Navigation Signal Connections ---------------- #

        # Dashboard page connections
        self.dashboard_page.admin_login_clicked.connect(self.show_admin_login)
        self.dashboard_page.student_register_clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )
        self.dashboard_page.staff_login_clicked.connect(self.show_staff_login)

        # Email page connections
        self.email_page.next_clicked.connect(self.on_email_next)

        # Personal Info page connections
        self.personal_info_page.next_clicked.connect(self.on_personal_info_next)
        self.personal_info_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(1)
        )

        # Family page connections
        self.family_page.next_clicked.connect(self.on_family_next)
        self.family_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(2)
        )

        # Academic page connections
        self.academic_page.next_clicked.connect(self.on_academic_next)
        self.academic_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(3)
        )

        # Emergency page connections
        self.emergency_page.next_clicked.connect(self.on_emergency_next)
        self.emergency_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(4)
        )

        # Confirmation page connections
        self.confirmation_page.back_clicked.connect(
            lambda: self.stack.setCurrentIndex(5)
        )
        # This is the critical connection - make sure it's correct:
        self.confirmation_page.submit_clicked.connect(self.on_submit)

        # Success page connection
        self.success_page.close_clicked.connect(self.close)

        # Reference code screen connection
        self.reference_screen.close_clicked.connect(lambda: self.stack.setCurrentWidget(self.dashboard_page))

        # Check database connection in background
        QApplication.processEvents()
        self.check_database_connection()

    def check_database_connection(self):
        """Check database connection on startup"""
        results = db_manager.test_connections()

        # Check both database connections and show appropriate warnings
        if 'mysql' in results and not results['mysql']:
            QMessageBox.warning(
                self,
                "Database Connection Error",
                "Could not connect to the MySQL database.\n\n"
                "Please make sure XAMPP is running and MySQL service is started.\n\n"
                "The application will attempt to use SQLite as a fallback."
            )

        if 'sqlite' in results and not results['sqlite']:
            QMessageBox.warning(
                self,
                "Database Connection Error",
                "Could not connect to the SQLite database.\n\n"
                "Please make sure the database file exists and is accessible.\n\n"
                "The application will attempt to use MySQL as a fallback."
            )

        if (('mysql' in results and not results['mysql']) and
            ('sqlite' in results and not results['sqlite'])):
            QMessageBox.critical(
                self,
                "Critical Database Error",
                "Could not connect to any database (MySQL or SQLite).\n\n"
                "The application requires at least one working database connection to function."
            )

    # ---------------- Data Collection Methods ---------------- #

    def on_email_next(self, data):
        self.form_data["email"] = data
        self.stack.setCurrentIndex(2)

    def on_personal_info_next(self, data):
        self.form_data["personal"] = data
        self.stack.setCurrentIndex(3)

    def on_family_next(self, data):
        self.form_data["family"] = data
        self.stack.setCurrentIndex(4)

    def on_academic_next(self, data):
        self.form_data["academic"] = data
        self.stack.setCurrentIndex(5)

    def on_emergency_next(self, data):
        self.form_data["emergency"] = data
        # Pass all collected data to Confirmation page
        self.confirmation_page.update_data(self.form_data)
        self.stack.setCurrentIndex(6)

    def on_submit(self):
        """Handle submit button click and save to the database"""
        print("Processing registration submission...")

        # Disable submit button to prevent multiple submissions
        self.confirmation_page.submit_button.setEnabled(False)
        self.confirmation_page.submit_button.setText("Submitting...")
        QApplication.processEvents()  # Force UI update

        try:
            # Save data using database manager which handles both SQLite and MySQL
            success, reference_code, student_id, db_results = db_manager.save_registration(self.form_data)

            if success:
                print(f"Registration saved successfully. Reference code: {reference_code}")
                print(f"Database results: {db_results}")

                # Determine which databases were used successfully
                sqlite_success = db_results.get('sqlite', {}).get('success', False)
                mysql_success = db_results.get('mysql', {}).get('success', False)

                # Get student name for display
                personal_data = self.form_data.get("personal", {})
                student_name = f"{personal_data.get('first_name', '')} {personal_data.get('last_name', '')}"

                # Show reference code screen
                self.reference_screen.set_code(reference_code, student_name)

                # Add note about database storage based on which databases worked
                current_date = datetime.now().strftime("%B %d, %Y")
                if sqlite_success and mysql_success:
                    db_note = f"Registration completed on {current_date}.\n" \
                              f"All information has been saved to both MySQL and SQLite databases."
                elif mysql_success:
                    db_note = f"Registration completed on {current_date}.\n" \
                              f"All information has been saved to the MySQL database."
                elif sqlite_success:
                    db_note = f"Registration completed on {current_date}.\n" \
                              f"All information has been saved to the SQLite database."
                else:
                    # This shouldn't happen since success would be False
                    db_note = f"Registration completed on {current_date}.\n" \
                              f"Warning: Database storage may not be complete."

                self.reference_screen.set_db_note(db_note)

                # Show the reference screen
                self.stack.setCurrentWidget(self.reference_screen)

                # Clear form data
                self.form_data = {}

            else:
                # Show error message
                error_msg = "Registration could not be saved to any database."
                if isinstance(reference_code, str) and reference_code:
                    error_msg = f"Error: {reference_code}"

                QMessageBox.critical(
                    self,
                    "Registration Error",
                    f"{error_msg}\n\n"
                    "Please check your input and try again."
                )
                # Re-enable submit button
                self.confirmation_page.submit_button.setEnabled(True)
                self.confirmation_page.submit_button.setText("Submit")

        except Exception as e:
            print(f"Unexpected error: {e}")
            traceback.print_exc()

            QMessageBox.critical(
                self,
                "System Error",
                f"An unexpected error occurred:\n\n{str(e)}"
            )

            # Re-enable submit button
            self.confirmation_page.submit_button.setEnabled(True)
            self.confirmation_page.submit_button.setText("Submit")

    def show_staff_login(self):
        """Show the staff login dialog"""
        dialog = StaffLoginDialog(self)
        dialog.login_successful.connect(self.show_staff_dashboard)
        dialog.show()

    def show_staff_dashboard(self, staff_data):
        """Show the staff dashboard with the logged-in staff data"""
        self.staff_dashboard = StaffDashboard(staff_data)
        self.staff_dashboard.parent = self  # Set parent reference for logout navigation

        # Connect close event to return to dashboard
        self.staff_dashboard.closeEvent = lambda event: self.handle_staff_logout(event)

        self.staff_dashboard.show()

    def handle_staff_logout(self, event):
        """Handle staff dashboard logout by showing the main dashboard login again"""
        # Show the main window again
        self.show()
        # Accept the close event for the staff dashboard
        event.accept()

    def show_admin_login(self):
        """Show the admin login dialog"""
        dialog = AdminLoginDialog(self)
        dialog.login_successful.connect(self.show_admin_dashboard)
        dialog.exec()  # Use exec() instead of show() for modal dialog

    def show_admin_dashboard(self, admin_data):
        """Show the admin dashboard after successful admin authentication"""
        # The AdminDashboard class doesn't accept parameters in its constructor
        # So we'll just switch to the admin dashboard page in the stack
        self.stack.setCurrentWidget(self.admin_dashboard)

        # Connect the admin dashboard's close event to return to dashboard login
        self.admin_dashboard.closeEvent = lambda event: self.handle_admin_logout(event)

        # Display a welcome message
        QMessageBox.information(
            self,
            "Admin Login Successful",
            f"Welcome, {admin_data['first_name']} {admin_data['last_name']}!\n\n"
            f"You have logged in as Admin."
        )

    def handle_admin_logout(self, event):
        """Handle admin dashboard logout by returning to dashboard login"""
        # Return to the dashboard login page
        self.stack.setCurrentWidget(self.dashboard_page)
        # Let the close event continue for the admin dashboard
        event.accept()

    # ---------------- Window Event ---------------- #

    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()


# Main application
if __name__ == "__main__":
    try:
        print("Starting OwlReg application...")
        app = QApplication(sys.argv)
        print("QApplication initialized")

        # Check database connections (but don't block the application)
        print("Checking database connections...")
        try:
            connection_results = db_manager.test_connections()
            print(f"Database connection results: {connection_results}")

            sqlite_ok = connection_results.get('sqlite', False)
            mysql_ok = connection_results.get('mysql', False)

            print(f"SQLite connection status: {'Connected' if sqlite_ok else 'Not connected'}")
            print(f"MySQL connection status: {'Connected' if mysql_ok else 'Not connected'}")

            if not sqlite_ok and not mysql_ok:
                print("No database available - application may not function correctly")
                # Show warning to user
                QMessageBox.warning(
                    None,
                    "Database Connection Error",
                    "Could not connect to any database (SQLite or MySQL).\n\n"
                    "Please make sure the database file exists and is accessible, "
                    "and that MySQL server is running if you are using it.\n\n"
                    "The application requires at least one working database connection to function."
                )
        except Exception as e:
            print(f"Error checking databases: {e}")
            traceback.print_exc()

        # Create and show main window
        print("Creating main window...")
        window = MainWindow()
        print("Maximizing main window...")
        window.showMaximized()  # Use showMaximized instead of show to start in maximized state
        print("Main window displayed")

        # Run application
        print("Starting application event loop...")
        sys.exit(app.exec())

    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()

        QMessageBox.critical(
            None,
            "Critical Error",
            f"The application encountered a critical error:\n\n{str(e)}"
        )