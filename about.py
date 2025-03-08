from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from themes import apply_theme

class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Secure Browser")
        self.setFixedSize(400, 300)
        
        # Apply parent's theme
        if parent and hasattr(parent, 'settings'):
            apply_theme(self, parent.settings.get('theme', 'dracula'))
        
        layout = QVBoxLayout(self)
        
        # Browser info
        title = QLabel("Secure Browser")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        version = QLabel("Version 1.0")
        layout.addWidget(version)
        
        description = QLabel(
            "A secure and private web browser focused on:\n"
            "• Ad blocking\n"
            "• Cookie management\n"
            "• JavaScript control\n"
            "• Privacy protection"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Add some spacing
        layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px 10px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)
