from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFormLayout, QGroupBox, QScrollArea, QStackedLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from image_helper import load_pixmap  # Import the image helper

class Form3Academic(QWidget):
    next_clicked = pyqtSignal(dict)  # Changed to emit dict
    back_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.resize(1200, 850)
        self.setStyleSheet("background-color: #f7f7f7;")

        # Updated textbox style to ensure white background
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

        # Combobox style with white background
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

        # Add owl logo
        owl_img = QLabel()
        owl_img.setPixmap(QPixmap("owl_logo2.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(owl_img)
        sidebar_layout.addSpacing(20)

        # Sidebar menu with buttons
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

        # Replace "Form" page with the real form
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

        # Academic Info
        academic_group = QGroupBox()
        academic_group.setStyleSheet("border: none;")
        academic_layout = QVBoxLayout(academic_group)

        academic_title = QLabel("C. Academic Profile")
        academic_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        academic_title.setStyleSheet("background-color: #4bb3fd; color: white; border-radius: 4px; padding: 6px 12px;")
        academic_layout.addWidget(academic_title)
        academic_layout.addSpacing(10)

        # Elementary Background
        elementary_group = QGroupBox("Elementary")
        elementary_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }
        """)
        elementary_layout = QFormLayout()
        elementary_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        elementary_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        elementary_layout.setSpacing(15)

        # Year Graduated
        elem_year = self.make_textbox(200, "Year Graduated...")
        elem_year.setObjectName("elem_year")  # Added object name
        elementary_layout.addRow("Year Graduated:", elem_year)

        # School Name
        elem_school = self.make_textbox(400, "School...")
        elem_school.setObjectName("elem_school")  # Added object name
        elementary_layout.addRow("Name of the School:", elem_school)

        # Honors
        elem_honors = self.make_textbox(400)
        elem_honors.setObjectName("elem_honors")  # Added object name
        elementary_layout.addRow("Honors Recieved:", elem_honors)

        elementary_group.setLayout(elementary_layout)
        academic_layout.addWidget(elementary_group)
        academic_layout.addSpacing(20)

        # Junior High School Background
        jhs_group = QGroupBox("Junior High")
        jhs_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 8px;
                margin-top: 15px;
                padding: 15px;
            }
        """)
        jhs_layout = QFormLayout()
        jhs_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        jhs_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        jhs_layout.setSpacing(15)

        # Year Graduated
        jhs_year = self.make_textbox(200, "Year Graduated...")
        jhs_year.setObjectName("jhs_year")  # Added object name
        jhs_layout.addRow("Year Graduated:", jhs_year)

        # School Name
        jhs_school = self.make_textbox(400, "School...")
        jhs_school.setObjectName("jhs_school")  # Added object name
        jhs_layout.addRow("Name of the School:", jhs_school)

        # Honors
        jhs_honors = self.make_textbox(400)
        jhs_honors.setObjectName("jhs_honors")  # Added object name
        jhs_layout.addRow("Honors Recieved:", jhs_honors)

        jhs_group.setLayout(jhs_layout)
        academic_layout.addWidget(jhs_group)

        form_area.addWidget(academic_group)

        # Navigation
        nav_layout = QHBoxLayout()

        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""
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
        back_btn.setFixedWidth(160)
        back_btn.setFixedHeight(45)
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        next_btn = QPushButton("Next")
        next_btn.setStyleSheet("""
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
        next_btn.setFixedWidth(160)
        next_btn.setFixedHeight(45)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_layout.addWidget(back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(next_btn)

        form_area.addSpacing(20)
        form_area.addLayout(nav_layout)

        back_btn.clicked.connect(self.back_clicked.emit)
        next_btn.clicked.connect(self.on_next)  # Changed to call on_next

        return form_widget

    def get_data(self):
        """Collect form data"""
        data = {
            'elementary_school': self.findChild(QLineEdit, 'elem_school').text(),
            'elementary_year': self.findChild(QLineEdit, 'elem_year').text(),
            'elementary_honors': self.findChild(QLineEdit, 'elem_honors').text(),
            'jhs_school': self.findChild(QLineEdit, 'jhs_school').text(),
            'jhs_year': self.findChild(QLineEdit, 'jhs_year').text(),
            'jhs_honors': self.findChild(QLineEdit, 'jhs_honors').text()
        }
        return data

    def on_next(self):
        """Emit form data when next is clicked"""
        self.next_clicked.emit(self.get_data())

    # ---------------- Helpers ----------------
    def make_textbox(self, width=200, placeholder=""):
        tb = QLineEdit()
        tb.setMinimumWidth(width)
        tb.setFixedHeight(32)
        tb.setPlaceholderText(placeholder)
        tb.setStyleSheet(self.textbox_style)
        return tb

    def combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setFixedHeight(32)
        c.setStyleSheet(self.combobox_style)  # Apply custom style
        return c

    def row(self, widgets):
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

    def rowWidget(self, widgets):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        for w in widgets:
            layout.addWidget(w)
        container = QWidget()
        container.setLayout(layout)
        return container
