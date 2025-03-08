THEMES = {
    "dark": {
        "background": "#2b2b2b",
        "secondary": "#3b3b3b",
        "text": "#ffffff",
        "border": "#555555",
        "hover": "#4b4b4b"
    },
    "light": {
        "background": "#ffffff",
        "secondary": "#f0f0f0",
        "text": "#000000",
        "border": "#cccccc",
        "hover": "#e5e5e5"
    },
    "dracula": {
        "background": "#282a36",
        "secondary": "#44475a",
        "text": "#f8f8f2",
        "border": "#6272a4",
        "hover": "#bd93f9"
    }
}

def apply_theme(widget, theme_name):
    theme = THEMES.get(theme_name, THEMES["dark"])
    
    widget.setStyleSheet(f"""
        QMainWindow, QDialog, QTabWidget, QWidget {{
            background-color: {theme["background"]};
            color: {theme["text"]};
        }}
        QLineEdit, QComboBox {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
            padding: 5px;
        }}
        QPushButton {{
            background-color: {theme["secondary"]};
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
            padding: 5px 10px;
            margin: 2px;
        }}
        QPushButton:hover {{
            background-color: {theme["hover"]};
        }}
        QMenu {{
            background-color: {theme["background"]};
            color: {theme["text"]};
            border: 1px solid {theme["border"]};
        }}
        QMenu::item:selected {{
            background-color: {theme["hover"]};
        }}
        QLabel {{
            color: {theme["text"]};
        }}
        QCheckBox {{
            color: {theme["text"]};
        }}
    """)
