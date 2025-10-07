from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QStackedLayout, QDialog,
    QFormLayout, QComboBox, QMessageBox, QTabWidget, QSplitter
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from OwlReg.image_helper import load_pixmap  # Fixed import path
import sqlite3
import os
import threading

# For the chart
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Get database path
DB_FILE = os.path.join(os.path.dirname(__file__), "student_records.db")

# Import MySQL synchronization if available
try:
    from db_sync import sync_staff_to_mysql, test_mysql_connection
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("MySQL synchronization not available for staff management")

class StaffDialog(QDialog):
    """Dialog for adding or editing staff members"""
    def __init__(self, parent=None, staff_id=None):
        super().__init__(parent)
        self.staff_id = staff_id
        self.setWindowTitle("Add Staff Member" if not staff_id else "Edit Staff Member")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        # Create form fields
        self.username_field = QLineEdit()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.first_name_field = QLineEdit()
        self.last_name_field = QLineEdit()
        self.email_field = QLineEdit()
        self.position_field = QComboBox()
        self.position_field.addItems(["Teacher", "Counselor", "Registrar", "IT Staff", "Other"])
        self.department_field = QComboBox()
        self.department_field.addItems(["STEM", "ICT", "ABM", "GAS", "Administration", "IT"])
        self.is_admin_field = QComboBox()
        self.is_admin_field.addItems(["No", "Yes"])

        # Add fields to form
        form.addRow("Username:", self.username_field)
        form.addRow("Password:", self.password_field)
        form.addRow("First Name:", self.first_name_field)
        form.addRow("Last Name:", self.last_name_field)
        form.addRow("Email:", self.email_field)
        form.addRow("Position:", self.position_field)
        form.addRow("Department:", self.department_field)
        form.addRow("Admin Access:", self.is_admin_field)

        layout.addLayout(form)

        # Button layout
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_staff)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # If editing, load existing data
        if staff_id:
            self.load_staff_data()

    def load_staff_data(self):
        """Load staff data from database when editing"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM staff WHERE staff_id = ?", (self.staff_id,))
            staff = cursor.fetchone()

            if staff:
                self.username_field.setText(staff[1])
                self.password_field.setText("********")  # Don't display actual password
                self.first_name_field.setText(staff[3])
                self.last_name_field.setText(staff[4])
                self.email_field.setText(staff[5])

                # Set position
                position_index = self.position_field.findText(staff[6])
                if position_index >= 0:
                    self.position_field.setCurrentIndex(position_index)

                # Set department
                dept_index = self.department_field.findText(staff[7])
                if dept_index >= 0:
                    self.department_field.setCurrentIndex(dept_index)

                # Set admin status
                self.is_admin_field.setCurrentIndex(1 if staff[8] else 0)

            conn.close()
        except Exception as e:
            print(f"Error loading staff data: {e}")

    def save_staff(self):
        """Save staff data to database"""
        # Get values from fields
        username = self.username_field.text().strip()
        password = self.password_field.text()
        first_name = self.first_name_field.text().strip()
        last_name = self.last_name_field.text().strip()
        email = self.email_field.text().strip()
        position = self.position_field.currentText()
        department = self.department_field.currentText()
        is_admin = 1 if self.is_admin_field.currentText() == "Yes" else 0

        # Validate fields
        if not username or not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "Username, first name, and last name are required.")
            return

        if not self.staff_id and not password:
            QMessageBox.warning(self, "Validation Error", "Password is required for new staff members.")
            return

        try:
            # Import the password hashing function
            from password_utils import hash_password

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            # Check if username exists (for new staff)
            if not self.staff_id:
                cursor.execute("SELECT COUNT(*) FROM staff WHERE username = ?", (username,))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Validation Error", f"Username '{username}' already exists.")
                    conn.close()
                    return

            # Variable to store staff ID for MySQL sync
            staff_id = None

            # Insert or update staff
            if self.staff_id:
                staff_id = self.staff_id  # Use existing ID
                # Update existing staff
                if password == "********":
                    # Password unchanged
                    cursor.execute("""
                        UPDATE staff SET
                        username = ?, first_name = ?, last_name = ?,
                        email = ?, position = ?, department = ?, is_admin = ?
                        WHERE staff_id = ?
                    """, (username, first_name, last_name, email, position,
                         department, is_admin, self.staff_id))
                else:
                    # Password changed - hash the new password
                    hashed_password = hash_password(password)
                    cursor.execute("""
                        UPDATE staff SET
                        username = ?, password = ?, first_name = ?, last_name = ?,
                        email = ?, position = ?, department = ?, is_admin = ?
                        WHERE staff_id = ?
                    """, (username, hashed_password, first_name, last_name, email, position,
                         department, is_admin, self.staff_id))
            else:
                # Insert new staff - hash the password
                hashed_password = hash_password(password)
                from datetime import datetime
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("""
                    INSERT INTO staff (username, password, first_name, last_name, 
                    email, position, department, is_admin, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, hashed_password, first_name, last_name, email, position,
                     department, is_admin, created_at))

                staff_id = cursor.lastrowid  # Get the new ID

            # Commit changes
            conn.commit()
            conn.close()

            # Sync to MySQL in background thread if available
            if MYSQL_AVAILABLE and staff_id:
                sync_thread = threading.Thread(
                    target=self.sync_staff_to_mysql_background,
                    args=(staff_id,)
                )
                sync_thread.daemon = True
                sync_thread.start()

            self.accept()  # Close dialog with success

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save staff: {e}")
            print(f"Error saving staff: {e}")

    def sync_staff_to_mysql_background(self, staff_id):
        """Sync staff data to MySQL in background thread"""
        try:
            if MYSQL_AVAILABLE:
                # Check MySQL connection first
                if test_mysql_connection():
                    # Sync the staff data
                    sync_staff_to_mysql(staff_id)
                else:
                    print("MySQL not available for sync")
        except Exception as e:
            print(f"Background staff sync error: {e}")

class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OwlReg Admin Dashboard")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("background-color: white; font-family: Arial;")

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
        title = QLabel("OwlReg.Admin")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"background-color: {sidebar_bg_color}; color: black; padding: 5px; border-radius: 5px;")
        sidebar.addWidget(title)
        sidebar.addSpacing(40)

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

        self.staff_button = QPushButton("Staff Management")
        self.staff_button.setStyleSheet(button_style)
        sidebar.addWidget(self.staff_button)

        self.feedback_button = QPushButton("Feedbacks")
        self.feedback_button.setStyleSheet(button_style)
        sidebar.addWidget(self.feedback_button)

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

        # --- Staff management page ---
        self.staff_page = QWidget()
        staff_layout = QVBoxLayout(self.staff_page)

        # Staff header
        staff_header = QHBoxLayout()
        staff_title = QLabel("Staff Management")
        staff_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        staff_header.addWidget(staff_title)

        staff_header.addStretch()

        # Add staff button
        add_staff_btn = QPushButton("Add New Staff")
        add_staff_btn.setStyleSheet("""
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
        add_staff_btn.clicked.connect(self.add_staff)
        staff_header.addWidget(add_staff_btn)

        staff_layout.addLayout(staff_header)

        # Staff table
        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(7)
        self.staff_table.setHorizontalHeaderLabels([
            "ID", "Name", "Username", "Position", "Department", "Admin Access", "Actions"
        ])
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.staff_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.staff_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.staff_table.setAlternatingRowColors(True)
        staff_layout.addWidget(self.staff_table)

        # Add pages to stacked layout
        self.stack_layout.addWidget(self.dashboard_page)  # index 0
        self.stack_layout.addWidget(self.table_page)      # index 1
        self.stack_layout.addWidget(self.staff_page)      # index 2

        # ---------------- Button Connections ---------------- #
        self.dashboard_button.clicked.connect(lambda: self.show_page(0))
        self.list_button.clicked.connect(lambda: self.show_page(1))
        self.staff_button.clicked.connect(lambda: self.show_page(2))

        # Load initial data
        self.load_student_data()
        self.load_staff_data()
        self.update_dashboard_metrics()

    def show_page(self, index):
        """Show page at given index and update data if needed"""
        self.stack_layout.setCurrentIndex(index)

        # Refresh data when switching to pages
        if index == 0:  # Dashboard
            self.update_dashboard_metrics()
        elif index == 1:  # Student List
            self.load_student_data()
        elif index == 2:  # Staff Management
            self.load_staff_data()

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

        # Update column count to include Actions column
        self.student_table.setColumnCount(6)  # Added one more column for actions
        self.student_table.setHorizontalHeaderLabels([
            "Student No.", "Student Full Name", "Entry Status", "Strand", "Registration Date", "Actions"
        ])

        for student in students:
            row_position = self.student_table.rowCount()
            self.student_table.insertRow(row_position)

            # Store student_id in the first item for reference
            student_id = student[0]

            # Student ID
            student_id_item = QTableWidgetItem(f"ST-{student_id:04d}")
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

            # Actions column with Delete button
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(4, 4, 4, 4)
            action_layout.setSpacing(4)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #e53e3e;
                }
            """)
            delete_btn.clicked.connect(lambda _, s_id=student_id: self.delete_student(s_id))

            action_layout.addWidget(delete_btn)

            action_widget = QWidget()
            action_widget.setLayout(action_layout)

            self.student_table.setCellWidget(row_position, 5, action_widget)

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

    def load_staff_data(self):
        """Load staff data from database"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT staff_id, first_name, last_name, username, 
                       position, department, is_admin
                FROM staff
                ORDER BY last_name, first_name
            """)

            staff_members = cursor.fetchall()
            conn.close()

            # Populate staff table
            self.staff_table.setRowCount(len(staff_members))

            for row, staff in enumerate(staff_members):
                # ID
                id_item = QTableWidgetItem(str(staff[0]))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.staff_table.setItem(row, 0, id_item)

                # Name
                name_item = QTableWidgetItem(f"{staff[1]} {staff[2]}")
                self.staff_table.setItem(row, 1, name_item)

                # Username
                username_item = QTableWidgetItem(staff[3])
                self.staff_table.setItem(row, 2, username_item)

                # Position
                position_item = QTableWidgetItem(staff[4])
                self.staff_table.setItem(row, 3, position_item)

                # Department
                dept_item = QTableWidgetItem(staff[5])
                self.staff_table.setItem(row, 4, dept_item)

                # Admin Access
                admin_item = QTableWidgetItem("Yes" if staff[6] else "No")
                admin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.staff_table.setItem(row, 5, admin_item)

                # Actions
                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(4, 4, 4, 4)
                action_layout.setSpacing(4)

                edit_btn = QPushButton("Edit")
                edit_btn.setStyleSheet("background-color: #4bb3fd; color: white;")
                edit_btn.clicked.connect(lambda _, s_id=staff[0]: self.edit_staff(s_id))

                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("background-color: #ff6b6b; color: white;")
                delete_btn.clicked.connect(lambda _, s_id=staff[0]: self.delete_staff(s_id))

                action_layout.addWidget(edit_btn)
                action_layout.addWidget(delete_btn)

                action_widget = QWidget()
                action_widget.setLayout(action_layout)

                self.staff_table.setCellWidget(row, 6, action_widget)

        except Exception as e:
            print(f"Error loading staff data: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load staff data: {e}")

    def add_staff(self):
        """Open dialog to add new staff member"""
        dialog = StaffDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_staff_data()

    def edit_staff(self, staff_id):
        """Open dialog to edit staff member"""
        dialog = StaffDialog(self, staff_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_staff_data()

    def delete_staff(self, staff_id):
        """Delete staff member after confirmation"""
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this staff member?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM staff WHERE staff_id = ?", (staff_id,))
                conn.commit()
                conn.close()

                self.load_staff_data()

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete staff: {e}")

    def delete_student(self, student_id):
        """Delete student record after confirmation"""
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this student record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                # Delete from SQLite
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()

                # First get the student reference code and other related info before deleting
                cursor.execute("SELECT reference_code FROM students WHERE student_id = ?", (student_id,))
                result = cursor.fetchone()

                if not result:
                    QMessageBox.warning(self, "Warning", "Student record not found in SQLite database.")
                    return

                ref_code = result[0]

                # Delete from SQLite - cascade delete will handle related tables
                cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                conn.commit()
                conn.close()

                # Delete from MySQL if available
                try:
                    # Import here to avoid circular import
                    from mysql_db import MYSQL_CONFIG
                    import pymysql

                    # Connect to MySQL
                    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
                    mysql_cursor = mysql_conn.cursor()

                    # Get MySQL student ID using reference code
                    mysql_cursor.execute("SELECT student_id FROM students WHERE reference_code = %s", (ref_code,))
                    mysql_result = mysql_cursor.fetchone()

                    if mysql_result:
                        mysql_student_id = mysql_result[0]

                        # Delete from MySQL - foreign keys should handle cascade delete
                        mysql_cursor.execute("DELETE FROM students WHERE student_id = %s", (mysql_student_id,))
                        mysql_conn.commit()
                        print(f"Student {ref_code} deleted from MySQL database")
                    else:
                        print(f"Student {ref_code} not found in MySQL database")

                    mysql_conn.close()
                except Exception as mysql_error:
                    print(f"MySQL deletion error: {mysql_error}")
                    # Don't show error to user if MySQL fails - SQLite is primary database

                # Refresh the UI
                self.load_student_data()
                QMessageBox.information(self, "Success", "Student record has been deleted successfully")

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete student: {e}")

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

    def logout(self):
        """Handle logout action"""
        confirm = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # Create a signal that we can connect to in the main window
            # This will be picked up by the MainWindow class
            self.close()
            # The parent MainWindow will handle returning to dashboard