
"""
A simple success screen that shows after form submission.
This is a simplified version to ensure it works properly.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class SuccessScreen(QWidget):
    close_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: white;")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header
        header = QLabel("Registration Successful!")
        header.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #4bb3fd; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Reference code frame
        ref_frame = QFrame()
        ref_frame.setFrameShape(QFrame.Shape.Box)
        ref_frame.setStyleSheet("""
            border: 2px solid #4bb3fd;
            border-radius: 10px;
            background-color: #f0f5ff;
            padding: 20px;
        """)

        ref_layout = QVBoxLayout(ref_frame)

        # Reference code title
        ref_title = QLabel("Your Reference Code:")
        ref_title.setFont(QFont("Arial", 16))
        ref_title.setStyleSheet("color: #333;")
        ref_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_layout.addWidget(ref_title)

        # The actual reference code
        self.code_label = QLabel("ST-101")
        self.code_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.code_label.setStyleSheet("color: #2356c5; margin: 20px 0;")
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_layout.addWidget(self.code_label)

        # Student name
        self.name_label = QLabel("")
        self.name_label.setFont(QFont("Arial", 14))
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ref_layout.addWidget(self.name_label)

        layout.addWidget(ref_frame)

        # Instructions
        instructions = QLabel(
            "Please keep this reference code. You will need to present it when you enroll physically."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #555; margin: 20px 0;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        # Thank you message
        thank_you = QLabel("THANK YOU FOR CHOOSING US!")
        thank_you.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        thank_you.setStyleSheet("color: #4bb3fd;")
        thank_you.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(thank_you)

        # Close button
        close_button = QPushButton("Close")
        close_button.setFixedSize(180, 50)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #4bb3fd;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #379be6;
            }
        """)
        close_button.clicked.connect(self.close_clicked.emit)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_code(self, code, name=""):
        """Set the reference code and optionally the student name"""
        self.code_label.setText(code)
        if name:
            self.name_label.setText(name)
