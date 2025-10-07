# form2_family.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QFormLayout, QGroupBox, QScrollArea,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from image_helper import load_pixmap  # Import the image helper


class FamilyForm(QWidget):
    next_clicked = pyqtSignal(dict)  # Signal for navigation with dict parameter
    back_clicked = pyqtSignal()  # Signal for navigation

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Family Background")
        self.resize(1200, 850)
        self.setStyleSheet("background-color: #f7f7f7;")

        # common textbox style
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

        # combobox style - Enhanced for better visibility with visible borders
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
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(220)
        sidebar_widget.setStyleSheet("background-color: #f3f3f3; border-radius: 12px;")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo
        logo = QLabel("OwlReg")
        logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo.setStyleSheet("color: #2356c5; margin-top: 32px;")
        sidebar_layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        owl_img = QLabel()
        owl_img.setPixmap(QPixmap("owl_logo2.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(owl_img)
        sidebar_layout.addSpacing(20)

        # Menu items
        menu_items = ["Discover", "Form", "About", "Vision Mission and...", "Library", "Subject", "Scholarship", "Feedback"]
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
            sidebar_layout.addWidget(btn)

        main_layout.addWidget(sidebar_widget)

        # ---------------- Scrollable Form Area ----------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header = QLabel("Student General Information Sheet")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 8px; padding: 18px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(header)
        form_layout.addSpacing(15)

        # Family Background Section
        family_group = QGroupBox()
        family_group.setStyleSheet("border: none;")
        family_layout = QVBoxLayout(family_group)

        family_title = QLabel("B. Family Background")
        family_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        family_title.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 4px; padding: 6px 12px;")
        family_layout.addWidget(family_title)
        family_layout.addSpacing(10)

        # Build parent groups
        father_group = self.build_parent_group("Father's Information", allow_skip=True)
        mother_group = self.build_parent_group("Mother's Information", allow_skip=True)
        guardian_group = self.build_parent_group("Guardian's Information", allow_skip=True)
        family_layout.addWidget(father_group["widget"])
        family_layout.addWidget(mother_group["widget"])
        family_layout.addWidget(guardian_group["widget"])

        form_layout.addWidget(family_group)

        # Navigation
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

        form_layout.addSpacing(20)
        form_layout.addLayout(nav_layout)

        back_btn.clicked.connect(self.back_clicked.emit)
        next_btn.clicked.connect(lambda: self.next_clicked.emit(self.get_data()))

        scroll.setWidget(form_container)
        main_layout.addWidget(scroll, stretch=1)

    def build_parent_group(self, title, allow_skip=False):
        group = QGroupBox()
        group.setStyleSheet("QGroupBox { border: none; }")
        layout = QVBoxLayout(group)
        controls = {}

        prefix = title.split("'")[0].lower().strip()  # father, mother, or guardian

        # Custom header label
        header = QLabel(title)
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("background-color: #dbeafe; color: #111; border-radius: 4px; padding: 6px 10px;")
        layout.addWidget(header)

        skip = None
        if allow_skip:
            skip = QCheckBox(f"Check if {title.split()[0]}'s Information is Not Applicable")
            skip.setObjectName(f"{prefix}_skip")
            skip.setCursor(Qt.CursorShape.PointingHandCursor)
            skip.setStyleSheet("""
                QCheckBox {
                    font-size: 14px;
                    color: #555;
                    font-weight: bold;
                }
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                }
                QCheckBox::indicator:unchecked {
                    border: 2px solid #ccc;
                    background-color: white;
                    border-radius: 4px;
                }
                QCheckBox::indicator:checked {
                    border: 2px solid #ff7043;
                    background-color: #ff7043;
                    border-radius: 4px;
                }
            """)

            # Add visual feedback when skipping sections
            section_controls = QWidget()
            section_controls.setObjectName(f"{prefix}_controls")
            section_controls_layout = QHBoxLayout(section_controls)
            section_controls_layout.setContentsMargins(0, 0, 0, 0)

            skip_notification = QLabel("This section will be skipped")
            skip_notification.setStyleSheet("color: #ff7043; font-style: italic; margin-left: 10px;")
            skip_notification.setVisible(False)

            section_controls_layout.addWidget(skip)
            section_controls_layout.addWidget(skip_notification)
            section_controls_layout.addStretch()

            layout.addWidget(section_controls)

            # Connect checkbox to show/hide notification and disable form fields
            skip.stateChanged.connect(lambda state, label=skip_notification, p=prefix: self.handle_skip_state(state, label, p))

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        # Name fields
        name_layout = QHBoxLayout()
        name_fields = ["last_name", "first_name", "middle_name", "extension"]
        name_widths = [120, 120, 120, 80]

        for field, width in zip(name_fields, name_widths):
            edit = QLineEdit()
            edit.setObjectName(f"{prefix}_{field}")
            edit.setPlaceholderText(field.replace('_', ' ').title())
            edit.setMinimumWidth(width)
            edit.setFixedHeight(32)
            edit.setStyleSheet(self.textbox_style)
            name_layout.addWidget(edit)
            controls[field] = edit

        name_row = QWidget()
        name_row.setLayout(name_layout)
        form.addRow("Name:", name_row)

        # Age
        age_edit = QLineEdit()
        age_edit.setObjectName(f"{prefix}_age")
        age_edit.setMinimumWidth(80)
        age_edit.setFixedHeight(32)
        age_edit.setStyleSheet(self.textbox_style)
        form.addRow("Age:", age_edit)
        controls["age"] = age_edit

        # Only add Gender field for Guardian (not for Father or Mother)
        if prefix == "guardian":
            gender = QComboBox()
            gender.setObjectName(f"{prefix}_gender")
            gender.addItems(["Select Gender...", "Male", "Female", "Other"])
            gender.setFixedHeight(32)
            gender.setStyleSheet(self.combobox_style)  # Use the updated combobox style
            form.addRow("Gender:", gender)
            controls["gender"] = gender

        # Ethnicity
        eth_edit = QLineEdit()
        eth_edit.setObjectName(f"{prefix}_ethnicity")
        eth_edit.setMinimumWidth(120)
        eth_edit.setFixedHeight(32)
        eth_edit.setStyleSheet(self.textbox_style)
        form.addRow("Ethnicity:", eth_edit)
        controls["ethnicity"] = eth_edit

        # Occupation
        occ_edit = QLineEdit()
        occ_edit.setObjectName(f"{prefix}_occupation")
        occ_edit.setMinimumWidth(120)
        occ_edit.setFixedHeight(32)
        occ_edit.setStyleSheet(self.textbox_style)
        form.addRow("Occupation:", occ_edit)
        controls["occupation"] = occ_edit

        # Education
        education = QComboBox()
        education.setObjectName(f"{prefix}_education")
        education.addItems([
            "Select Educational Attainment...", "Elementary", "High School", "College", "Postgraduate", "Other"
        ])
        education.setFixedHeight(32)
        education.setStyleSheet(self.combobox_style)  # Use the updated combobox style
        form.addRow("Highest Educational Attainment:", education)
        controls["education"] = education

        layout.addLayout(form)

        # Checkbox logic
        if skip:
            def toggle_group(state):
                checked = state == Qt.CheckState.Checked
                for control in controls.values():
                    if isinstance(control, (QLineEdit, QComboBox)):
                        control.setDisabled(checked)
                        if checked:
                            if isinstance(control, QLineEdit):
                                control.clear()
                            elif isinstance(control, QComboBox):
                                control.setCurrentIndex(0)

            skip.stateChanged.connect(toggle_group)
            controls["skip"] = skip

        return {"widget": group, "controls": controls}

    def get_parent_data(self, prefix):
        data = {}

        skip = self.findChild(QCheckBox, f"{prefix}_skip")
        if skip and skip.isChecked():
            data["skipped"] = True
            return data

        data["skipped"] = False

        # Get name fields
        name_parts = ["last_name", "first_name", "middle_name", "extension"]
        other_fields = ["age", "gender", "ethnicity", "occupation", "education"]

        for field in name_parts:
            control = self.findChild(QLineEdit, f"{prefix}_{field}")
            data[field] = control.text() if control else ""

        for field in other_fields:
            control = self.findChild((QLineEdit, QComboBox), f"{prefix}_{field}")
            if isinstance(control, QLineEdit):
                data[field] = control.text()
            elif isinstance(control, QComboBox):
                data[field] = control.currentText()
            else:
                data[field] = ""

        return data

    def get_data(self):
        return {
            "father": self.get_parent_data("father"),
            "mother": self.get_parent_data("mother"),
            "guardian": self.get_parent_data("guardian")
        }

    def on_next(self):
        self.next_clicked.emit(self.get_data())

    def handle_skip_state(self, state, notification_label, prefix):
        """Handle the state change of skip checkboxes"""
        is_checked = state == 2  # Qt.CheckState.Checked

        # Show/hide notification
        notification_label.setVisible(is_checked)

        # Enable/disable form fields for this section
        controls = self.findChildren(QWidget, f"{prefix}_*")
        for control in controls:
            # Skip the container itself and other non-input controls
            if isinstance(control, (QLineEdit, QComboBox)):
                control.setEnabled(not is_checked)
                if is_checked:
                    if isinstance(control, QLineEdit):
                        control.clear()
                    elif isinstance(control, QComboBox):
                        control.setCurrentIndex(0)
                    # Update visual style for disabled controls
                    control.setStyleSheet("""
                        background-color: #f3f3f3;
                        color: #999;
                        border: 1px solid #ddd;
                    """)
                else:
                    # Restore original style
                    if isinstance(control, QLineEdit):
                        control.setStyleSheet(self.textbox_style)
                    elif isinstance(control, QComboBox):
                        control.setStyleSheet(self.combobox_style)  # Restore combobox style
