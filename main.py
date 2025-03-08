from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                          QWidget, QLineEdit, QPushButton, QMenu, QAction, QDialog,
                          QTableWidgetItem, QStatusBar, QLabel, QToolBar, QToolButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QTimer, Qt, QMimeData
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import QDrag
import os
import sys
import json
from settings import Settings
from about import About  
from themes import THEMES, apply_theme
from history import History
from downloads import Downloads
from datetime import datetime
import tempfile
from bookmarks import BookmarkManager

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

class BookmarkButton(QToolButton):
    def __init__(self, title, url, parent=None):
        super().__init__(parent)
        self.setText(title)
        self.url = url
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_start_position = e.pos()
        super().mousePressEvent(e)
        
    def mouseMoveEvent(self, e):
        if not (e.buttons() & Qt.LeftButton):
            return
        if (e.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.url)
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_bookmark()
        elif action == edit_action:
            self.edit_bookmark()
            
    def delete_bookmark(self):
        try:
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
            
            bookmarks["bookmarks"] = [b for b in bookmarks["bookmarks"] 
                                    if not (b["title"] == self.text() and b["url"] == self.url)]
            
            with open("browser_bookmarks.json", "w") as f:
                json.dump(bookmarks, f)
                
            self.parent().update_bookmark_bar()
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            
    def edit_bookmark(self):
        dialog = BookmarkManager(self.parent())
        dialog.title_input.setText(self.text())
        dialog.url_input.setText(self.url)
        dialog.exec_()

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
        
        # Set up cookie storage
        self.cookie_path = os.path.join(tempfile.gettempdir(), 'browser_cookies')
        if not os.path.exists(self.cookie_path):
            os.makedirs(self.cookie_path)
            
        self.profile.setPersistentStoragePath(self.cookie_path)
        self.profile.setCachePath(self.cookie_path)
        
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
        
        # Connect signals for cookie management - modify these connections
        self.browser.loadFinished.connect(self.on_load_finished)
        # Remove the urlChanged connection for cookies
        # self.browser.urlChanged.connect(self.clear_cookies)
        
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
        
        bookmarks_action = QAction("Manage Bookmarks", self)
        bookmarks_action.triggered.connect(self.show_bookmarks)
        settings_menu.addAction(bookmarks_action)
        
        add_bookmark_action = QAction("Add to Bookmarks", self)
        add_bookmark_action.triggered.connect(self.add_current_to_bookmarks)
        settings_menu.addAction(add_bookmark_action)
        
        settings_menu.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)  
        settings_menu.addAction(about_action)
        
        # Add show/hide bookmark bar action
        self.toggle_bookmarks_action = QAction("Show Bookmark Bar", self)
        self.toggle_bookmarks_action.setCheckable(True)
        self.toggle_bookmarks_action.setChecked(True)
        self.toggle_bookmarks_action.triggered.connect(self.toggle_bookmark_bar)
        settings_menu.addAction(self.toggle_bookmarks_action)
        
        settings_button.clicked.connect(lambda: settings_menu.exec_(settings_button.mapToGlobal(settings_button.rect().bottomRight())))
        nav_layout.addWidget(settings_button)
        
        main_layout.addWidget(nav_widget)
        main_layout.addWidget(self.browser)
        
        # Add bookmark bar
        self.bookmark_bar = QToolBar("Bookmarks")
        self.bookmark_bar.setMovable(False)
        self.addToolBar(self.bookmark_bar)
        self.update_bookmark_bar()
        
        # Set the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("QStatusBar { padding: 2px; }")
        self.setStatusBar(self.status_bar)
        
        # Add cookie counter to status bar
        self.cookie_label = QLabel("Cookies: 0")
        self.status_bar.addPermanentWidget(self.cookie_label)
        
        # Add status message
        self.status_label = QLabel("Ready")  # Changed from status_message to status_label
        self.status_bar.addWidget(self.status_label)
        
        # Track cookies with a list
        self.cookies = []
        self.cookie_count = 0
        cookie_store = self.profile.cookieStore()
        cookie_store.cookieAdded.connect(self.on_cookie_added)
        cookie_store.cookieRemoved.connect(self.on_cookie_removed)
        
        # Add tracking domains list
        self.tracking_domains = [
            'analytics', 'tracker', 'metrics',
            'doubleclick.net', 'facebook.com',
            'google-analytics.com', 'advertising',
            'pixel', 'statistics', 'stats',
            'tracking', 'adserver', 'monitor'
        ]
        
        # Add search engine URLs
        self.search_engines = {
            "google": "https://www.google.com/search?q={}",
            "duckduckgo": "https://duckduckgo.com/?q={}",
            "bing": "https://www.bing.com/search?q={}"
        }
        
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
        """Clear all cookies and reset counter"""
        self.profile.cookieStore().deleteAllCookies()
        self.cookies.clear()
        self.cookie_count = 0
        self.update_cookie_display()

    def on_load_finished(self, ok):
        if ok:
            self.set_status("Page loaded")  # Updated method name
            # Don't clear all cookies, they're managed by on_cookie_added
        else:
            self.set_status("Failed to load page")  # Updated method name
            
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        
        # Check if it's a valid URL
        if any([
            url.startswith(('http://', 'https://')),  # Has protocol
            url.split('.')[-1].lower() in ['com', 'org', 'net', 'edu', 'gov', 'io'],  # Common TLDs
            '.' in url and '/' in url,  # Likely a URL with path
            url.startswith('localhost'),  # Local development
            url.startswith('127.0.0.1'),  # Local development
        ]):
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            self.browser.setUrl(QUrl(url))
        else:
            # Use search engine
            engine = self.settings.get("search_engine", "duckduckgo").lower()
            search_url = self.search_engines.get(engine, self.search_engines["duckduckgo"])
            search_url = search_url.format(url.replace(' ', '+'))
            self.browser.setUrl(QUrl(search_url))
            
        self.set_status(f"Loading: {url}")

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
        
    def on_cookie_added(self, cookie):
        cookie_domain = cookie.domain()
        if cookie_domain.startswith('.'):
            cookie_domain = cookie_domain[1:]

        current_domain = self.browser.url().host()
        
        # Check if it's a third-party or tracking cookie
        is_third_party = current_domain not in cookie_domain
        is_tracker = any(tracker in cookie_domain.lower() for tracker in self.tracking_domains)
        
        if is_third_party or is_tracker:
            # Remove tracking/third-party cookie
            self.profile.cookieStore().deleteCookie(cookie)
        else:
            # Keep first-party cookie
            self.cookies.append(cookie)
            self.cookie_count += 1
            self.update_cookie_display()

    def on_cookie_removed(self, cookie):
        if cookie in self.cookies:
            self.cookies.remove(cookie)
            self.cookie_count = len(self.cookies)
            self.update_cookie_display()

    def update_cookie_display(self):
        self.cookie_label.setText(f"Cookies: {self.cookie_count}")
        
    def set_status(self, message):  # New method name to avoid confusion
        """Update the status bar message."""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            
    def update_bookmark_bar(self):
        """Update the bookmark bar with current bookmarks"""
        self.bookmark_bar.clear()
        try:
            with open("browser_bookmarks.json", "r") as f:
                data = json.load(f)
                
            # Initialize empty structure if file exists but is old format
            if isinstance(data, list):
                bookmarks = {
                    "folders": [],
                    "bookmarks": []
                }
                # Convert old bookmarks to new format
                for item in data:
                    bookmarks["bookmarks"].append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "folder": "No Folder"
                    })
                # Save in new format
                with open("browser_bookmarks.json", "w") as f:
                    json.dump(bookmarks, f)
            else:
                bookmarks = data

            # Create folder menus
            folder_menus = {}
            for folder in bookmarks.get("folders", []):
                folder_name = folder["name"]
                folder_button = QToolButton(self.bookmark_bar)
                folder_button.setText(folder_name)
                folder_button.setPopupMode(QToolButton.InstantPopup)
                folder_menu = QMenu(folder_button)
                folder_button.setMenu(folder_menu)
                folder_button.setContextMenuPolicy(Qt.CustomContextMenu)
                folder_button.customContextMenuRequested.connect(
                    lambda pos, name=folder_name: self.show_folder_context_menu(pos, name)
                )
                self.bookmark_bar.addWidget(folder_button)
                folder_menus[folder_name] = folder_menu

            # Add bookmarks
            for bookmark in bookmarks.get("bookmarks", []):
                folder = bookmark.get("folder", "No Folder")
                if folder != "No Folder" and folder in folder_menus:
                    # Add to folder menu
                    action = folder_menus[folder].addAction(bookmark["title"])
                    url = bookmark["url"]
                    action.triggered.connect(
                        lambda checked=False, url=url: self.browser.setUrl(QUrl(url))
                    )
                else:
                    # Only add to bar if not in a folder
                    if folder == "No Folder":
                        button = BookmarkButton(bookmark["title"], bookmark["url"], self)
                        button.clicked.connect(
                            lambda checked=False, url=bookmark["url"]: self.browser.setUrl(QUrl(url))
                        )
                        self.bookmark_bar.addWidget(button)

        except FileNotFoundError:
            bookmarks = {"folders": [], "bookmarks": []}
            with open("browser_bookmarks.json", "w") as f:
                json.dump(bookmarks, f)

    def show_folder_context_menu(self, pos, folder_name):
        """Show context menu for folder"""
        menu = QMenu(self)
        delete_action = menu.addAction("Delete Folder")
        action = menu.exec_(self.bookmark_bar.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_folder(folder_name)

    def delete_folder(self, folder_name):
        """Delete folder and move its bookmarks to No Folder"""
        try:
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
            
            # Remove folder
            bookmarks["folders"] = [f for f in bookmarks["folders"] 
                                  if f["name"] != folder_name]
            
            # Move bookmarks to No Folder
            for bookmark in bookmarks["bookmarks"]:
                if bookmark.get("folder") == folder_name:
                    bookmark["folder"] = "No Folder"
            
            with open("browser_bookmarks.json", "w") as f:
                json.dump(bookmarks, f)
                
            self.update_bookmark_bar()
        except Exception as e:
            print(f"Error deleting folder: {e}")

    def toggle_bookmark_bar(self):
        """Toggle bookmark bar visibility"""
        self.bookmark_bar.setVisible(self.toggle_bookmarks_action.isChecked())

    def show_bookmarks(self):
        """Show the bookmark manager dialog"""
        dialog = BookmarkManager(self)
        dialog.exec_()

    def add_current_to_bookmarks(self):
        """Add the current page to bookmarks"""
        title = self.browser.page().title()
        url = self.browser.url().toString()
        
        try:
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
                if isinstance(bookmarks, list):
                    bookmarks = {"folders": [], "bookmarks": bookmarks}
        except FileNotFoundError:
            bookmarks = {"folders": [], "bookmarks": []}
            
        bookmarks["bookmarks"].append({
            "title": title,
            "url": url,
            "folder": "No Folder"
        })
        
        with open("browser_bookmarks.json", "w") as f:
            json.dump(bookmarks, f)
            
        self.update_bookmark_bar()
                
if __name__ == "__main__":    
    app = QApplication(sys.argv)    
    browser = Browser()    
    browser.show()
    sys.exit(app.exec_())