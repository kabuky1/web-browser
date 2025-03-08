from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QCheckBox, QPushButton,
                           QTabWidget, QWidget)
import json
import os
from themes import THEMES, apply_theme

class Settings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = parent  
        self.setWindowTitle("Browser Settings")
        self.setFixedSize(400, 500)
        
        # Default settings
        self.default_settings = {
            "homepage": "https://www.duckduckgo.com",
            "search_engine": "duckduckgo",  # lowercase default
            "enable_cookies": True,
            "enable_javascript": True,
            "download_path": os.path.expanduser("~/Downloads"),
            "theme": "dark"
        }
        
        self.current_settings = self.load_settings()
        self.create_settings_ui()
        
        # Apply the dark theme
        self.setStyleSheet("""
            QDialog, QTabWidget, QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit, QComboBox {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 5px;
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
            QCheckBox {
                color: #ffffff;
            }
        """)

    def create_settings_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Homepage
        homepage_layout = QHBoxLayout()
        homepage_layout.addWidget(QLabel("Homepage:"))
        self.homepage_input = QLineEdit(self.current_settings["homepage"])
        homepage_layout.addWidget(self.homepage_input)
        general_layout.addLayout(homepage_layout)
        
        # Search Engine
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search Engine:"))
        self.search_combo = QComboBox()
        search_engines = ["DuckDuckGo", "Google", "Bing"]  # Make DuckDuckGo first
        self.search_combo.addItems(search_engines)
        
        # Set current search engine (case-insensitive comparison)
        current_engine = self.current_settings["search_engine"].lower()
        for i in range(self.search_combo.count()):
            if self.search_combo.itemText(i).lower() == current_engine:
                self.search_combo.setCurrentIndex(i)
                break
                
        search_layout.addWidget(self.search_combo)
        general_layout.addLayout(search_layout)
        
        tabs.addTab(general_tab, "General")
        
        # Privacy tab
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)
        
        self.cookie_checkbox = QCheckBox("Enable Cookies")
        self.cookie_checkbox.setChecked(self.current_settings["enable_cookies"])
        privacy_layout.addWidget(self.cookie_checkbox)
        
        self.js_checkbox = QCheckBox("Enable JavaScript")
        self.js_checkbox.setChecked(self.current_settings["enable_javascript"])
        privacy_layout.addWidget(self.js_checkbox)
        
        tabs.addTab(privacy_tab, "Privacy")
        
        # Add Appearance tab
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Dracula", "System"])
        current_theme = self.current_settings.get("theme", "Dracula").capitalize()
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.preview_theme)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        tabs.addTab(appearance_tab, "Appearance")
        
        layout.addWidget(tabs)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

    def preview_theme(self, theme_name):
        apply_theme(self, theme_name.lower())

    def load_settings(self):
        try:
            with open("browser_settings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.default_settings.copy()

    def save_settings(self):
        settings = {
            "homepage": self.homepage_input.text(),
            "search_engine": self.search_combo.currentText().lower(),  # ensure lowercase
            "enable_cookies": self.cookie_checkbox.isChecked(),
            "enable_javascript": self.js_checkbox.isChecked(),
            "download_path": self.current_settings["download_path"],
            "theme": self.theme_combo.currentText().lower()
        }
        
        with open("browser_settings.json", "w") as f:
            json.dump(settings, f)
        
        # Store settings in browser
        if self.browser:
            self.browser.settings = settings
            
        self.accept()