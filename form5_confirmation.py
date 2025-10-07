from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea,
    QHBoxLayout, QFrame, QGroupBox, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from image_helper import load_pixmap  # Import the image helper


class ConfirmationForm(QWidget):
    back_clicked = pyqtSignal()
    submit_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.form_data = {}
        self.summary_widget = None

        # Track submit button click to prevent multiple submissions
        self.submitted = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        title = QLabel("Confirmation & Summary")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2356c5; padding: 10px; background-color: #f0f5ff; border-radius: 8px;")
        main_layout.addWidget(title)

        # Logo/image if needed
        if hasattr(self, 'logo_label') and self.logo_label:
            logo_pixmap = load_pixmap("owl_logo2.png")
            self.logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation))

        # Scroll area for long content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        main_layout.addWidget(self.scroll, 1)  # Give it a stretch factor of 1

        # Placeholder summary widget
        self.summary_widget = QWidget()
        self.scroll.setWidget(self.summary_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(15)

        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(130, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #4bb3fd;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #379be6;
            }
        """)
        self.back_button.clicked.connect(self.back_clicked.emit)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedSize(130, 40)
        self.submit_button.setStyleSheet("""
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
        self.submit_button.clicked.connect(self.on_submit)

        button_layout.addWidget(self.back_button)
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        main_layout.addLayout(button_layout)

    def update_data(self, data):
        """Update the form with the collected data"""
        self.form_data = data
        self.rebuild_summary()

    def rebuild_summary(self):
        """Rebuild the summary section with current data"""
        if self.summary_widget:
            self.summary_widget.deleteLater()

        self.summary_widget = QWidget()
        summary_layout = QVBoxLayout(self.summary_widget)
        summary_layout.setSpacing(20)
        summary_layout.setContentsMargins(10, 10, 10, 10)
        summary_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Extract all collected data
        email_data = self.form_data.get('email', {})
        personal_data = self.form_data.get('personal', {})
        family_data = self.form_data.get('family', {})
        academic_data = self.form_data.get('academic', {})
        emergency_data = self.form_data.get('emergency', {})

        # Process family data to remove internal fields and set empty values to N/A
        processed_family_data = self.process_family_data(family_data)

        # Add sections
        summary_layout.addWidget(self.create_section("Email Information", email_data))
        summary_layout.addWidget(self.create_section("Personal Information", personal_data))
        summary_layout.addWidget(self.create_section("Family Information", processed_family_data))
        summary_layout.addWidget(self.create_section("Academic Information", academic_data))
        summary_layout.addWidget(self.create_section("Emergency Information", emergency_data))

        # Add the final agreement / consent
        agreement_box = QGroupBox("Terms & Consent")
        agreement_box.setStyleSheet("""
            QGroupBox {
                background-color: #fff8f0;
                border: 2px solid #ffa940;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
                color: #d46b08;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        agreement_layout = QVBoxLayout(agreement_box)

        agreement = QLabel("""
<b>APPROVAL WILL BE AUTOMATICALLY REVOKED IF THE SUBMITTED BASIS FOR ACCEPTANCE IS LATER PROVEN FRAUDULENT. ANY UNITS EARNED FROM THE TIME OF ACCEPTANCE SHALL BE CONSIDERED NULL AND VOID.</b><br><br>

<b>CONSENT</b><br>
I hereby give my consent to the school to collect my personal data and information by filling up and submitting the Student General Information Sheet for purposes of processing my application for admission and enrolment, and such other legitimate purpose or purposes in relation to my intention to study at the school.<br><br>

All information provided shall be treated with strict confidentiality and shall not be disclosed to third parties without my written permission or consent, except as may be required by law and in accordance with the Data Privacy Act of 2012 (Republic Act 10173).<br><br>

<b>CONDITIONAL ENROLLMENT</b><br>
<b>FRESHMEN</b><br>
- Form 137<br>
- PSA Cert. of Live Birth<br>
- Cert. of Good Moral Character<br>
- Others<br><br>

<b>TRANSFEREE</b><br>
- Cert. of Honorable Dismissal<br>
- Form 137<br>
- PSA Cert. of Live Birth<br>
- Cert. of Good Moral Character<br>
- Others<br><br>

I hereby acknowledge that my enrolment is conditional upon the submission of the above-mentioned document/s, which I commit to provide within four (4) semesters, except for the JHS Card/F137A which must be submitted within two (2) semesters.<br><br>

I further acknowledge that failure to submit the required document/s within the specified period shall result in the cancellation of my enrolment. In such case, I understand that I will not be entitled to credits for the subjects I have enrolled in, nor to any refund of payments made. Additionally, this will not release me from my responsibility to settle any outstanding balance.
        """)
        agreement.setWordWrap(True)
        agreement.setStyleSheet("color: #333; margin-top: 5px; padding: 5px;")
        agreement_layout.addWidget(agreement)

        summary_layout.addWidget(agreement_box)

        # Add some space at the bottom
        summary_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.scroll.setWidget(self.summary_widget)

    def create_section(self, title, data_dict):
        """Helper to create summary sections"""
        section = QGroupBox(title)
        section.setStyleSheet("""
            QGroupBox {
                background-color: #f5f5f5;
                border: 2px solid #4bb3fd;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                padding: 10px;
                color: #2356c5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(8)

        if not data_dict:
            no_data = QLabel("No data provided.")
            no_data.setStyleSheet("color: gray; font-style: italic;")
            section_layout.addWidget(no_data)
        else:
            for key, value in data_dict.items():
                # Format the key for better display (replace underscores with spaces, capitalize)
                display_key = key.replace('_', ' ').title()

                # Create row with formatted data
                row = QLabel(f"<b>{display_key}:</b> {value}")
                row.setWordWrap(True)
                row.setStyleSheet("color: #333; padding: 3px;")
                section_layout.addWidget(row)

        return section

    def process_family_data(self, family_data):
        """Process family data to display only relevant information and format it properly"""
        processed_data = {}

        # Handle father information
        father = family_data.get('father', {})
        if father and not father.get('skipped', True):
            # Combine first and last name instead of showing them separately
            full_name = f"{father.get('first_name', '')} {father.get('last_name', '')}".strip()
            if full_name:
                processed_data['Father Name'] = full_name

            # Add other father fields except metadata fields
            for key, value in father.items():
                if key not in ['first_name', 'last_name', 'skipped']:
                    if value:
                        processed_data[f'Father {key.replace("_", " ").title()}'] = value
                    else:
                        processed_data[f'Father {key.replace("_", " ").title()}'] = 'N/A'
        else:
            processed_data['Father Information'] = 'N/A'

        # Handle mother information
        mother = family_data.get('mother', {})
        if mother and not mother.get('skipped', True):
            # Combine first and last name
            full_name = f"{mother.get('first_name', '')} {mother.get('last_name', '')}".strip()
            if full_name:
                processed_data['Mother Name'] = full_name

            # Add other mother fields except metadata fields
            for key, value in mother.items():
                if key not in ['first_name', 'last_name', 'skipped']:
                    if value:
                        processed_data[f'Mother {key.replace("_", " ").title()}'] = value
                    else:
                        processed_data[f'Mother {key.replace("_", " ").title()}'] = 'N/A'
        else:
            processed_data['Mother Information'] = 'N/A'

        # Handle guardian information
        guardian = family_data.get('guardian', {})
        if guardian and not guardian.get('skipped', True):
            # Combine first and last name
            full_name = f"{guardian.get('first_name', '')} {guardian.get('last_name', '')}".strip()
            if full_name:
                processed_data['Guardian Name'] = full_name

            # Add other guardian fields except metadata fields
            for key, value in guardian.items():
                if key not in ['first_name', 'last_name', 'skipped']:
                    if value:
                        processed_data[f'Guardian {key.replace("_", " ").title()}'] = value
                    else:
                        processed_data[f'Guardian {key.replace("_", " ").title()}'] = 'N/A'
        else:
            processed_data['Guardian Information'] = 'N/A'

        return processed_data

    def on_submit(self):
        """Handle the submit button click"""
        if self.submitted:
            return  # Ignore additional clicks if already submitted

        self.submitted = True
        # Change the button appearance to show submission is in progress
        self.submit_button.setText("Submitting...")
        self.submit_button.setEnabled(False)  # Disable to prevent multiple clicks

        print("Submit button clicked, emitting submit_clicked signal")
        # Emit the submit signal to be handled by the main window
        self.submit_clicked.emit()
        print("Signal emitted")