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
        try:
            with open("browser_history.json", "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
            
        self.table.setRowCount(len(history))
        for i, entry in enumerate(history):
            self.table.setItem(i, 0, QTableWidgetItem(entry.get("title", "")))
            self.table.setItem(i, 1, QTableWidgetItem(entry.get("url", "")))
            self.table.setItem(i, 2, QTableWidgetItem(entry.get("date", "")))
    
    def clear_history(self):
        self.table.setRowCount(0)
        with open("browser_history.json", "w") as f:
            json.dump([], f)
