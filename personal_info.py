# personal_info.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDateEdit, QFormLayout, QFrame, QStackedLayout, QCheckBox, QRadioButton, QGroupBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap, QFont
from image_helper import load_pixmap



class StudentGeneralInfoScreen(QWidget):
    next_clicked = pyqtSignal(dict)
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f7f7f7;")
        self.sidebar_expanded = True

        # 🔹 Common textbox style
        self.textbox_style = """
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4bb3fd;
            }
        """

        # 🔹 Dropdown style - Enhanced for better visibility and with visible borders
        self.combobox_style = """
            QComboBox {
                border: 1px solid #4bb3fd;
                border-radius: 4px;
                padding: 4px 10px;
                background-color: white;
                min-width: 100px;
            }
            QComboBox:hover {
                border: 2px solid #2356c5;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: 1px solid #4bb3fd;
                background-color: #e1ecff;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #4bb3fd;
                selection-background-color: #e1ecff;
            }
        """

        main_layout = QHBoxLayout(self)

        # ---------------- Sidebar ----------------
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(220)
        self.sidebar_widget.setStyleSheet("background-color: #f3f3f3; border-radius: 12px;")
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        # Logo
        self.logo_label = QLabel("OwlReg")
        self.logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.logo_label.setStyleSheet("color: #2356c5;")
        sidebar_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Owl image
        self.owl_img = QLabel()
        try:
            self.owl_img.setPixmap(QPixmap("owl_logo2.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                                   Qt.TransformationMode.SmoothTransformation))
        except Exception:
            pass
        self.owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.owl_img)
        sidebar_layout.addSpacing(20)

        # ---------------- Pages stack ----------------
        self.pages = QStackedLayout()
        menu_items = ["Discover", "Form", "About", "Vision Mission and...", "Library", "Subject", "Scholarship", "Feedback"]

        self.menu_items = []
        for text in menu_items:
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet("""
                QPushButton {
                    color: #222;
                    background: transparent;
                    border: none;
                    text-align: left;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    border-radius: 6px;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=len(self.menu_items): self.pages.setCurrentIndex(idx))
            sidebar_layout.addWidget(btn)
            self.menu_items.append(btn)

            placeholder = QLabel(f"{text} – Empty (Soon to open...)")
            placeholder.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pages.addWidget(placeholder)

        main_layout.addWidget(self.sidebar_widget)

        # ---------------- Main Content ----------------
        main_container = QWidget()
        main_container.setLayout(self.pages)
        main_layout.addWidget(main_container, stretch=1)

        # Replace "Form" page
        self.pages.insertWidget(1, self.build_form())
        self.pages.setCurrentIndex(1)

    def build_form(self):
        form_widget = QWidget()
        form_area = QVBoxLayout(form_widget)
        form_area.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QLabel("Student General Information Sheet")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 8px; padding: 18px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_area.addWidget(header)
        form_area.addSpacing(15)

        # ---------------- Personal Info ----------------
        personal_group = QGroupBox()
        personal_group.setStyleSheet("border: none;")
        personal_layout = QVBoxLayout(personal_group)

        personal_title = QLabel("A. Personal Information")
        personal_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        personal_title.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 4px; padding: 6px 12px;")
        personal_layout.addWidget(personal_title)
        personal_layout.addSpacing(10)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        # Row 1
        enroll_combo = QComboBox(); enroll_combo.addItems(["Select...", "Grade 11", "Grade 12"])
        strand_combo = QComboBox(); strand_combo.addItems(["Select...", "STEM", "ABM", "ICT", "GAS"])

        # Apply the combobox style to make borders visible
        enroll_combo.setStyleSheet(self.combobox_style)
        strand_combo.setStyleSheet(self.combobox_style)

        # Add student status label that will update based on grade level
        self.status_label = QLabel("Student Status: Freshmen")
        self.status_label.setObjectName("status_label")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #4bb3fd;
            padding: 5px;
            border-radius: 4px;
        """)

        # Connect grade level dropdown to update student status
        enroll_combo.setObjectName("enrolling_combo")
        enroll_combo.currentIndexChanged.connect(lambda index: self.update_student_status(index))

        form.addRow(self.row([("Enrolling as:", enroll_combo), ("Select Strand:", strand_combo)], ["enrolling_combo", "strand_combo"]))
        form.addRow(self.status_label)

        # Row 2
        lrn_edit = self.make_textbox()
        form.addRow(self.row([("Learner Reference Number (LRN):", lrn_edit)], ["lrn_edit"]))

        # Session preference radio buttons
        morning_radio = QRadioButton("Morning")
        morning_radio.setObjectName("morning_radio")
        afternoon_radio = QRadioButton("Afternoon")
        afternoon_radio.setObjectName("afternoon_radio")
        session_widget = self.rowWidget([morning_radio, afternoon_radio])
        form.addRow(self.row([("Preferred class session?", session_widget)], []))

        # Row 3 - Name
        form.addRow("Name:", self.row([
            ("Last Name:", self.make_textbox(120)),
            ("First Name:", self.make_textbox(120)),
            ("Middle Name:", self.make_textbox(120)),
            ("Extension:", self.make_textbox(80))
        ], ["last_name_edit", "first_name_edit", "middle_name_edit", "extension_edit"]))

        # Birth
        birth_date = QDateEdit()
        birth_date.setCalendarPopup(True)
        birth_date.setDisplayFormat("dd/MM/yyyy")  # Changed to numeric month display format
        birth_date.setObjectName("birth_date_calendar")
        birth_date.setDate(QDate(2000, 1, 1))  # Default date for better usability
        birth_date.setMinimumDate(QDate(1900, 1, 1))  # Set reasonable minimum date
        birth_date.setMaximumDate(QDate(2025, 9, 28))  # Set max date to current date (Sept 28, 2025)
        birth_date.setMinimumWidth(160)  # Slightly reduced width since month is now numeric
        birth_date.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                min-width: 160px;
            }
            QDateEdit:focus {
                border: 1px solid #4bb3fd;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 20px;
                border-left: 1px solid #ccc;
            }
            /* Make sure calendar widget shows month and year clearly */
            QCalendarWidget QToolButton {
                color: #333;
                font-size: 14px;
                font-weight: bold;
                background-color: #f0f5ff;
                padding: 6px;
            }
            QCalendarWidget QMenu {
                font-size: 12px;
                background-color: white;
                selection-background-color: #4bb3fd;
                selection-color: white;
            }
            QCalendarWidget QSpinBox {
                font-size: 14px;
                color: #333;
                background-color: white;
                selection-background-color: #4bb3fd;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 12px;
                color: #333;
                background-color: white;
                selection-background-color: #4bb3fd;
                selection-color: white;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #e1ecff;
                padding: 2px;
            }
        """)

        form.addRow("Birth Info:", self.row([
            ("Date of Birth:", birth_date),
            ("Birth Place:", self.make_textbox(180))
        ], ["birth_date_calendar", "birth_place_edit"]))

        # Other Info
        form.addRow("Other Info:", self.row([
            ("Gender:", self.combo(["Select Gender...", "Male", "Female", "Other"], "gender_combo")),
            ("Civil Status:", self.combo(["Select...", "Single", "Married", "Other"], "civil_status_combo")),
            ("Religion:", self.make_textbox(140, "", "religion_edit"))
        ]))

        # Contact
        form.addRow("Contact Info:", self.row([
            ("Mobile Number:", self.make_textbox(140, "", "mobile_edit")),
            ("Telephone Number:", self.make_textbox(140, "", "telephone_edit")),
            ("Ethnicity:", self.make_textbox(140, "", "ethnicity_edit"))
        ]))

        personal_layout.addLayout(form)
        form_area.addWidget(personal_group)

        # ---------------- Address ----------------
        address_group = QGroupBox()
        address_group.setStyleSheet("border: none;")
        address_layout = QVBoxLayout(address_group)

        address_title = QLabel("Home Address")
        address_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        address_title.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 4px; padding: 6px 12px;")
        address_layout.addWidget(address_title)
        address_layout.addSpacing(10)

        address_layout.addWidget(self.row([
            ("Province:", self.make_textbox(140, "", "province_edit")),
            ("City/Municipality:", self.make_textbox(140, "", "city_edit")),
            ("Barangay:", self.make_textbox(140, "", "barangay_edit"))
        ]))

        # Other address fields
        house_edit = self.make_textbox(400, "House Number/Building/Street/Subdivision:", "street_edit")
        address_layout.addWidget(house_edit)

        # PWD checkbox
        pwd_check = QCheckBox()
        pwd_check.setText("Yes")
        pwd_check.setObjectName("pwd_check")
        pwd_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4bb3fd;
                background-color: #4bb3fd;
                border-radius: 3px;
            }
        """)

        # Create a label that appears when PWD is checked
        pwd_label = QLabel("PWD ID will be required during enrollment")
        pwd_label.setObjectName("pwd_notification")
        pwd_label.setStyleSheet("color: #2356c5; font-style: italic; margin-left: 10px;")
        pwd_label.setVisible(False)

        # Connect checkbox to show/hide the notification
        pwd_check.stateChanged.connect(lambda state: pwd_label.setVisible(state == 2))

        # Create a layout for the PWD question with notification
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.row([("Are you a Person with Disability (PWD)?      ", pwd_check)]))
        pwd_layout.addWidget(pwd_label)
        address_layout.addLayout(pwd_layout)



        form_area.addWidget(address_group)

        # ---------------- Navigation ----------------
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        next_btn = QPushButton("Next")

        for btn in (back_btn, next_btn):
            btn.setFixedWidth(140)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4bb3fd;
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #379be6;
                }
            """)

        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)

        back_btn.clicked.connect(self.back_clicked.emit)
        next_btn.clicked.connect(self.on_next)

        form_area.addSpacing(20)
        form_area.addLayout(nav_layout)

        return form_widget

    def update_student_status(self, index):
        """Update the student status label based on the selected grade level"""
        enrolling_combo = self.findChild(QComboBox, "enrolling_combo")

        if enrolling_combo:
            grade_level = enrolling_combo.currentText()

            if grade_level == "Grade 12":
                self.status_label.setText("Student Status: Transferee")
                self.status_label.setStyleSheet("""
                    font-size: 14px;
                    font-weight: bold;
                    color: #d32f2f;
                    background-color: #ffebee;
                    padding: 5px;
                    border-radius: 4px;
                """)
            elif grade_level == "Grade 11":
                self.status_label.setText("Student Status: Freshmen")
                self.status_label.setStyleSheet("""
                    font-size: 14px;
                    font-weight: bold;
                    color: #4bb3fd;
                    padding: 5px;
                    border-radius: 4px;
                """)
            else:
                self.status_label.setText("Student Status: Select Grade Level")
                self.status_label.setStyleSheet("""
                    font-size: 14px;
                    font-weight: bold;
                    color: #757575;
                    padding: 5px;
                    border-radius: 4px;
                """)

    def on_next(self):
        data = self.get_data()
        # data["reference_code"] = self.generate_reference_code()  # Remove or comment this if DB not ready
        self.next_clicked.emit(data)

    # ---------------- Helpers ----------------
    def make_textbox(self, width=200, placeholder="", objectName=""):
        tb = QLineEdit()
        tb.setObjectName(objectName)
        tb.setMinimumWidth(width)
        tb.setFixedHeight(32)
        tb.setPlaceholderText(placeholder)
        tb.setStyleSheet(self.textbox_style)
        return tb

    def combo(self, items, objectName=""):
        c = QComboBox()
        c.setObjectName(objectName)
        c.addItems(items)
        c.setFixedHeight(32)
        c.setStyleSheet(self.combobox_style)  # Apply custom style
        return c

    def row(self, widgets, objectNames=None):
        if objectNames is None:
            objectNames = []
        layout = QHBoxLayout()
        layout.setSpacing(12)
        for i, (label_text, widget) in enumerate(widgets):
            lbl = QLabel(label_text)
            lbl.setFixedWidth(120)
            layout.addWidget(lbl)
            if i < len(objectNames):
                widget.setObjectName(objectNames[i])
            layout.addWidget(widget)
        row_widget = QWidget()
        row_widget.setLayout(layout)
        return row_widget

    def rowWidget(self, widgets):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        for w in widgets:
            layout.addWidget(w)
        container = QWidget()
        container.setLayout(layout)
        return container

    def get_data(self):
        form_data = {}

        # Get enrolling info
        enrolling_combo = self.findChild(QComboBox, "enrolling_combo")
        strand_combo = self.findChild(QComboBox, "strand_combo")
        form_data["enrolling_as"] = enrolling_combo.currentText() if enrolling_combo else ""
        form_data["strand"] = strand_combo.currentText() if strand_combo else ""

        # Set transferee status based on grade level (Grade 12 = Transferee)
        is_transferee = (enrolling_combo and enrolling_combo.currentText() == "Grade 12")
        form_data["is_transferee"] = is_transferee
        form_data["student_status"] = "Transferee" if is_transferee else "Freshmen"

        # Get LRN
        lrn_edit = self.findChild(QLineEdit, "lrn_edit")
        form_data["lrn"] = lrn_edit.text() if lrn_edit else ""

        # Get session preference
        morning_radio = self.findChild(QRadioButton, "morning_radio")
        afternoon_radio = self.findChild(QRadioButton, "afternoon_radio")
        if morning_radio and morning_radio.isChecked():
            form_data["session"] = "Morning"
        elif afternoon_radio and afternoon_radio.isChecked():
            form_data["session"] = "Afternoon"
        else:
            form_data["session"] = ""

        # Get name fields
        name_fields = {
            "last_name": "",
            "first_name": "",
            "middle_name": "",
            "extension": ""
        }
        for field in name_fields:
            edit = self.findChild(QLineEdit, f"{field}_edit")
            if edit:
                name_fields[field] = edit.text()
        form_data.update(name_fields)

        # Get birth info
        birth_date_calendar = self.findChild(QDateEdit, "birth_date_calendar")
        birth_place = self.findChild(QLineEdit, "birth_place_edit")

        # Format birth date as YYYY-MM-DD for database
        if birth_date_calendar:
            selected_date = birth_date_calendar.date()
            form_data["birth_date"] = selected_date.toString("yyyy-MM-dd")
        else:
            form_data["birth_date"] = ""

        form_data["birth_place"] = birth_place.text() if birth_place else ""

        # Get other info
        gender_combo = self.findChild(QComboBox, "gender_combo")
        civil_status_combo = self.findChild(QComboBox, "civil_status_combo")
        religion_edit = self.findChild(QLineEdit, "religion_edit")
        form_data["gender"] = gender_combo.currentText() if gender_combo else ""
        form_data["civil_status"] = civil_status_combo.currentText() if civil_status_combo else ""
        form_data["religion"] = religion_edit.text() if religion_edit else ""

        # Get contact info
        mobile_edit = self.findChild(QLineEdit, "mobile_edit")
        telephone_edit = self.findChild(QLineEdit, "telephone_edit")
        ethnicity_edit = self.findChild(QLineEdit, "ethnicity_edit")
        form_data["mobile"] = mobile_edit.text() if mobile_edit else ""
        form_data["telephone"] = telephone_edit.text() if telephone_edit else ""
        form_data["ethnicity"] = ethnicity_edit.text() if ethnicity_edit else ""

        # Get address info
        province_edit = self.findChild(QLineEdit, "province_edit")
        city_edit = self.findChild(QLineEdit, "city_edit")
        barangay_edit = self.findChild(QLineEdit, "barangay_edit")
        street_edit = self.findChild(QLineEdit, "street_edit")
        form_data["province"] = province_edit.text() if province_edit else ""
        form_data["city"] = city_edit.text() if city_edit else ""
        form_data["barangay"] = barangay_edit.text() if barangay_edit else ""
        form_data["street_address"] = street_edit.text() if street_edit else ""

        # Get PWD status
        pwd_check = self.findChild(QCheckBox, "pwd_check")
        form_data["is_pwd"] = pwd_check.isChecked() if pwd_check else False

        return form_data

    # ---------------- Sidebar Toggle ----------------
    def toggle_sidebar(self):
        if self.sidebar_expanded:
            self.sidebar_widget.setFixedWidth(60)
            self.logo_label.hide()
            self.owl_img.hide()
            for btn in self.menu_items:
                btn.setStyleSheet("""
                    QPushButton {
                        color: #222;
                        background: transparent;
                        border: none;
                        padding: 6px;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                        border-radius: 6px;
                    }
                """)
                btn.setText(btn.text()[0])
        else:
            self.sidebar_widget.setFixedWidth(220)
            self.logo_label.show()
            self.owl_img.show()
            for i, btn in enumerate(self.menu_items):
                btn.setStyleSheet("""
                    QPushButton {
                        color: #222;
                        background: transparent;
                        border: none;
                        text-align: left;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #e6e6e6;
                        border-radius: 6px;
                    }
                """)
                btn.setText(
                    ["Discover", "Form", "About", "Vision Mission and...", "Library", "Subject", "Scholarship", "Feedback"][i]
                )

        self.sidebar_expanded = not self.sidebar_expanded

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # ---------------- Sidebar ----------------
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(220)
        self.sidebar_widget.setStyleSheet("background-color: #f3f3f3; border-radius: 12px;")
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Toggle button
        toggle_btn = QPushButton("≡")
        toggle_btn.setFont(QFont("Arial", 16))
        toggle_btn.setFixedSize(40, 40)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #2356c5;
                color: white;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1a408f;
            }
        """)
        toggle_btn.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(toggle_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # Logo
        self.logo_label = QLabel("OwlReg")
        self.logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.logo_label.setStyleSheet("color: #2356c5;")
        sidebar_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Owl image
        self.owl_img = QLabel()
        owl_pixmap = load_pixmap("owl_logo2.png")
        self.owl_img.setPixmap(owl_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation))
        self.owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.owl_img)
        sidebar_layout.addSpacing(20)

        # ---------------- Pages stack ----------------
        self.pages = QStackedLayout()
        menu_items = ["Discover", "Form", "About", "Vision Mission and...", "Library", "Subject", "Scholarship", "Feedback"]

        self.menu_items = []
        for text in menu_items:
            btn = QPushButton(text)
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet("""
                QPushButton {
                    color: #222;
                    background: transparent;
                    border: none;
                    text-align: left;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    border-radius: 6px;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=len(self.menu_items): self.pages.setCurrentIndex(idx))
            sidebar_layout.addWidget(btn)
            self.menu_items.append(btn)

            placeholder = QLabel(f"{text} – Empty (Soon to open...)")
            placeholder.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pages.addWidget(placeholder)

        main_layout.addWidget(self.sidebar_widget)

        # ---------------- Main Content ----------------
        main_container = QWidget()
        main_container.setLayout(self.pages)
        main_layout.addWidget(main_container, stretch=1)

        # Replace "Form" page
        self.pages.insertWidget(1, self.build_form())
        self.pages.setCurrentIndex(1)
