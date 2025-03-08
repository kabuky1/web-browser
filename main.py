from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                          QWidget, QLineEdit, QPushButton, QMenu, QAction, QDialog,
                          QTableWidgetItem)  
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
import os
import sys
import json
from settings import Settings
from about import About  
from themes import THEMES, apply_theme
from history import History
from downloads import Downloads
from datetime import datetime

class AdBlocker(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        # Basic ad blocking rules
        blocked_domains = [
            'ads', 'analytics', 'tracker', 'doubleclick.net',
            'google-analytics.com', 'advertising'
        ]
        if any(domain in url.lower() for domain in blocked_domains):
            info.block(True)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Browser")
        self.setGeometry(300, 300, 1024, 768)
        
        # Load settings first - this will set self.settings
        self.load_and_apply_settings()
        
        # Rest of the initialization using self.settings
        # Configure profile for cookie management
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setCachePath("")
        
        # Apply cookie settings from loaded settings
        if self.settings.get("enable_cookies", False):
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        else:
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Set up ad blocker
        self.ad_blocker = AdBlocker()
        self.profile.setUrlRequestInterceptor(self.ad_blocker)
        
        # Create web view with settings
        self.browser = QWebEngineView()
        self.page = QWebEnginePage(self.profile, self.browser)
        self.browser.setPage(self.page)
        
        # Configure browser settings from loaded settings
        browser_settings = self.browser.settings()
        browser_settings.setAttribute(QWebEngineSettings.JavascriptEnabled, 
                                   self.settings.get("enable_javascript", False))
        browser_settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        browser_settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        browser_settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
        
        # Set homepage from settings
        self.browser.setUrl(QUrl(self.settings.get("homepage", "https://www.duckduckgo.com")))
        
        # Connect signals for cookie management
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(self.clear_cookies)
        
        # Connect page title changed signal for history
        self.browser.titleChanged.connect(self.update_history)
        
        # Connect download requested signal
        self.page.profile().downloadRequested.connect(self.handle_download)

        # Navigation buttons
        self.back_button = QPushButton("←")
        self.back_button.clicked.connect(self.browser.back)
        
        self.forward_button = QPushButton("→")
        self.forward_button.clicked.connect(self.browser.forward)
        
        self.reload_button = QPushButton("↻")
        self.reload_button.clicked.connect(self.browser.reload)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_url)
        
        # Control buttons
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.navigate_to_url)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(QApplication.instance().quit)
        
        # Create main layout first
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create single navigation bar
        nav_widget = QWidget()
        nav_widget.setFixedHeight(40)
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 0, 5, 0)
        nav_layout.setSpacing(2)
        nav_widget.setLayout(nav_layout)
        
        # Add all controls to single row
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.forward_button)
        nav_layout.addWidget(self.reload_button)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.go_button)
        nav_layout.addWidget(self.close_button)  
        
        # Settings button and menu
        settings_button = QPushButton("☰")
        settings_button.setFixedSize(30, 30)
        settings_menu = QMenu(self)
        
        # Add menu items
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(settings_action)
        
        history_action = QAction("History", self)
        history_action.triggered.connect(self.show_history)
        settings_menu.addAction(history_action)
        
        downloads_action = QAction("Downloads", self)
        downloads_action.triggered.connect(self.show_downloads)
        settings_menu.addAction(downloads_action)
        
        settings_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)  
        settings_menu.addAction(about_action)
        
        settings_button.clicked.connect(lambda: settings_menu.exec_(settings_button.mapToGlobal(settings_button.rect().bottomRight())))
        nav_layout.addWidget(settings_button)
        
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.browser)
        
        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    def load_and_apply_settings(self):
        try:
            with open("browser_settings.json", "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                "homepage": "https://www.duckduckgo.com",
                "search_engine": "duckduckgo",
                "enable_cookies": False,
                "enable_javascript": False,
                "theme": "dracula",
                "download_path": os.path.expanduser("~/Downloads")
            }
            with open("browser_settings.json", "w") as f:
                json.dump(self.settings, f)
        
        # Apply theme immediately
        apply_theme(self, self.settings.get("theme", "dracula"))

    def open_settings(self):
        settings_dialog = Settings(self)
        result = settings_dialog.exec_()
        if result == QDialog.Accepted:
            # Reload settings and apply them
            self.load_and_apply_settings()

    def clear_cookies(self, _):
        self.profile.cookieStore().deleteAllCookies()
        
    def on_load_finished(self, ok):
        if ok:
            self.profile.cookieStore().deleteAllCookies()
            
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url        
            self.browser.setUrl(QUrl(url))            

    def update_url(self, url):        
        self.url_bar.setText(url.toString())

    def show_about(self):
        about_dialog = About(self)
        about_dialog.exec_()
        
    def update_history(self, title):
        url = self.browser.url().toString()
        entry = {
            "title": title,
            "url": url,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open("browser_history.json", "r") as f:
                history = json.load(f)
        except FileNotFoundError:
            history = []
            
        history.append(entry)
        
        with open("browser_history.json", "w") as f:
            json.dump(history, f)

    def handle_download(self, download):
        path = os.path.join(
            self.settings.get("download_path", os.path.expanduser("~/Downloads")),
            download.suggestedFileName()
        )
        download.setPath(path)
        download.accept()
        
        # Update downloads dialog if it exists
        if hasattr(self, 'downloads_dialog'):
            row = self.downloads_dialog.table.rowCount()
            self.downloads_dialog.table.insertRow(row)
            self.downloads_dialog.table.setItem(row, 0, QTableWidgetItem(download.suggestedFileName()))
            self.downloads_dialog.table.setItem(row, 2, QTableWidgetItem("Downloading..."))

    def show_history(self):
        history_dialog = History(self)
        history_dialog.exec_()

    def show_downloads(self):
        self.downloads_dialog = Downloads(self)
        self.downloads_dialog.exec_()
                
if __name__ == "__main__":    
    app = QApplication(sys.argv)    
    browser = Browser()    
    browser.show()
    sys.exit(app.exec_())