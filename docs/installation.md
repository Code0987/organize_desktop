# Installation Guide

This guide covers installation of Organize Desktop on different platforms.

## Requirements

- Python 3.9 or higher
- pip (Python package manager)
- An operating system: Windows, macOS, or Linux

## Quick Install

The fastest way to install:

```bash
pip install organize-desktop
```

## Platform-Specific Instructions

### Windows

1. **Install Python**
   - Download from [python.org](https://python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Restart your terminal after installation

2. **Install Organize Desktop**
   ```cmd
   pip install organize-desktop
   ```

3. **Run the application**
   ```cmd
   organize-desktop
   ```

### macOS

1. **Install Python** (if not already installed)
   ```bash
   # Using Homebrew
   brew install python@3.11
   
   # Or download from python.org
   ```

2. **Install Organize Desktop**
   ```bash
   pip3 install organize-desktop
   ```

3. **Run the application**
   ```bash
   organize-desktop
   ```

### Linux

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Create a virtual environment (recommended)
python3 -m venv ~/.venvs/organize-desktop
source ~/.venvs/organize-desktop/bin/activate

# Install Organize Desktop
pip install organize-desktop

# Run the application
organize-desktop
```

#### Fedora
```bash
sudo dnf install python3 python3-pip
pip install organize-desktop
```

#### Arch Linux
```bash
sudo pacman -S python python-pip
pip install organize-desktop
```

## Install from Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/your-username/organize-desktop.git
cd organize-desktop

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Run
organize-desktop
```

## Installing with Optional Dependencies

### For better icon support
```bash
pip install organize-desktop[icons]
```

### For development
```bash
pip install organize-desktop[dev]
```

## Verifying Installation

After installation, verify everything works:

```bash
# Check the version
organize-desktop --version

# Or start the application
organize-desktop
```

## Updating

To update to the latest version:

```bash
pip install --upgrade organize-desktop
```

## Uninstalling

To remove Organize Desktop:

```bash
pip uninstall organize-desktop
```

Settings and configurations are stored in:
- Windows: `%APPDATA%\organize-desktop\`
- macOS: `~/Library/Application Support/organize-desktop/`
- Linux: `~/.config/organize-desktop/`

Delete these folders to remove all settings.

## Troubleshooting

### "Command not found" error

Make sure Python scripts are in your PATH:

**Windows:**
```cmd
# Add to PATH or run:
python -m app.main
```

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"
```

### Permission errors

Try installing for the current user only:
```bash
pip install --user organize-desktop
```

### PyQt6 issues

If you have Qt installation issues:

**Ubuntu/Debian:**
```bash
sudo apt install python3-pyqt6
```

**Fedora:**
```bash
sudo dnf install python3-qt6
```

### Missing icons

Install the icon package:
```bash
pip install qtawesome
```

## Getting Help

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/your-username/organize-desktop/issues)
2. Search existing issues for solutions
3. Open a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Error messages
   - Steps to reproduce
