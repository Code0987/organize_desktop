# Organize Desktop User Guide

Welcome to Organize Desktop! This guide will help you get started with automating your file organization tasks.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Creating Rules](#creating-rules)
4. [Working with Locations](#working-with-locations)
5. [Using Filters](#using-filters)
6. [Applying Actions](#applying-actions)
7. [Running and Simulating](#running-and-simulating)
8. [Working with the YAML Editor](#working-with-the-yaml-editor)
9. [Tips and Best Practices](#tips-and-best-practices)

---

## Getting Started

### First Launch

When you first launch Organize Desktop, you'll see the main window with:
- A sidebar showing available configuration files
- The rule editor (visual mode by default)
- The output log at the bottom

### Creating Your First Rule

1. Click the **"Add Rule"** button in the toolbar or use `Ctrl+R`
2. Give your rule a descriptive name
3. Add at least one location to search
4. Add filters to match specific files
5. Add actions to perform on matching files
6. Click **OK** to save the rule

### Testing Your Rule

Before running rules on your actual files:
1. Click **Simulate** (or press `F5`)
2. Review the output log to see what would happen
3. Make adjustments if needed
4. When satisfied, click **Run** (or press `F6`)

---

## Understanding the Interface

### Main Window Layout

```
┌──────────────────────────────────────────────────────────────┐
│                        TOOLBAR                                │
├────────────────┬─────────────────────────────────────────────┤
│                │                                              │
│    SIDEBAR     │              EDITOR AREA                     │
│                │     (Visual Editor or YAML Editor)           │
│  Config list   │                                              │
│                │                                              │
│                │                                              │
├────────────────┴─────────────────────────────────────────────┤
│                       OUTPUT LOG                              │
└──────────────────────────────────────────────────────────────┘
```

### Toolbar Buttons

| Button | Description |
|--------|-------------|
| 📄+ | Create new configuration |
| 📂 | Open existing configuration |
| 💾 | Save current configuration |
| ➕ | Add new rule |
| 🧪 | Simulate (dry run) |
| ▶️ | Run rules |
| ⏹️ | Stop execution |
| ⚙️ | Open settings |

### Sidebar

The sidebar shows all available configuration files found in the default locations. Double-click a config to open it.

### Status Bar

The status bar at the bottom shows:
- Current status message
- Loaded configuration name
- Execution state

---

## Creating Rules

### Rule Components

Every rule consists of:

1. **Name** (optional): A descriptive name for the rule
2. **Locations**: Folders to search for files
3. **Filters**: Conditions that files must match
4. **Actions**: What to do with matching files

### Rule Options

| Option | Description |
|--------|-------------|
| **Enabled** | Toggle to enable/disable the rule |
| **Targets** | `files` or `dirs` - what to match |
| **Subfolders** | Include subdirectories in search |
| **Filter Mode** | How to combine multiple filters |
| **Tags** | Labels for organizing and selecting rules |

### Filter Modes

- **All (AND)**: All filters must match
- **Any (OR)**: At least one filter must match  
- **None**: No filters should match (inverts all)

---

## Working with Locations

### Adding Locations

1. In the rule editor, go to the **Locations** tab
2. Click **Add Location**
3. Select a folder using the file browser
4. The location is added to the list

### Location Options

When using the YAML editor, you can specify options:

```yaml
locations:
  - path: ~/Downloads
    max_depth: 3
    exclude_files:
      - "*.tmp"
    exclude_dirs:
      - .git
```

### Common Location Patterns

| Pattern | Description |
|---------|-------------|
| `~/Downloads` | User's Downloads folder |
| `~/Desktop` | User's Desktop |
| `~/Documents` | User's Documents |
| `{env.MY_VAR}` | Environment variable path |

---

## Using Filters

### Basic Filters

#### Extension Filter
Match files by their extension:
```yaml
filters:
  - extension: pdf
  - extension:
      - jpg
      - jpeg
      - png
```

#### Name Filter
Match files by name patterns:
```yaml
filters:
  - name:
      startswith: Invoice
      contains: 2024
      case_sensitive: false
```

#### Size Filter
Match files by size:
```yaml
filters:
  - size: "> 10 MB"
  - size: "< 100 KB"
  - size: ">1gb, <5gb"
```

### Date Filters

#### Created Date
```yaml
filters:
  - created:
      days: 30
      mode: older  # or "newer"
```

#### Last Modified
```yaml
filters:
  - lastmodified:
      days: 7
      mode: newer
```

### Content Filters

#### Duplicate Detection
```yaml
filters:
  - duplicate:
      detect_original_by: first_seen
```

#### File Content (PDF, DOCX, etc.)
```yaml
filters:
  - filecontent: "Invoice.*(?P<number>\d+)"
```

### Advanced Filters

#### Regular Expression
```yaml
filters:
  - regex: '^IMG_\d{4}\.jpg$'
```

#### Python Code
```yaml
filters:
  - python: |
      return path.stat().st_size > 1000000
```

### Excluding Filters

Prefix any filter with `not` to invert it:
```yaml
filters:
  - not extension: tmp
  - not empty
```

---

## Applying Actions

### File Operations

#### Move Files
```yaml
actions:
  - move: ~/Sorted/{extension.upper()}/
  - move:
      dest: ~/Documents/
      on_conflict: rename_new
```

#### Copy Files
```yaml
actions:
  - copy: ~/Backup/
  - copy:
      dest: ~/Archive/{created.year}/
      on_conflict: skip
```

#### Rename Files
```yaml
actions:
  - rename: "{name.lower()}{extension}"
  - rename: "backup_{name}{extension}"
```

#### Delete/Trash
```yaml
actions:
  - trash  # Moves to system trash (recoverable)
  - delete # Permanent deletion (use with caution!)
```

### Output Actions

#### Echo (Print Message)
```yaml
actions:
  - echo: "Found: {path.name}"
  - echo: "Size: {size.decimal}"
```

#### Write to File
```yaml
actions:
  - write:
      outfile: "./log.txt"
      text: "{path} - {size.decimal}"
      mode: append
```

### Advanced Actions

#### Shell Command
```yaml
actions:
  - shell: 'open "{path}"'  # macOS
  - shell: 'start "" "{path}"'  # Windows
```

#### Python Code
```yaml
actions:
  - python: |
      import webbrowser
      webbrowser.open(f'https://www.google.com/search?q={path.stem}')
```

### Conflict Resolution

When a file already exists at the destination:

| Mode | Description |
|------|-------------|
| `skip` | Don't move/copy the file |
| `overwrite` | Replace the existing file |
| `rename_new` | Add a counter to the new file |
| `rename_existing` | Add a counter to the existing file |
| `deduplicate` | Skip if identical, rename if different |

---

## Running and Simulating

### Simulation Mode (F5)

Simulation shows what would happen without modifying files:
- Safe to run multiple times
- Preview all changes before applying
- Look for errors or unexpected behavior

### Run Mode (F6)

Actually performs the file operations:
- Always simulate first!
- Creates backups when possible
- Can be cancelled with Stop (Shift+F5)

### Understanding the Log

The output log shows:
- ✓ (green): Successful operation
- ⚠ (yellow): Warning
- ✗ (red): Error
- ℹ (gray): Information

### Filtering the Log

Use the filter dropdown to show only:
- All messages
- Info only
- Errors only
- Warnings only

---

## Working with the YAML Editor

### Switching Views

Click **YAML Editor** tab to switch from visual mode.

### Syntax Highlighting

The editor highlights:
- **Keys** (blue)
- **Strings** (green)
- **Numbers** (orange)
- **Comments** (gray)
- **Template variables** (cyan)

### Validation

The editor validates your YAML in real-time:
- ✓ Green checkmark = valid
- ✗ Red X = error (with location)

### Template Variables

Use these variables in actions:

| Variable | Description |
|----------|-------------|
| `{path}` | Full file path |
| `{path.name}` | Filename with extension |
| `{path.stem}` | Filename without extension |
| `{extension}` | File extension |
| `{relative_path}` | Path relative to location |
| `{now()}` | Current datetime |
| `{created}` | Creation date (with filter) |
| `{size}` | File size (with filter) |

---

## Tips and Best Practices

### Start Small
- Begin with simple rules
- Test with simulation
- Gradually add complexity

### Use Descriptive Names
```yaml
rules:
  - name: "Sort downloaded PDFs by month"
    # ...
```

### Backup Important Files
Before running on important files:
1. Create a backup
2. Test on a small subset
3. Use simulation mode

### Organize Your Rules
Use tags to group related rules:
```yaml
rules:
  - name: Photo rule
    tags:
      - photos
      - media
```

### Common Use Cases

#### Clean Downloads Folder
```yaml
rules:
  - name: Sort downloads by type
    locations: ~/Downloads
    filters:
      - extension:
          - pdf
          - doc
          - docx
    actions:
      - move: ~/Documents/Downloads/
```

#### Archive Old Files
```yaml
rules:
  - name: Archive files older than 1 year
    locations:
      - path: ~/Documents
        max_depth: null
    filters:
      - lastmodified:
          years: 1
          mode: older
    actions:
      - move: ~/Archive/{lastmodified.year}/
```

#### Remove Duplicates
```yaml
rules:
  - name: Find and remove duplicate files
    locations:
      - ~/Downloads
      - ~/Desktop
    subfolders: true
    filters:
      - duplicate
    actions:
      - trash
```

#### Organize Photos by Date
```yaml
rules:
  - name: Sort photos by date taken
    locations: ~/Pictures
    subfolders: true
    filters:
      - extension:
          - jpg
          - jpeg
          - png
      - exif
    actions:
      - move: "~/Pictures/Sorted/{exif.image.datetime.year}/{exif.image.datetime.month:02d}/"
```

---

## Troubleshooting

### Rule Not Matching Files

1. Check location path is correct
2. Verify filters aren't too restrictive
3. Try with `subfolders: true`
4. Check file permissions

### Action Failed

1. Check destination path exists
2. Verify write permissions
3. Check for path conflicts
4. Review error message in log

### Configuration Won't Load

1. Check YAML syntax (look for red X)
2. Verify indentation (use spaces, not tabs)
3. Check for missing colons or quotes

---

For more help, visit the [organize documentation](https://organize.readthedocs.io).
