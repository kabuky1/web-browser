from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                           QPushButton, QTableWidgetItem, QHBoxLayout,
                           QFileDialog, QProgressBar)
from PyQt5.QtCore import Qt
from themes import apply_theme
import os

class Downloads(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.setWindowTitle("Downloads")
        self.setFixedSize(600, 400)
        
        if parent and hasattr(parent, 'settings'):
            apply_theme(self, parent.settings.get('theme', 'dracula'))
        
        layout = QVBoxLayout(self)
        
        # Create downloads table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Filename", "Progress", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
