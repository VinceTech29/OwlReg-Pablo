# emergency_form_scroll.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QCheckBox, QScrollArea, QLineEdit, QStackedLayout, QComboBox
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from image_helper import load_pixmap  # Import the image helper


class EmergencyForm(QWidget):
    next_clicked = pyqtSignal(dict)  # Changed to emit dict
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resize(1200, 850)
        self.setStyleSheet("background-color: #f7f7f7;")

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

        # Add owl logo
        owl_img = QLabel()
        owl_img.setPixmap(QPixmap("owl_logo2.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(owl_img)
        sidebar_layout.addSpacing(20)

        # Menu items
        self.pages = QStackedLayout()
        menu_items = ["Discover", "Form", "About", "Vision Mission and...", "Library", "Subject", "Scholarship", "Feedback"]

        for i, text in enumerate(menu_items):
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
            btn.clicked.connect(lambda _, idx=i: self.pages.setCurrentIndex(idx))
            sidebar_layout.addWidget(btn)

            placeholder = QLabel(f"{text} – Empty (Soon to open...)")
            placeholder.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pages.addWidget(placeholder)

        main_layout.addWidget(sidebar_widget)

        # ---------------- Main Area ----------------
        main_container = QWidget()
        main_container.setLayout(self.pages)
        main_layout.addWidget(main_container, stretch=1)

        self.pages.insertWidget(1, self.build_scroll_form())
        self.pages.setCurrentIndex(1)

    def build_scroll_form(self):
        # Add scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------- HEADER ----------
        header = QLabel("Student General Information Sheet")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 8px; padding: 18px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(header)
        content_layout.addSpacing(15)

        # ---------- EMERGENCY CONTACT ----------
        emergency_group = QGroupBox()
        emergency_group.setStyleSheet("border: none;")
        emergency_layout = QVBoxLayout(emergency_group)

        emergency_title = QLabel("D. Emergency Contact Information")
        emergency_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        emergency_title.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 4px; padding: 6px 12px;")
        emergency_layout.addWidget(emergency_title)
        emergency_layout.addSpacing(10)

        # Form fields with object names
        form = QFormLayout()
        form.addRow("Name:", self.row([
            ("Last Name:", self.make_textbox(120, objectName="last_name")),
            ("First Name:", self.make_textbox(120, objectName="first_name")),
            ("Middle Name:", self.make_textbox(120, objectName="middle_name"))
        ]))

        relationship_edit = self.make_textbox(300, objectName="relationship")
        form.addRow("Relationship to Student:", relationship_edit)

        form.addRow("Contact Numbers:", self.row([
            ("Mobile:", self.make_textbox(140, objectName="mobile")),
            ("Landline:", self.make_textbox(140, objectName="landline"))
        ]))

        address_edit = self.make_textbox(600, objectName="address")
        form.addRow("Complete Address:", address_edit)

        emergency_layout.addLayout(form)

        content_layout.addWidget(emergency_group)
        content_layout.addSpacing(20)

        # ---------- NOTICE, CONSENT & ENROLLMENT ----------
        notice_group = QGroupBox()
        notice_group.setStyleSheet("border: none;")
        notice_layout = QVBoxLayout(notice_group)

        # Warning Banner
        warning_text = QLabel("APPROVAL WILL BE AUTOMATICALLY REVOKED IF THE SUBMITTED BASIS FOR ACCEPTANCE IS LATER PROVEN FRAUDULENT. ANY UNITS EARNED FROM THE TIME OF ACCEPTANCE SHALL BE CONSIDERED NULL AND VOID.")
        warning_text.setWordWrap(True)
        warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_text.setStyleSheet("""
            QLabel {
                color: black;
                font-weight: bold;
                font-size: 14px;
                border-top: 2px solid #ccc;
                border-bottom: 2px solid #ccc;
                padding: 12px;
                background-color: #fff;
            }
        """)
        notice_layout.addWidget(warning_text)

        # Consent
        consent_title = QLabel("CONSENT")
        consent_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        consent_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        consent_title.setStyleSheet("color: #2356c5; margin-top: 15px;")
        notice_layout.addWidget(consent_title)

        consent_text = QLabel(
            "I hereby give my consent to the school to collect my personal data and information by filling up and submitting "
            "the Student General Information Sheet for purposes of processing my application for admission and enrolment, "
            "and such other legitimate purpose or purposes in relation to my intention to study at the school.\n\n"
            "All information provided shall be treated with strict confidentiality and shall not be disclosed to third parties "
            "without my written permission or consent, except as may be required by law and in accordance with the Data Privacy "
            "Act of 2012 (Republic Act 10173)."
        )
        consent_text.setWordWrap(True)
        consent_text.setStyleSheet("font-size: 13px; color: #333; padding: 5px;")
        notice_layout.addWidget(consent_text)

        # Conditional Enrollment
        enrollment_title = QLabel("CONDITIONAL ENROLLMENT")
        enrollment_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        enrollment_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        enrollment_title.setStyleSheet("color: #2356c5; margin-top: 15px;")
        notice_layout.addWidget(enrollment_title)

        # Requirements (2 columns)
        requirements = QHBoxLayout()
        freshmen = QLabel("FRESHMEN\n\nForm 137\nPSA Cert. of Live Birth\nCert. of Good Moral Character\nOthers")
        transferee = QLabel("TRANSFEREE\n\nCert. of Honorable Dismissal\nForm 137\nPSA Cert. of Live Birth\nCert. of Good Moral Character\nOthers")

        for col in (freshmen, transferee):
            col.setStyleSheet("font-size: 13px; color: #333; margin: 10px;")
            col.setAlignment(Qt.AlignmentFlag.AlignTop)
        requirements.addWidget(freshmen)
        requirements.addWidget(transferee)
        notice_layout.addLayout(requirements)

        # Acknowledgment
        acknowledgment_text = QLabel(
            "I hereby acknowledge that my enrolment is conditional upon the submission of the above-mentioned document/s, "
            "which I commit to provide within four (4) semesters, except for the JHS Card/F137A which must be submitted within two (2) semesters.\n\n"
            "I further acknowledge that failure to submit the required document/s within the specified period shall result "
            "in the cancellation of my enrolment. In such case, I understand that I will not be entitled to credits for "
            "the subjects I have enrolled in, nor to any refund of payments made. Additionally, this will not release me "
            "from my responsibility to settle any outstanding balance."
        )
        acknowledgment_text.setWordWrap(True)
        acknowledgment_text.setStyleSheet("font-size: 13px; color: #333; padding: 5px;")
        notice_layout.addWidget(acknowledgment_text)

        content_layout.addWidget(notice_group)

        # Agreement Checkbox
        agreement_check = QCheckBox("I have read and agree to the terms and conditions stated above.")
        agreement_check.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                margin: 10px;
            }
            QCheckBox:checked {
                color: #2356c5;
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
                border: 2px solid #4bb3fd;
                background-color: #4bb3fd;
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(agreement_check)

        # Navigation
        nav_layout = QHBoxLayout()
        back_btn = QPushButton("Back")
        next_btn = QPushButton("Next")

        for btn in (back_btn, next_btn):
            btn.setFixedWidth(160)
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4bb3fd;
                    color: white;
                    font-size: 16px;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #379be6;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)
        content_layout.addLayout(nav_layout)

        # Enable next only if checked
        self.agreement_check = agreement_check  # Store reference
        agreement_check.stateChanged.connect(lambda state: self.update_next_button(next_btn, state))
        next_btn.setEnabled(False)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #ccc;
                color: #666;
                font-size: 16px;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)

        back_btn.clicked.connect(self.back_clicked.emit)
        next_btn.clicked.connect(self.on_next)  # Changed to call on_next

        scroll.setWidget(content_widget)
        return scroll

    def update_next_button(self, button, state):
        """Update next button appearance based on checkbox state"""
        if state == 2:  # Checked
            button.setEnabled(True)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4bb3fd;
                    color: white;
                    font-size: 16px;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #379be6;
                }
            """)
        else:  # Not checked
            button.setEnabled(False)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ccc;
                    color: #666;
                    font-size: 16px;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
            """)

    def make_textbox(self, width=200, placeholder="", objectName=""):
        tb = QLineEdit()
        if objectName:
            tb.setObjectName(objectName)
        tb.setMinimumWidth(width)
        tb.setFixedHeight(32)
        tb.setPlaceholderText(placeholder)
        tb.setStyleSheet(self.textbox_style)
        return tb

    def row(self, widgets):
        """Helper method to create a row of widgets with labels"""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        for label_text, widget in widgets:
            lbl = QLabel(label_text)
            lbl.setFixedWidth(120)
            layout.addWidget(lbl)
            layout.addWidget(widget)
        row_widget = QWidget()
        row_widget.setLayout(layout)
        return row_widget

    def get_data(self):
        """Collect form data"""
        data = {
            'contact_person': ' '.join(filter(None, [
                self.findChild(QLineEdit, 'first_name').text() if self.findChild(QLineEdit, 'first_name') else '',
                self.findChild(QLineEdit, 'middle_name').text() if self.findChild(QLineEdit, 'middle_name') else '',
                self.findChild(QLineEdit, 'last_name').text() if self.findChild(QLineEdit, 'last_name') else ''
            ])),
            'relationship': self.findChild(QLineEdit, 'relationship').text() if self.findChild(QLineEdit, 'relationship') else '',
            'contact_number': self.findChild(QLineEdit, 'mobile').text() if self.findChild(QLineEdit, 'mobile') else '',
            'landline': self.findChild(QLineEdit, 'landline').text() if self.findChild(QLineEdit, 'landline') else '',
            'address': self.findChild(QLineEdit, 'address').text() if self.findChild(QLineEdit, 'address') else '',
            'terms_accepted': self.agreement_check.isChecked() if hasattr(self, 'agreement_check') else False
        }
        return data

    def on_next(self):
        """Emit form data when next is clicked"""
        self.next_clicked.emit(self.get_data())
