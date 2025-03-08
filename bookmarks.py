from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
                           QComboBox, QInputDialog, QMainWindow, QToolButton)
from themes import apply_theme
import json

class BookmarkManager(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.browser = self.get_browser_window(parent)
        self.setWindowTitle("Manage Bookmarks")
        self.setFixedSize(600, 400)
        
        if parent and hasattr(parent, 'settings'):
            apply_theme(self, parent.settings.get('theme', 'dracula'))
            
        layout = QVBoxLayout(self)
        
        # Add bookmark section
        add_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_bookmark)
        
        add_layout.addWidget(QLabel("Title:"))
        add_layout.addWidget(self.title_input)
        add_layout.addWidget(QLabel("URL:"))
        add_layout.addWidget(self.url_input)
        add_layout.addWidget(QLabel("Folder:"))
        self.folder_combo = QComboBox()
        self.folder_combo.addItem("No Folder")
        add_layout.addWidget(self.folder_combo)
        
        add_folder_button = QPushButton("New Folder")
        add_folder_button.clicked.connect(self.add_folder)
        add_layout.addWidget(add_folder_button)
        
        # Add delete folder button
        delete_folder_button = QPushButton("Delete Folder")
        delete_folder_button.clicked.connect(self.delete_folder)
        add_layout.addWidget(delete_folder_button)
        
        add_layout.addWidget(add_button)
        
        layout.addLayout(add_layout)
        
        # Bookmarks table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Title", "URL", "Folder"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_bookmark)
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_bookmark)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        self.load_bookmarks()
        
    def get_browser_window(self, widget):
        """Find the main browser window instance"""
        while widget is not None:
            if hasattr(widget, 'update_bookmark_bar'):
                return widget
            widget = widget.parent()
        return None

    def load_bookmarks(self):
        try:
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
        except FileNotFoundError:
            bookmarks = {"folders": [], "bookmarks": []}
            
        # Update folder combo
        self.folder_combo.clear()
        self.folder_combo.addItem("No Folder")
        for folder in bookmarks.get("folders", []):
            self.folder_combo.addItem(folder["name"])
            
        # Load bookmarks
        bookmarks_list = bookmarks.get("bookmarks", [])
        self.table.setRowCount(len(bookmarks_list))
        for i, bookmark in enumerate(bookmarks_list):
            self.table.setItem(i, 0, QTableWidgetItem(bookmark["title"]))
            self.table.setItem(i, 1, QTableWidgetItem(bookmark["url"]))
            self.table.setItem(i, 2, QTableWidgetItem(bookmark.get("folder", "No Folder")))
            
    def save_bookmarks(self):
        bookmarks = {"folders": [], "bookmarks": []}
        
        # Save folders
        for i in range(self.folder_combo.count()):
            folder_name = self.folder_combo.itemText(i)
            if folder_name != "No Folder":
                bookmarks["folders"].append({"name": folder_name})
        
        # Save bookmarks
        for row in range(self.table.rowCount()):
            bookmark = {
                "title": self.table.item(row, 0).text(),
                "url": self.table.item(row, 1).text(),
                "folder": self.table.item(row, 2).text()
            }
            bookmarks["bookmarks"].append(bookmark)
            
        with open("browser_bookmarks.json", "w") as f:
            json.dump(bookmarks, f)
            
        # Update browser's bookmark bar if we have a reference
        if self.browser:
            self.browser.update_bookmark_bar()
            
    def add_folder(self):
        folder_name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and folder_name:
            self.folder_combo.addItem(folder_name)
            self.save_bookmarks()

    def delete_folder(self):
        folder_name = self.folder_combo.currentText()
        if folder_name != "No Folder":
            # Remove folder from combo box
            self.folder_combo.removeItem(self.folder_combo.currentIndex())
            
            # Update bookmarks in the table
            for row in range(self.table.rowCount()):
                if self.table.item(row, 2).text() == folder_name:
                    self.table.item(row, 2).setText("No Folder")
            
            self.save_bookmarks()

    def add_bookmark(self):
        title = self.title_input.text()
        url = self.url_input.text()
        folder = self.folder_combo.currentText()
        if title and url:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(title))
            self.table.setItem(row, 1, QTableWidgetItem(url))
            self.table.setItem(row, 2, QTableWidgetItem(folder))
            self.title_input.clear()
            self.url_input.clear()
            self.save_bookmarks()
            
    def edit_bookmark(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.title_input.setText(self.table.item(current_row, 0).text())
            self.url_input.setText(self.table.item(current_row, 1).text())
            self.table.removeRow(current_row)
            self.save_bookmarks()
            
    def delete_bookmark(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            self.save_bookmarks()

class BookmarkButton(QToolButton):
    def __init__(self, title, url, parent=None):
        super().__init__(parent)
        self.setText(title)
        self.url = url
        self.browser = self.get_browser_window(parent)

    def get_browser_window(self, widget):
        """Find the main browser window instance"""
        while widget is not None:
            if hasattr(widget, 'update_bookmark_bar'):
                return widget
            widget = widget.parent()
        return None

    def delete_bookmark(self):
        try:
            with open("browser_bookmarks.json", "r") as f:
                bookmarks = json.load(f)
            
            bookmarks["bookmarks"] = [b for b in bookmarks["bookmarks"] 
                                    if not (b["title"] == self.text() and b["url"] == self.url)]
            
            with open("browser_bookmarks.json", "w") as f:
                json.dump(bookmarks, f)
                
            if self.browser:
                self.browser.update_bookmark_bar()
        except Exception as e:
            print(f"Error deleting bookmark: {e}")
            
    def edit_bookmark(self):
        if self.browser:
            dialog = BookmarkManager(self.browser)
            dialog.title_input.setText(self.text())
            dialog.url_input.setText(self.url)
            dialog.exec_()
