# Organize Desktop

<p align="center">
  <img width="128" height="128" alt="Organize Desktop Logo" src="resources/icon.png">
</p>

<p align="center">
  <b>A modern desktop application for file management automation</b>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Overview

Organize Desktop is a user-friendly graphical interface for the [organize](https://github.com/tfeldmann/organize) file management automation tool. It provides an intuitive way to create, manage, and execute file organization rules without writing YAML configuration files manually.

## Features

### 🎨 Modern User Interface
- Beautiful dark and light themes
- Responsive design that works on all screen sizes
- Intuitive navigation with sidebar and tabbed editor

### 📝 Visual Rule Editor
- Create rules with drag-and-drop simplicity
- Add locations, filters, and actions using dropdown menus
- Preview changes before executing

### 💻 Advanced YAML Editor
- Syntax highlighting for YAML configuration
- Line numbers and bracket matching
- Real-time validation with error highlighting

### ⚡ Execution Engine
- Run simulations to preview changes (dry run)
- Execute rules with real-time progress feedback
- Detailed logging with filtering and search

### 🔧 Customizable Settings
- Personalize themes and fonts
- Configure auto-save and editor preferences
- Set default working directories

### 🌍 Cross-Platform
- Native support for Windows, macOS, and Linux
- Consistent experience across all platforms
- Uses native file dialogs and notifications

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Install from Source

```bash
# Clone this repository
git clone https://github.com/your-username/organize-desktop.git
cd organize-desktop

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Run the application
organize-desktop
```

### Dependencies

The application automatically installs the following dependencies:

- **organize-tool** (>=3.3.0): The core file management automation library
- **PyQt6** (>=6.6.0): Cross-platform GUI framework
- **PyYAML** (>=6.0): YAML parsing and generation
- **platformdirs** (>=4.0.0): Platform-specific directories
- **watchdog** (>=3.0.0): File system monitoring
- **qtawesome** (>=1.3.0): Icon library for Qt

## Usage

### Starting the Application

```bash
# Start from command line
organize-desktop

# Or use Python
python -m app.main
```

### Creating Your First Rule

1. **Open the application** - The main window shows the rule editor
2. **Click "Add Rule"** - A dialog opens for creating a new rule
3. **Add a location** - Click "Add Location" and select a folder to organize
4. **Add filters** - Choose filters like "extension", "size", or "created"
5. **Add actions** - Select actions like "move", "copy", or "rename"
6. **Save the rule** - Click OK to add the rule to your configuration

### Running Rules

- **Simulate (F5)**: Preview changes without modifying files
- **Run (F6)**: Execute rules and modify files
- **Stop (Shift+F5)**: Cancel execution

### Switching Between Editors

- **Visual Editor**: Create and edit rules using a graphical interface
- **YAML Editor**: View and modify the raw YAML configuration

## Screenshots

### Main Window (Dark Theme)
```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  Run  View  Help                      [⚙️ Settings]  │
├─────────────────────────────────────────────────────────────────┤
│ Configs     │  [Visual Editor] [YAML Editor]        config.yaml │
│ ─────────── │ ┌───────────────────────────────────────────────┐ │
│ ☰ config    │ │ ┌─────────────────────────────────────────┐   │ │
│ ☰ backup    │ │ │ ✓ Sort Downloads                        │   │ │
│ ☰ photos    │ │ │   📁 1 location  🔍 2 filters  ⚡ 1 action │   │ │
│             │ │ │   [Edit] [↑] [↓] [🗑️]                    │   │ │
│             │ │ └─────────────────────────────────────────┘   │ │
│             │ │                                               │ │
│             │ │ ┌─────────────────────────────────────────┐   │ │
│             │ │ │ ✓ Archive Old Files                     │   │ │
│             │ │ │   📁 2 locations  🔍 1 filter  ⚡ 2 actions│   │ │
│ [New Config]│ │ │   [Edit] [↑] [↓] [🗑️]                    │   │ │
│ [Open Folder│ │ └─────────────────────────────────────────┘   │ │
├─────────────┴─┴───────────────────────────────────────────────┤
│ Output                                     [Filter ▼] [🔍    ] │
│ ──────────────────────────────────────────────────────────────│
│ [12:30:15] ✓ Moved file.pdf to ~/Documents/PDF/               │
│ [12:30:15] ✓ Moved report.docx to ~/Documents/Word/           │
│ ──────────────────────────────────────────────────────────────│
│ Ready                      │ config.yaml │ Idle    2 entries  │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration

### Settings Location

Settings are stored in platform-specific locations:

- **Windows**: `%APPDATA%\organize-desktop\settings.json`
- **macOS**: `~/Library/Application Support/organize-desktop/settings.json`
- **Linux**: `~/.config/organize-desktop/settings.json`

### Config Files Location

Organize configuration files are stored in:

- **Windows**: `%APPDATA%\organize\`
- **macOS**: `~/Library/Application Support/organize/`
- **Linux**: `~/.config/organize/`

## Available Filters

| Filter | Description |
|--------|-------------|
| `created` | Filter by file creation date |
| `date_added` | Filter by date added (macOS) |
| `date_lastused` | Filter by last access date (macOS) |
| `duplicate` | Detect duplicate files |
| `empty` | Filter empty files/folders |
| `exif` | Filter by image EXIF metadata |
| `extension` | Filter by file extension |
| `filecontent` | Filter by text content (PDF, DOCX) |
| `hash` | Get file hash |
| `lastmodified` | Filter by modification date |
| `macos_tags` | Filter by macOS Finder tags |
| `mimetype` | Filter by MIME type |
| `name` | Filter by filename |
| `python` | Custom Python filter |
| `regex` | Regular expression filter |
| `size` | Filter by file size |

## Available Actions

| Action | Description |
|--------|-------------|
| `confirm` | Ask for confirmation |
| `copy` | Copy files to destination |
| `delete` | Permanently delete files |
| `echo` | Print a message |
| `hardlink` | Create hard links |
| `macos_tags` | Add macOS Finder tags |
| `move` | Move files to destination |
| `python` | Execute custom Python code |
| `rename` | Rename files |
| `shell` | Execute shell commands |
| `symlink` | Create symbolic links |
| `trash` | Move to system trash |
| `write` | Write content to file |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New configuration |
| `Ctrl+O` | Open configuration |
| `Ctrl+S` | Save configuration |
| `Ctrl+Shift+S` | Save configuration as |
| `Ctrl+R` | Add new rule |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `F5` | Simulate (dry run) |
| `F6` | Run |
| `Shift+F5` | Stop execution |
| `Ctrl+L` | Toggle log panel |
| `Ctrl+,` | Open settings |
| `F1` | Open documentation |

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/organize-desktop.git
cd organize-desktop

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy app
```

### Project Structure

```
organize_desktop/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py               # Application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config_manager.py # Configuration file management
│   │   ├── file_watcher.py   # File system monitoring
│   │   ├── rule_engine.py    # Rule execution engine
│   │   └── settings.py       # Application settings
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py    # Main application window
│   │   ├── rule_editor.py    # Visual rule editor
│   │   ├── config_editor.py  # YAML code editor
│   │   ├── log_viewer.py     # Execution log viewer
│   │   ├── settings_dialog.py# Settings dialog
│   │   └── styles.py         # Theme and styling
│   └── utils/
│       ├── __init__.py
│       ├── constants.py      # Filter and action definitions
│       └── helpers.py        # Utility functions
├── resources/
│   └── icon.png              # Application icon
├── tests/
│   └── ...                   # Test files
├── docs/
│   └── ...                   # Documentation
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

**Q: The application doesn't start**
- Ensure Python 3.9+ is installed
- Check that all dependencies are installed: `pip install -e .`
- Try running with: `python -m app.main`

**Q: Cannot see icons in the interface**
- Install qtawesome: `pip install qtawesome`
- The application will work without icons but look better with them

**Q: Configuration not saving**
- Check write permissions to the config directory
- Try running as administrator/sudo (not recommended for regular use)

**Q: Rules not executing**
- Verify the config is valid (check for green checkmark)
- Try simulation first (F5) to see what would happen
- Check the log for error messages

### Getting Help

- Open an issue on GitHub
- Check the [organize documentation](https://organize.readthedocs.io)
- Join the discussion on GitHub Discussions

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public functions
- Add tests for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [organize](https://github.com/tfeldmann/organize) - The underlying file management automation tool
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Cross-platform GUI framework
- [QtAwesome](https://github.com/spyder-ide/qtawesome) - Icon library

---

<p align="center">
  Made with ❤️ for file organization enthusiasts
</p>
