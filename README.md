# Secure Browser

A privacy-focused web browser built with PyQt5, featuring built-in ad blocking, cookie management, and customizable security settings.

## Features

- 🛡️ Built-in ad blocker
- 🍪 Cookie management and control
- 🔒 JavaScript toggle support
- 📜 Browsing history management
- ⬇️ Download management
- 🎨 Multiple themes (Light, Dark, Dracula)
- 🏠 Customizable homepage
- 🔍 Choice of search engines (DuckDuckGo, Google, Bing)

## Requirements

- Python 3.x
- PyQt5
- PyQtWebEngine

## Installation

1. Install the required packages:
```bash
pip install PyQt5 PyQtWebEngine
```

2. Clone the repository:
```bash
git clone https://github.com/kabuky1/web-browser.git
cd secure-browser
```

3. Run the browser:
```bash
python main.py
```

## Usage

### Navigation
- Use the address bar to enter URLs
- Click the arrow buttons for back/forward navigation
- Use the reload button to refresh the page
- Click the hamburger menu (☰) for additional options

### Settings
Access settings through the hamburger menu (☰) to configure:
- Homepage
- Search engine preference
- Cookie settings
- JavaScript settings
- Theme selection
- Download path

### Privacy Features
- Ad blocking is enabled by default
- Cookies can be enabled/disabled in settings
- JavaScript can be enabled/disabled in settings
- History can be viewed and cleared

### Themes
Three built-in themes:
- Light
- Dark
- Dracula

## File Structure
```
secure-browser/
├── main.py          # Main browser implementation
├── settings.py      # Settings dialog and configuration
├── history.py       # History management
├── downloads.py     # Download management
├── about.py         # About dialog
├── themes.py        # Theme definitions and management
└── README.md        # Documentation
```


## License

This project is licensed under the MIT License - see the LICENSE file for details.