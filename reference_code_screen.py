"""
Reference code confirmation screen that appears after successful registration.
Displays the student's reference code that they can use when enrolling physically.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor
from image_helper import load_pixmap


class ReferenceCodeScreen(QWidget):
    close_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registration Confirmation")
        self.reference_code = ""
        self.student_name = ""

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Top section with logo and title
        top_section = QHBoxLayout()

        # Logo
        logo_container = QVBoxLayout()
        logo_label = QLabel("OwlReg")
        logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #2356c5;")

        owl_img = QLabel()
        # Use the image helper to load the logo
        owl_pixmap = load_pixmap("owl_logo2.png")
        owl_img.setPixmap(owl_pixmap.scaled(100, 100,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.SmoothTransformation))

        owl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_container.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        logo_container.addWidget(owl_img, alignment=Qt.AlignmentFlag.AlignCenter)

        top_section.addLayout(logo_container)
        top_section.addSpacing(30)

        # Title and message
        title_container = QVBoxLayout()
        title = QLabel("Registration Successful!")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2356c5;")

        confirmation_message = QLabel(
            "Thank you for registering with OwlReg. Your information has been saved successfully."
        )
        confirmation_message.setWordWrap(True)
        confirmation_message.setStyleSheet("font-size: 14px; color: #444;")

        from datetime import datetime
        date_label = QLabel(datetime.now().strftime("%B %d, %Y"))
        date_label.setStyleSheet("font-size: 12px; color: #666;")

        title_container.addWidget(title)
        title_container.addWidget(confirmation_message)
        title_container.addWidget(date_label)

        top_section.addLayout(title_container, stretch=1)
        main_layout.addLayout(top_section)

        # Reference code display (card)
        code_card = QFrame()
        code_card.setFrameShape(QFrame.Shape.Box)
        code_card.setStyleSheet("""
            QFrame {
                background-color: #f0f5ff;
                border: 2px solid #4bb3fd;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        code_layout = QVBoxLayout(code_card)

        ref_title = QLabel("Your Unique Reference Code")
        ref_title.setFont(QFont("Arial", 16))
        ref_title.setStyleSheet("color: #2356c5;")
        ref_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Reference code display
        self.code_display = QLabel("ST-000000-0000")  # Placeholder
        self.code_display.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.code_display.setStyleSheet("color: #2356c5;")
        self.code_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add copy button
        copy_button = QPushButton("Copy Code")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4bb3fd;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #379be6;
            }
        """)
        copy_button.clicked.connect(self.copy_to_clipboard)

        # Important instructions
        instructions = QLabel(
            "Please save this reference code. You will need to provide this code when completing your enrollment."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #e63946; font-weight: bold; font-size: 14px; margin-top: 10px;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Student name
        self.name_display = QLabel()  # Will be set later
        self.name_display.setStyleSheet("font-size: 18px; color: #333;")
        self.name_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Database note (for SQLite fallback)
        self.db_note = QLabel()
        self.db_note.setStyleSheet("font-size: 12px; color: #e67e22; font-style: italic;")
        self.db_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.db_note.setVisible(False)

        # Add widgets to code layout
        code_layout.addWidget(ref_title)
        code_layout.addWidget(self.code_display)
        code_layout.addWidget(copy_button, alignment=Qt.AlignmentFlag.AlignCenter)
        code_layout.addWidget(self.name_display)
        code_layout.addWidget(instructions)
        code_layout.addWidget(self.db_note)

        main_layout.addWidget(code_card)

        # Additional information
        info_text = QLabel(
            "All your submitted information has been saved in our database. Please bring your supporting documents when you come for enrollment."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 13px; color: #444; margin-top: 15px;")
        main_layout.addWidget(info_text)

        # Close button
        close_button = QPushButton("Close")
        close_button.setFixedSize(150, 40)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2356c5;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1a408f;
            }
        """)
        close_button.clicked.connect(self.close_clicked.emit)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_code(self, reference_code, student_name):
        """Set the reference code and student name"""
        self.reference_code = reference_code
        self.student_name = student_name

        self.code_display.setText(reference_code)
        self.name_display.setText(f"Name: {student_name}")

    def set_db_note(self, note_text):
        """Set a database note (used for SQLite fallback notification)"""
        if note_text:
            self.db_note.setText(note_text)
            self.db_note.setVisible(True)
        else:
            self.db_note.setVisible(False)

    def copy_to_clipboard(self):
        """Copy the reference code to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.reference_code)

        # Visual feedback could be added here (like a temporary label)
