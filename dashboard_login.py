from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QStackedLayout, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout, QGroupBox, QScrollArea, QFrame, QSizePolicy
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, pyqtSignal
from OwlReg.image_helper import load_pixmap  # Fixed import path
import sqlite3
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import traceback
from password_utils import verify_password  # Import password verification function

# Get database path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")


class DashboardLoginScreen(QWidget):
    student_register_clicked = pyqtSignal()
    teacher_register_clicked = pyqtSignal()  # This will be for staff login
    admin_login_clicked = pyqtSignal()
    staff_login_clicked = pyqtSignal()  # New signal for staff login

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2356c5;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 60, 0, 60)

        # Logo
        # Using our image helper to load the logo safely
        pixmap = load_pixmap("owl_logo.png")
        logo = QLabel()
        logo.setPixmap(
            pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(40)

        # Title
        title = QLabel("Welcome to OwlReg")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(30)

        # Buttons
        button_style = """
            QPushButton {
                background-color: white;
                color: #2356c5;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """

        register_student = QPushButton("Register for Student")
        register_student.setStyleSheet(button_style)
        register_student.clicked.connect(self.student_register_clicked.emit)
        layout.addWidget(register_student, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)

        register_staff = QPushButton("Login as Staff")
        register_staff.setStyleSheet(button_style)
        register_staff.clicked.connect(self.staff_login_clicked.emit)  # Connect to new signal
        layout.addWidget(register_staff, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)

        admin_login = QPushButton("Login as Admin")
        admin_login.setStyleSheet(button_style)
        admin_login.clicked.connect(self.admin_login_clicked.emit)
        layout.addWidget(admin_login, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class StaffLoginDialog(QDialog):
    """Dialog for staff login"""
    login_successful = pyqtSignal(dict)  # Signal to emit staff data upon successful login

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Staff Login")
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.setFixedSize(400, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        title = QLabel("Staff Login")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(20)

        # Form layout for better alignment
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Username field
        username_label = QLabel("Username:")
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter your username")
        self.username_field.setMinimumHeight(30)

        # Password field
        password_label = QLabel("Password:")
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter your password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setMinimumHeight(30)
        self.password_field.returnPressed.connect(self.attempt_login)  # Login on Enter key

        # Add fields to form
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        layout.addLayout(form_layout)

        layout.addSpacing(20)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2356c5;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #1a3f8e;
            }
        """)
        login_button.clicked.connect(self.attempt_login)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                min-height: 36px;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def attempt_login(self):
        """Attempt to log in with the provided credentials"""
        username = self.username_field.text().strip()
        password = self.password_field.text()

        if not username or not password:
            self.error_label.setText("Please enter both username and password")
            return

        try:
            # Connect to the database directly
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Print debug information to terminal
            print(f"Attempting staff login with username: {username}")

            # Check for user in staff table with exact password match (not admin)
            cursor.execute("""
                SELECT * FROM staff 
                WHERE username = ? AND is_admin = 0
            """, (username,))

            staff_data = cursor.fetchone()

            if not staff_data:
                print("No matching staff account found")
                self.error_label.setText("Invalid username or password")
                conn.close()
                return

            print(f"Found staff: {staff_data[1]}, stored password type: {type(staff_data[2])}")

            # Direct password comparison - both for plaintext and binary passwords
            stored_password = staff_data[2]
            authenticated = False

            if isinstance(stored_password, bytes):
                # For binary/hashed passwords
                try:
                    authenticated = verify_password(stored_password, password)
                    print(f"Hashed password verification result: {authenticated}")
                except Exception as verify_err:
                    print(f"Error in password verification: {verify_err}")
                    authenticated = False
            else:
                # For plain text passwords - simple string comparison
                authenticated = (stored_password == password)
                print(f"Plain text password match: {authenticated}")

            if authenticated:
                # Create a dictionary of staff data for the application
                staff_dict = {
                    "staff_id": staff_data[0],
                    "username": staff_data[1],
                    "first_name": staff_data[3],
                    "last_name": staff_data[4],
                    "email": staff_data[5],
                    "position": staff_data[6],
                    "department": staff_data[7]
                }

                print("Authentication successful, emitting login_successful signal")
                self.login_successful.emit(staff_dict)
                conn.close()
                self.accept()  # Close the dialog with accept status
            else:
                print("Authentication failed - password mismatch")
                self.error_label.setText("Invalid username or password")

            conn.close()

        except Exception as e:
            print(f"Login error: {str(e)}")
            traceback.print_exc()
            self.error_label.setText(f"Login error: {str(e)}")

        # Also print known good credentials to help troubleshoot
        print("\nValid test credentials for staff login:")
        print("Username: 'staff' or 'stafftest', Password: 'password' or 'staff123'")


class AdminLoginDialog(QDialog):
    """Dialog for admin login"""
    login_successful = pyqtSignal(dict)  # Signal to emit admin data upon successful login

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Login")
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.setFixedSize(400, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Title
        title = QLabel("Admin Login")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #b91c1c;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(20)

        # Form layout for better alignment
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        # Username field
        username_label = QLabel("Admin Username:")
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Enter admin username")
        self.username_field.setMinimumHeight(30)

        # Password field
        password_label = QLabel("Admin Password:")
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Enter admin password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setMinimumHeight(30)
        self.password_field.returnPressed.connect(self.attempt_login)  # Login on Enter key

        # Add fields to form
        form_layout.addRow(username_label, self.username_field)
        form_layout.addRow(password_label, self.password_field)
        layout.addLayout(form_layout)

        layout.addSpacing(20)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #b91c1c;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #991b1b;
            }
        """)
        login_button.clicked.connect(self.attempt_login)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 5px;
                min-height: 36px;
            }
        """)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(login_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def attempt_login(self):
        """Attempt to log in with the provided credentials"""
        username = self.username_field.text().strip()
        password = self.password_field.text()

        if not username or not password:
            self.error_label.setText("Please enter both username and password")
            return

        try:
            # Connect to the database directly
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Print debug information to terminal
            print(f"Attempting admin login with username: {username}")

            # Check for admin user in staff table
            cursor.execute("""
                SELECT * FROM staff 
                WHERE username = ? AND is_admin = 1
            """, (username,))

            admin_data = cursor.fetchone()

            if not admin_data:
                print("No matching admin account found")
                self.error_label.setText("Invalid admin credentials")
                conn.close()
                return

            print(f"Found admin: {admin_data[1]}, stored password type: {type(admin_data[2])}")

            # Direct password comparison - both for plaintext and binary passwords
            stored_password = admin_data[2]
            authenticated = False

            if isinstance(stored_password, bytes):
                # For binary/hashed passwords
                try:
                    authenticated = verify_password(stored_password, password)
                    print(f"Hashed password verification result: {authenticated}")
                except Exception as verify_err:
                    print(f"Error in password verification: {verify_err}")
                    authenticated = False
            else:
                # For plain text passwords - simple string comparison
                authenticated = (stored_password == password)
                print(f"Plain text password match: {authenticated}")

            if authenticated:
                # Create a dictionary of admin data for the application
                admin_dict = {
                    "staff_id": admin_data[0],
                    "username": admin_data[1],
                    "first_name": admin_data[3],
                    "last_name": admin_data[4],
                    "email": admin_data[5],
                    "position": admin_data[6],
                    "department": admin_data[7]
                }

                print("Admin authentication successful, emitting login_successful signal")
                self.login_successful.emit(admin_dict)
                conn.close()
                self.accept()  # Close the dialog with accept status
            else:
                print("Admin authentication failed - password mismatch")
                self.error_label.setText("Invalid admin credentials")

            conn.close()

        except Exception as e:
            print(f"Admin login error: {str(e)}")
            traceback.print_exc()
            self.error_label.setText(f"Login error: {str(e)}")

        # Also print known good credentials to help troubleshoot
        print("\nValid test credentials for admin login:")
        print("Username: 'admin' or 'admintest', Password: 'password' or 'admin123'")

class StaffDashboard(QWidget):
    """Dashboard for staff with limited access compared to admin"""
    def __init__(self, staff_data):
        super().__init__()
        self.staff_data = staff_data
        self.setWindowTitle("OwlReg Staff Dashboard")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: white; font-family: Arial;")
        self.parent = None  # Will be set by main window

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # ---------------- Sidebar ---------------- #
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(20, 20, 20, 20)
        sidebar.setSpacing(30)

        sidebar_bg_color = "#F5F5F5"  # match this color with logo/title

        # Logo with background
        logo_label = QLabel()
        pixmap = load_pixmap("owl_logo3.png")
        logo_label.setPixmap(
            pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet(f"background-color: {sidebar_bg_color}; border-radius: 40px;")
        sidebar.addWidget(logo_label)

        # Title with background
        title = QLabel("OwlReg.Staff")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"background-color: {sidebar_bg_color}; color: black; padding: 5px; border-radius: 5px;")
        sidebar.addWidget(title)
        sidebar.addSpacing(40)

        # Staff info
        staff_info = QLabel(f"Welcome, {staff_data['first_name']} {staff_data['last_name']}")
        staff_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        staff_info.setStyleSheet("color: #2356c5; font-weight: bold;")
        sidebar.addWidget(staff_info)

        staff_position = QLabel(f"{staff_data['position']} - {staff_data['department']}")
        staff_position.setAlignment(Qt.AlignmentFlag.AlignCenter)
        staff_position.setStyleSheet("color: #555; font-size: 12px;")
        sidebar.addWidget(staff_position)
        sidebar.addSpacing(20)

        # Menu buttons
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #2356c5;
                font-weight: bold;
            }
        """

        self.dashboard_button = QPushButton("Dashboard")
        self.dashboard_button.setStyleSheet(button_style)
        sidebar.addWidget(self.dashboard_button)

        self.list_button = QPushButton("Student List")
        self.list_button.setStyleSheet(button_style)
        sidebar.addWidget(self.list_button)

        # New button for Search by Reference Code
        self.search_ref_button = QPushButton("Search by Reference Code")
        self.search_ref_button.setStyleSheet(button_style)
        sidebar.addWidget(self.search_ref_button)

        sidebar.addStretch()

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 8px;
                color: #555;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        logout_button.clicked.connect(self.logout)
        sidebar.addWidget(logout_button)

        main_layout.addLayout(sidebar, 1)

        # ---------------- Stacked Main Content ---------------- #
        self.stack_layout = QStackedLayout()
        main_layout.addLayout(self.stack_layout, 4)

        # --- Dashboard page ---
        self.dashboard_page = QWidget()
        dash_layout = QVBoxLayout(self.dashboard_page)
        dash_layout.setContentsMargins(20, 20, 20, 20)
        dash_layout.setSpacing(20)

        # Dashboard title
        dash_title = QLabel("Dashboard")
        dash_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        dash_layout.addWidget(dash_title)

        # Cards row
        cards_layout = QHBoxLayout()

        # Store the value labels so we can update them
        self.metric_labels = {}

        for title_text, value_text, change_text in [
            ("Registered Students", "0", "+0%"),
            ("Freshmen Students", "0", "+0%"),
            ("Transferee Students", "0", "+0%")
        ]:
            card = QWidget()
            card.setStyleSheet("""
                background-color: #f9f9f9;
                border-radius: 10px;
            """)
            card_layout = QVBoxLayout()
            card_layout.addWidget(QLabel(title_text))
            value_label = QLabel(value_text)
            value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            card_layout.addWidget(value_label)
            change_label = QLabel(change_text)
            change_label.setStyleSheet("color: gray; font-size: 12px;")
            card_layout.addWidget(change_label)
            card.setLayout(card_layout)
            cards_layout.addWidget(card)

            # Save reference to the value label
            self.metric_labels[title_text] = value_label

        dash_layout.addLayout(cards_layout)

        # ---------------- Bar Chart ---------------- #
        chart_container = QWidget()
        chart_layout = QVBoxLayout(chart_container)

        chart_title = QLabel("Students per Strand")
        chart_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        chart_layout.addWidget(chart_title)

        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)

        dash_layout.addWidget(chart_container)

        # --- Student list page ---
        self.table_page = QWidget()
        table_layout = QVBoxLayout(self.table_page)

        # Table header
        table_header = QHBoxLayout()
        table_title = QLabel("Student List")
        table_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        table_header.addWidget(table_title)

        table_header.addStretch()

        # Add refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4bb3fd;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #2356c5;
            }
        """)
        refresh_btn.clicked.connect(self.load_student_data)
        table_header.addWidget(refresh_btn)

        table_layout.addLayout(table_header)

        # Search and filter
        search_layout = QHBoxLayout()
        search_field = QLineEdit()
        search_field.setPlaceholderText("Search students...")
        search_field.textChanged.connect(self.filter_students)
        search_layout.addWidget(search_field)

        strand_filter = QComboBox()
        strand_filter.addItems(["All Strands", "STEM", "ICT", "ABM", "GAS"])
        strand_filter.currentTextChanged.connect(self.filter_students)
        search_layout.addWidget(strand_filter)

        self.search_field = search_field
        self.strand_filter = strand_filter

        table_layout.addLayout(search_layout)

        # Student table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels([
            "Student No.", "Student Full Name", "Entry Status", "Strand", "Registration Date"
        ])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.student_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.student_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.student_table.setAlternatingRowColors(True)
        table_layout.addWidget(self.student_table)

        # Add pages to stacked layout
        self.stack_layout.addWidget(self.dashboard_page)  # index 0
        self.stack_layout.addWidget(self.table_page)      # index 1

        # --- Reference Code Search Page ---
        self.ref_search_page = QWidget()
        ref_search_layout = QVBoxLayout(self.ref_search_page)
        ref_search_layout.setContentsMargins(20, 20, 20, 20)
        ref_search_layout.setSpacing(20)

        # Page title
        search_title = QLabel("Search Student by Reference Code")
        search_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        ref_search_layout.addWidget(search_title)

        # Search form
        search_form = QHBoxLayout()
        search_form.setSpacing(10)

        ref_code_label = QLabel("Reference Code:")
        ref_code_label.setFont(QFont("Arial", 12))
        search_form.addWidget(ref_code_label)

        self.ref_code_input = QLineEdit()
        self.ref_code_input.setPlaceholderText("Enter student reference code (e.g., REF1A2B3C)")
        self.ref_code_input.setMinimumHeight(36)
        self.ref_code_input.setMaximumWidth(300)
        self.ref_code_input.returnPressed.connect(self.search_by_ref_code)  # Allow search with Enter key
        search_form.addWidget(self.ref_code_input)

        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #2356c5;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                min-height: 36px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a3f8e;
            }
        """)
        self.search_button.clicked.connect(self.search_by_ref_code)
        search_form.addWidget(self.search_button)

        search_form.addStretch()  # Push elements to the left
        ref_search_layout.addLayout(search_form)

        # Results container
        self.search_results_container = QWidget()
        self.search_results_container.setVisible(False)  # Hide initially
        self.search_results_container.setStyleSheet("""
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 10px;
        """)

        # Create a scroll area to contain all the student information
        self.search_results_scroll = QScrollArea()
        self.search_results_scroll.setWidgetResizable(True)
        self.search_results_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.search_results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.search_results_scroll.setMinimumHeight(550)  # Increased height to fill vacant space better
        self.search_results_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Allow expanding in both directions
        self.search_results_scroll.setWidget(self.search_results_container)

        search_results_layout = QVBoxLayout(self.search_results_container)
        search_results_layout.setContentsMargins(10, 10, 10, 10)
        search_results_layout.setSpacing(15)

        # Student details sections
        self.results_title = QLabel("Student Information")
        self.results_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.results_title.setStyleSheet("color: #2356c5;")
        search_results_layout.addWidget(self.results_title)

        # Personal Information Section
        personal_group = QGroupBox("Personal Information")
        personal_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4bb3fd;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2356c5;
            }
        """)
        personal_layout = QVBoxLayout(personal_group)
        self.personal_info = QLabel("No student found")
        personal_layout.addWidget(self.personal_info)
        search_results_layout.addWidget(personal_group)

        # Family Information Section
        family_group = QGroupBox("Family Information")
        family_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4bb3fd;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2356c5;
            }
        """)
        family_layout = QVBoxLayout(family_group)
        self.family_info = QLabel("No family information available")
        family_layout.addWidget(self.family_info)
        search_results_layout.addWidget(family_group)

        # Academic Information Section
        academic_group = QGroupBox("Academic Information")
        academic_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4bb3fd;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2356c5;
            }
        """)
        academic_layout = QVBoxLayout(academic_group)
        self.academic_info = QLabel("No academic information available")
        academic_layout.addWidget(self.academic_info)
        search_results_layout.addWidget(academic_group)

        # Emergency Contact Information Section
        emergency_group = QGroupBox("Emergency Contact Information")
        emergency_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #4bb3fd;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2356c5;
            }
        """)
        emergency_layout = QVBoxLayout(emergency_group)
        self.emergency_info = QLabel("No emergency contact information available")
        emergency_layout.addWidget(self.emergency_info)
        search_results_layout.addWidget(emergency_group)

        ref_search_layout.addWidget(self.search_results_scroll)
        ref_search_layout.addStretch()  # Push everything to the top

        # Add the search page to the stack
        self.stack_layout.addWidget(self.ref_search_page)  # index 2

        # ---------------- Button Connections ---------------- #
        self.dashboard_button.clicked.connect(lambda: self.show_page(0))
        self.list_button.clicked.connect(lambda: self.show_page(1))
        self.search_ref_button.clicked.connect(lambda: self.show_page(2))

        # Load initial data
        self.load_student_data()
        self.update_dashboard_metrics()

    def show_page(self, index):
        """Show page at given index and update data if needed"""
        self.stack_layout.setCurrentIndex(index)

        # Refresh data when switching to pages
        if index == 0:  # Dashboard
            self.update_dashboard_metrics()
        elif index == 1:  # Student List
            self.load_student_data()

    def load_student_data(self):
        """Load student data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Get student data with fields needed for the list
            cursor.execute("""
                SELECT student_id, first_name, middle_name, last_name, extension,
                       enrollment_type, strand, registration_date
                FROM students
                ORDER BY registration_date DESC
            """)

            students = cursor.fetchall()
            conn.close()

            # Store the full student data for filtering
            self.all_students = students

            # Display the data
            self.populate_student_table(students)

        except Exception as e:
            print(f"Error loading student data: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load student data: {e}")

    def populate_student_table(self, students):
        """Populate the student table with data"""
        self.student_table.setRowCount(0)

        for student in students:
            row_position = self.student_table.rowCount()
            self.student_table.insertRow(row_position)

            # Student ID
            student_id_item = QTableWidgetItem(f"ST-{student[0]:04d}")
            student_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row_position, 0, student_id_item)

            # Full Name
            middle_initial = f" {student[2][0]}." if student[2] else ""
            extension = f" {student[4]}" if student[4] else ""
            full_name = f"{student[1]}{middle_initial} {student[3]}{extension}"
            name_item = QTableWidgetItem(full_name)
            self.student_table.setItem(row_position, 1, name_item)

            # Entry Status
            entry_status = student[5] or "Freshmen"  # Default to Freshmen
            status_item = QTableWidgetItem(entry_status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row_position, 2, status_item)

            # Strand
            strand_item = QTableWidgetItem(student[6] or "N/A")
            strand_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row_position, 3, strand_item)

            # Registration Date
            reg_date_item = QTableWidgetItem(student[7][:10] if student[7] else "N/A")
            reg_date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row_position, 4, reg_date_item)

    def filter_students(self):
        """Filter student data based on search term and strand filter"""
        search_term = self.search_field.text().lower()
        selected_strand = self.strand_filter.currentText()

        filtered_students = []
        for student in self.all_students:
            # Get student details
            full_name = f"{student[1]} {student[2]} {student[3]}".lower()
            student_id = f"ST-{student[0]:04d}".lower()
            strand = student[6] or ""

            # Check if student matches filter criteria
            name_match = search_term in full_name or search_term in student_id
            strand_match = selected_strand == "All Strands" or selected_strand == strand

            if name_match and strand_match:
                filtered_students.append(student)

        self.populate_student_table(filtered_students)

    def update_dashboard_metrics(self):
        """Update dashboard metrics and chart with data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Get total student count
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]

            # Get freshmen count
            cursor.execute("SELECT COUNT(*) FROM students WHERE enrollment_type = 'Freshmen' OR enrollment_type IS NULL")
            freshmen_count = cursor.fetchone()[0]

            # Get transferee count
            cursor.execute("SELECT COUNT(*) FROM students WHERE enrollment_type = 'Transferee'")
            transferee_count = cursor.fetchone()[0]

            # Update metric labels
            if "Registered Students" in self.metric_labels:
                self.metric_labels["Registered Students"].setText(str(total_students))

            if "Freshmen Students" in self.metric_labels:
                self.metric_labels["Freshmen Students"].setText(str(freshmen_count))

            if "Transferee Students" in self.metric_labels:
                self.metric_labels["Transferee Students"].setText(str(transferee_count))

            # Get strand distribution for chart
            cursor.execute("""
                SELECT strand, COUNT(*) 
                FROM students 
                WHERE strand IS NOT NULL AND strand != '' 
                GROUP BY strand
            """)

            strand_data = cursor.fetchall()
            conn.close()

            # Create dictionary of strand counts
            strands = []
            counts = []

            for strand, count in strand_data:
                strands.append(strand)
                counts.append(count)

            # Add default strands with zero count if not present
            default_strands = ["STEM", "ICT", "ABM", "GAS"]
            for strand in default_strands:
                if strand not in strands:
                    strands.append(strand)
                    counts.append(0)

            # Update bar chart
            self.update_bar_chart(strands, counts)

        except Exception as e:
            print(f"Error updating dashboard metrics: {e}")

    def update_bar_chart(self, strands, counts):
        """Update the bar chart with strand data"""
        ax = self.figure.add_subplot(111)
        ax.clear()

        if strands and counts:
            ax.bar(strands, counts, color="#2356c5")
            ax.set_ylabel("Number of Students")
            ax.set_xlabel("Strands")

            # Add count labels on top of bars
            for i, count in enumerate(counts):
                if count > 0:
                    ax.text(i, count + 0.5, str(count), ha='center')
        else:
            ax.text(0.5, 0.5, "No strand data available",
                   ha='center', va='center', transform=ax.transAxes)

        self.canvas.draw()

    def search_by_ref_code(self):
        """Search for a student by reference code and display all their information"""
        ref_code = self.ref_code_input.text().strip()

        if not ref_code:
            QMessageBox.warning(self, "Input Error", "Please enter a reference code")
            return

        try:
            # Connect to SQLite database
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row  # This allows accessing columns by name
            cursor = conn.cursor()

            # First, query for the student's personal information
            cursor.execute("""
                SELECT *
                FROM students
                WHERE reference_code = ?
            """, (ref_code,))

            student = cursor.fetchone()

            if not student:
                QMessageBox.warning(self, "Not Found", f"No student found with reference code: {ref_code}")
                self.search_results_container.setVisible(False)
                return

            # Now we have the student, get the student_id to retrieve related information
            student_id = student['student_id']

            # Get family background information
            cursor.execute("""
                SELECT *
                FROM family_background
                WHERE student_id = ?
            """, (student_id,))
            family = cursor.fetchone()

            # Get academic profile information
            cursor.execute("""
                SELECT *
                FROM academic_profile
                WHERE student_id = ?
            """, (student_id,))
            academic = cursor.fetchone()

            # Get emergency contact information
            cursor.execute("""
                SELECT *
                FROM emergency_contacts
                WHERE student_id = ?
            """, (student_id,))
            emergency = cursor.fetchone()

            conn.close()

            # Now display all the information
            self.display_student_details(student, family, academic, emergency)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to search student: {e}")
            print(f"Error searching by reference code: {e}")
            traceback.print_exc()

    def display_student_details(self, student, family, academic, emergency):
        """Format and display comprehensive student information"""
        try:
            # Set the title with the student's name
            full_name = f"{student['first_name']} {student['middle_name'] or ''} {student['last_name']} {student['extension'] or ''}".strip()
            self.results_title.setText(f"Student Information: {full_name}")

            # Format and display personal information
            registration_date = datetime.strptime(student['registration_date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y") if student['registration_date'] else "N/A"

            personal_html = f"""
            <table style="width:100%">
                <tr><td><b>Reference Code:</b></td><td>{student['reference_code']}</td>
                    <td><b>Student ID:</b></td><td>ST-{student['student_id']:04d}</td></tr>
                <tr><td><b>Full Name:</b></td><td colspan="3">{full_name}</td></tr>
                <tr><td><b>LRN:</b></td><td>{student['lrn'] or 'N/A'}</td>
                    <td><b>Entry Type:</b></td><td>{student['enrollment_type'] or 'N/A'}</td></tr>
                <tr><td><b>Strand:</b></td><td>{student['strand'] or 'N/A'}</td>
                    <td><b>Session:</b></td><td>{student['preferred_session'] or 'N/A'}</td></tr>
                <tr><td><b>Birthday:</b></td><td>{student['birthday'] or 'N/A'}</td>
                    <td><b>Civil Status:</b></td><td>{student['civil_status'] or 'N/A'}</td></tr>
                <tr><td><b>Religion:</b></td><td>{student['religion'] or 'N/A'}</td>
                    <td><b>Ethnicity:</b></td><td>{student['ethnicity'] or 'N/A'}</td></tr>
                <tr><td><b>Mobile No:</b></td><td>{student['mobile_no'] or 'N/A'}</td>
                    <td><b>Telephone:</b></td><td>{student['telephone_no'] or 'N/A'}</td></tr>
                <tr><td><b>Address:</b></td><td colspan="3">{student['address'] or 'N/A'}</td></tr>
                <tr><td><b>Registration Date:</b></td><td colspan="3">{registration_date}</td></tr>
            </table>
            """
            self.personal_info.setText(personal_html)

            # Format and display family information
            if family:
                # Try to access guardian_contact safely - sqlite3.Row doesn't have .get() method
                guardian_contact = "N/A"
                try:
                    # Check if 'guardian_contact' column exists in the row
                    guardian_contact = family['guardian_contact'] or "N/A"
                except (IndexError, KeyError):
                    # Column doesn't exist, keep the default value
                    pass

                family_html = f"""
                <table style="width:100%">
                    <tr><th colspan="2" style="text-align:left">Father's Information</th>
                        <th colspan="2" style="text-align:left">Mother's Information</th></tr>
                    <tr><td><b>Name:</b></td><td>{family['father_name'] or 'N/A'}</td>
                        <td><b>Name:</b></td><td>{family['mother_name'] or 'N/A'}</td></tr>
                    <tr><td><b>Age:</b></td><td>{family['father_age'] or 'N/A'}</td>
                        <td><b>Age:</b></td><td>{family['mother_age'] or 'N/A'}</td></tr>
                    <tr><td><b>Ethnicity:</b></td><td>{family['father_ethnicity'] or 'N/A'}</td>
                        <td><b>Ethnicity:</b></td><td>{family['mother_ethnicity'] or 'N/A'}</td></tr>
                    <tr><td><b>Occupation:</b></td><td>{family['father_occupation'] or 'N/A'}</td>
                        <td><b>Occupation:</b></td><td>{family['mother_occupation'] or 'N/A'}</td></tr>
                    <tr><td><b>Education:</b></td><td>{family['father_education'] or 'N/A'}</td>
                        <td><b>Education:</b></td><td>{family['mother_education'] or 'N/A'}</td></tr>
                </table>
                <br>
                <table style="width:100%">
                    <tr><th colspan="4" style="text-align:left">Guardian's Information</th></tr>
                    <tr><td><b>Name:</b></td><td>{family['guardian_name'] or 'N/A'}</td>
                        <td><b>Age:</b></td><td>{family['guardian_age'] or 'N/A'}</td></tr>
                    <tr><td><b>Ethnicity:</b></td><td>{family['guardian_ethnicity'] or 'N/A'}</td>
                        <td><b>Contact:</b></td><td>{guardian_contact}</td></tr>
                    <tr><td><b>Occupation:</b></td><td>{family['guardian_occupation'] or 'N/A'}</td>
                        <td><b>Education:</b></td><td>{family['guardian_education'] or 'N/A'}</td></tr>
                </table>
                """
                self.family_info.setText(family_html)
            else:
                self.family_info.setText("No family information available for this student.")

            # Format and display academic information
            if academic:
                # Print debug info to diagnose the issue
                print("Academic data found:")
                for key in academic.keys():
                    print(f"  {key}: {academic[key]}")

                # Directly access the fields in a way that works with SQLite Row objects
                elementary_school = academic['elementary_school'] if academic['elementary_school'] else "N/A"
                elem_year_graduated = academic['elem_year_graduated'] if academic['elem_year_graduated'] else "N/A"
                elem_honors = academic['elem_honors'] if academic['elem_honors'] else "N/A"

                # Direct column name access for juniorhs fields - this is the crucial fix
                juniorhs_school = academic['juniorhs_school'] if academic['juniorhs_school'] else "N/A"
                jhs_year_graduated = academic['jhs_year_graduated'] if academic['jhs_year_graduated'] else "N/A"
                jhs_honors = academic['jhs_honors'] if academic['jhs_honors'] else "N/A"

                academic_html = f"""
                <table style="width:100%">
                    <tr><th colspan="2" style="text-align:left">Elementary Education</th>
                        <th colspan="2" style="text-align:left">Junior High School Education</th></tr>
                    <tr><td><b>School:</b></td><td>{elementary_school}</td>
                        <td><b>School:</b></td><td>{juniorhs_school}</td></tr>
                    <tr><td><b>Year Graduated:</b></td><td>{elem_year_graduated}</td>
                        <td><b>Year Graduated:</b></td><td>{jhs_year_graduated}</td></tr>
                    <tr><td><b>Honors:</b></td><td>{elem_honors}</td>
                        <td><b>Honors:</b></td><td>{jhs_honors}</td></tr>
                </table>
                """
                self.academic_info.setText(academic_html)
            else:
                self.academic_info.setText("No academic information available for this student.")

            # Format and display emergency contact information
            if emergency:
                # Print debug info to diagnose the issue
                print("Emergency contact data found:")
                for key in emergency.keys():
                    print(f"  {key}: {emergency[key]}")

                # Direct column access for emergency contact fields - this is the crucial fix
                contact_name = emergency['contact_name'] if emergency['contact_name'] else "N/A"
                relationship = emergency['relationship'] if emergency['relationship'] else "N/A"
                contact_no = emergency['contact_no'] if emergency['contact_no'] else "N/A"
                address = emergency['address'] if emergency['address'] else "N/A"

                emergency_html = f"""
                <table style="width:100%">
                    <tr><td><b>Contact Name:</b></td><td colspan="3">{contact_name}</td></tr>
                    <tr><td><b>Relationship:</b></td><td>{relationship}</td>
                        <td><b>Contact No:</b></td><td>{contact_no}</td></tr>
                    <tr><td><b>Address:</b></td><td colspan="3">{address}</td></tr>
                </table>
                """
                self.emergency_info.setText(emergency_html)
            else:
                self.emergency_info.setText("No emergency contact information available for this student.")

            # Make results visible
            self.search_results_container.setVisible(True)

        except Exception as e:
            print(f"Error displaying student details: {e}")
            traceback.print_exc()
            QMessageBox.warning(self, "Display Error", "An error occurred while displaying student information.")
            self.search_results_container.setVisible(False)

    def logout(self):
        """Handle staff logout"""
        reply = QMessageBox.question(self, 'Logout Confirmation',
            "Are you sure you want to logout?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Close the dashboard and reopen the login screen
            self.close()
            # If parent is set, show login screen
            if self.parent:
                self.parent.show()

    def show_login_screen(self):
        """Method to support returning to the login screen"""
        # This is used by the parent window to show the login screen after logout
        if self.parent:
            self.parent.stack.setCurrentIndex(0)  # Assuming login screen is at index 0
