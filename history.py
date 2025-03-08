from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, 
                           QPushButton, QTableWidgetItem, QHBoxLayout)
from PyQt5.QtCore import Qt
from themes import apply_theme
import json
from datetime import datetime

class History(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent
        self.db = parent.db if parent else None
        self.setWindowTitle("Browsing History")
        self.setFixedSize(600, 400)
        
        if parent and hasattr(parent, 'settings'):
            apply_theme(self, parent.settings.get('theme', 'dracula'))
        
        layout = QVBoxLayout(self)
        
        # Create history table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Date"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear History")
        clear_button.clicked.connect(self.clear_history)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(clear_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.load_history()
        
    def load_history(self):
        if not self.db:
            return
            
        history = self.db.get_history()
        self.table.setRowCount(len(history))
        for i, entry in enumerate(history):
            self.table.setItem(i, 0, QTableWidgetItem(entry["title"]))
            self.table.setItem(i, 1, QTableWidgetItem(entry["url"]))
            self.table.setItem(i, 2, QTableWidgetItem(entry["date"]))
    
    def clear_history(self):
        if self.db:
            self.db.clear_history()
        self.table.setRowCount(0)
