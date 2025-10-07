from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

# Load the logo using the image helper
from image_helper import load_pixmap

class StudentEmailScreen(QWidget):
    next_clicked = pyqtSignal(dict)  # Modified to pass data

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2356c5;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        pixmap = load_pixmap("owl_logo.png")
        logo = QLabel()
        logo.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(40)

        # Email input with icon
        email_row = QHBoxLayout()
        email_icon = QLabel()
        email_icon.setText("👤")
        email_icon.setStyleSheet("color: #2356c5; background: white; border-top-left-radius: 4px; border-bottom-left-radius: 4px; padding: 8px;")
        email_icon.setFixedWidth(32)

        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText("EMAIL")
        self.email_field.setFixedWidth(300)
        self.email_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border-radius: 4px;
                padding: 8px;
                border: 1px solid #bfcbe6;
                font-size: 16px;
                color: #2356c5;
            }
        """)

        email_row.addWidget(email_icon)
        email_row.addWidget(self.email_field)
        email_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(email_row)
        layout.addSpacing(20)

        # Next button
        next_btn = QPushButton("Next")
        next_btn.setFixedWidth(332)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2356c5;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        next_btn.clicked.connect(self.on_next)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def get_data(self):
        return {
            "email": self.email_field.text()
        }

    def on_next(self):
        self.next_clicked.emit(self.get_data())
