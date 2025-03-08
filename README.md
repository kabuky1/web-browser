# Secure Browser

A privacy-focused web browser built with PyQt5, featuring built-in ad blocking, cookie management, smart search, and customizable security settings.

## Features

- 🛡️ Built-in ad blocker and tracker prevention
- 🍪 Intelligent cookie management (blocks third-party cookies)
- 🔒 JavaScript toggle support
- 📜 Browsing history management
- ⬇️ Download management
- 🎨 Multiple themes (Light, Dark, Dracula)
- 🏠 Customizable homepage
- 🔍 Smart address bar with search engine integration
- 📚 Advanced bookmark management
  - Folder organization
  - Drag-and-drop support
  - Context menus
  - Bookmark bar toggle

## Smart Navigation

- Direct URL navigation for valid web addresses
- Automatic search using your preferred search engine
- Supports DuckDuckGo, Google, and Bing
- Intelligent URL detection

## Privacy Features

- Blocks tracking cookies automatically
- Third-party cookie blocking
- Ad and tracker blocking
- Cookie counter in status bar
- Quick cookie clearing
- JavaScript can be disabled globally

## Bookmark Features

- Organize bookmarks in folders
- Drag-and-drop support
- Right-click context menus
- Toggle bookmark bar visibility
- Quick bookmark current page
- Import/export bookmarks

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
git clone https://github.com/yourusername/secure-browser.git
cd secure-browser
```

3. Run the browser:
```bash
python main.py
```

## Usage

### Navigation
- Use the address bar to enter URLs or search terms
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

### Bookmarks
- Use the bookmark manager to organize bookmarks
- Create folders for better organization
- Right-click bookmarks for quick actions
- Toggle bookmark bar visibility

## File Structure
```
secure-browser/
├── main.py          # Main browser implementation
├── settings.py      # Settings dialog and configuration
├── history.py       # History management
├── downloads.py     # Download management
├── bookmarks.py     # Bookmark management
├── about.py         # About dialog
├── themes.py        # Theme definitions and management
└── README.md        # Documentation
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.