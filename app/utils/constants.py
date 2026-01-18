"""
Constants and definitions for filters, actions, and other settings.
"""

from typing import Dict, List, Any

# Filter definitions with their parameters and descriptions
FILTERS: Dict[str, Dict[str, Any]] = {
    "created": {
        "name": "Created Date",
        "description": "Filter by file creation date",
        "icon": "mdi.calendar-plus",
        "category": "date",
        "params": {
            "days": {"type": "int", "default": None, "description": "Days threshold"},
            "hours": {"type": "int", "default": None, "description": "Hours threshold"},
            "weeks": {"type": "int", "default": None, "description": "Weeks threshold"},
            "months": {"type": "int", "default": None, "description": "Months threshold"},
            "years": {"type": "int", "default": None, "description": "Years threshold"},
            "mode": {"type": "choice", "choices": ["older", "newer"], "default": "older"},
        },
        "supports": ["files", "dirs"],
    },
    "date_added": {
        "name": "Date Added",
        "description": "Filter by date file was added to folder (macOS)",
        "icon": "mdi.calendar-import",
        "category": "date",
        "params": {
            "days": {"type": "int", "default": None, "description": "Days threshold"},
            "hours": {"type": "int", "default": None, "description": "Hours threshold"},
            "mode": {"type": "choice", "choices": ["older", "newer"], "default": "older"},
        },
        "supports": ["files", "dirs"],
        "platform": "darwin",
    },
    "date_lastused": {
        "name": "Date Last Used",
        "description": "Filter by last access date (macOS)",
        "icon": "mdi.calendar-clock",
        "category": "date",
        "params": {
            "days": {"type": "int", "default": None, "description": "Days threshold"},
            "hours": {"type": "int", "default": None, "description": "Hours threshold"},
            "mode": {"type": "choice", "choices": ["older", "newer"], "default": "older"},
        },
        "supports": ["files", "dirs"],
        "platform": "darwin",
    },
    "duplicate": {
        "name": "Duplicate",
        "description": "Detect duplicate files",
        "icon": "mdi.content-duplicate",
        "category": "content",
        "params": {
            "detect_original_by": {
                "type": "choice",
                "choices": ["first_seen", "name", "created", "lastmodified"],
                "default": "first_seen",
                "description": "Method to detect the original file",
            },
        },
        "supports": ["files"],
    },
    "empty": {
        "name": "Empty",
        "description": "Filter empty files or folders",
        "icon": "mdi.folder-open-outline",
        "category": "content",
        "params": {},
        "supports": ["files", "dirs"],
    },
    "exif": {
        "name": "EXIF Data",
        "description": "Filter by image EXIF metadata",
        "icon": "mdi.camera",
        "category": "content",
        "params": {
            "filter_tags": {"type": "list", "default": [], "description": "EXIF tags to filter"},
        },
        "supports": ["files"],
    },
    "extension": {
        "name": "Extension",
        "description": "Filter by file extension",
        "icon": "mdi.file-document-outline",
        "category": "name",
        "params": {
            "extensions": {"type": "list", "default": [], "description": "File extensions to match"},
        },
        "supports": ["files"],
    },
    "filecontent": {
        "name": "File Content",
        "description": "Filter by text content in files (PDF, DOCX, etc.)",
        "icon": "mdi.file-search-outline",
        "category": "content",
        "params": {
            "pattern": {"type": "string", "default": "", "description": "Regex pattern to match"},
        },
        "supports": ["files"],
    },
    "hash": {
        "name": "Hash",
        "description": "Get file hash (MD5, SHA1, SHA256, etc.)",
        "icon": "mdi.pound",
        "category": "content",
        "params": {
            "algorithm": {
                "type": "choice",
                "choices": ["md5", "sha1", "sha256", "sha512"],
                "default": "md5",
            },
        },
        "supports": ["files"],
    },
    "lastmodified": {
        "name": "Last Modified",
        "description": "Filter by last modification date",
        "icon": "mdi.calendar-edit",
        "category": "date",
        "params": {
            "days": {"type": "int", "default": None, "description": "Days threshold"},
            "hours": {"type": "int", "default": None, "description": "Hours threshold"},
            "weeks": {"type": "int", "default": None, "description": "Weeks threshold"},
            "months": {"type": "int", "default": None, "description": "Months threshold"},
            "years": {"type": "int", "default": None, "description": "Years threshold"},
            "mode": {"type": "choice", "choices": ["older", "newer"], "default": "older"},
        },
        "supports": ["files", "dirs"],
    },
    "macos_tags": {
        "name": "macOS Tags",
        "description": "Filter by macOS Finder tags",
        "icon": "mdi.tag-outline",
        "category": "metadata",
        "params": {
            "tags": {"type": "list", "default": [], "description": "Tags to match"},
        },
        "supports": ["files", "dirs"],
        "platform": "darwin",
    },
    "mimetype": {
        "name": "MIME Type",
        "description": "Filter by file MIME type",
        "icon": "mdi.file-question-outline",
        "category": "content",
        "params": {
            "mimetype": {"type": "string", "default": "", "description": "MIME type to match"},
        },
        "supports": ["files"],
    },
    "name": {
        "name": "Name",
        "description": "Filter by filename",
        "icon": "mdi.form-textbox",
        "category": "name",
        "params": {
            "startswith": {"type": "string", "default": None},
            "endswith": {"type": "string", "default": None},
            "contains": {"type": "list", "default": []},
            "case_sensitive": {"type": "bool", "default": True},
        },
        "supports": ["files", "dirs"],
    },
    "python": {
        "name": "Python",
        "description": "Custom Python filter code",
        "icon": "mdi.language-python",
        "category": "advanced",
        "params": {
            "code": {"type": "text", "default": "", "description": "Python code to execute"},
        },
        "supports": ["files", "dirs"],
    },
    "regex": {
        "name": "Regex",
        "description": "Filter by regular expression",
        "icon": "mdi.regex",
        "category": "name",
        "params": {
            "pattern": {"type": "string", "default": "", "description": "Regular expression pattern"},
        },
        "supports": ["files", "dirs"],
    },
    "size": {
        "name": "Size",
        "description": "Filter by file size",
        "icon": "mdi.scale-balance",
        "category": "content",
        "params": {
            "condition": {"type": "string", "default": "", "description": "Size condition (e.g., '> 1 MB')"},
        },
        "supports": ["files", "dirs"],
    },
}

# Action definitions with their parameters and descriptions
ACTIONS: Dict[str, Dict[str, Any]] = {
    "confirm": {
        "name": "Confirm",
        "description": "Ask for confirmation before proceeding",
        "icon": "mdi.help-circle-outline",
        "category": "control",
        "params": {
            "msg": {"type": "string", "default": "Continue?", "description": "Confirmation message"},
            "default": {"type": "bool", "default": True, "description": "Default answer"},
        },
        "supports": ["files", "dirs"],
    },
    "copy": {
        "name": "Copy",
        "description": "Copy files to destination",
        "icon": "mdi.content-copy",
        "category": "file",
        "params": {
            "dest": {"type": "path", "default": "", "description": "Destination path"},
            "on_conflict": {
                "type": "choice",
                "choices": ["skip", "overwrite", "rename_new", "rename_existing", "deduplicate"],
                "default": "rename_new",
            },
            "rename_template": {"type": "string", "default": "{name} {counter}{extension}"},
        },
        "supports": ["files", "dirs"],
    },
    "delete": {
        "name": "Delete",
        "description": "Permanently delete files",
        "icon": "mdi.delete-forever",
        "category": "file",
        "params": {},
        "supports": ["files", "dirs"],
        "dangerous": True,
    },
    "echo": {
        "name": "Echo",
        "description": "Print a message",
        "icon": "mdi.message-text-outline",
        "category": "output",
        "params": {
            "msg": {"type": "string", "default": "{path}", "description": "Message to print"},
        },
        "supports": ["files", "dirs"],
    },
    "hardlink": {
        "name": "Hard Link",
        "description": "Create a hard link",
        "icon": "mdi.link-variant",
        "category": "file",
        "params": {
            "dest": {"type": "path", "default": "", "description": "Hard link destination"},
        },
        "supports": ["files"],
    },
    "macos_tags": {
        "name": "macOS Tags",
        "description": "Add macOS Finder tags",
        "icon": "mdi.tag-plus-outline",
        "category": "metadata",
        "params": {
            "tags": {"type": "list", "default": [], "description": "Tags to add"},
        },
        "supports": ["files", "dirs"],
        "platform": "darwin",
    },
    "move": {
        "name": "Move",
        "description": "Move files to destination",
        "icon": "mdi.folder-move-outline",
        "category": "file",
        "params": {
            "dest": {"type": "path", "default": "", "description": "Destination path"},
            "on_conflict": {
                "type": "choice",
                "choices": ["skip", "overwrite", "rename_new", "rename_existing", "deduplicate"],
                "default": "rename_new",
            },
            "rename_template": {"type": "string", "default": "{name} {counter}{extension}"},
        },
        "supports": ["files", "dirs"],
    },
    "python": {
        "name": "Python",
        "description": "Execute custom Python code",
        "icon": "mdi.language-python",
        "category": "advanced",
        "params": {
            "code": {"type": "text", "default": "", "description": "Python code to execute"},
            "run_in_simulation": {"type": "bool", "default": False},
        },
        "supports": ["files", "dirs"],
    },
    "rename": {
        "name": "Rename",
        "description": "Rename files",
        "icon": "mdi.form-textbox",
        "category": "file",
        "params": {
            "new_name": {"type": "string", "default": "", "description": "New filename template"},
            "on_conflict": {
                "type": "choice",
                "choices": ["skip", "overwrite", "rename_new", "rename_existing"],
                "default": "rename_new",
            },
        },
        "supports": ["files", "dirs"],
    },
    "shell": {
        "name": "Shell",
        "description": "Execute shell command",
        "icon": "mdi.console",
        "category": "advanced",
        "params": {
            "command": {"type": "string", "default": "", "description": "Shell command to execute"},
            "run_in_simulation": {"type": "bool", "default": False},
        },
        "supports": ["files", "dirs"],
    },
    "symlink": {
        "name": "Symbolic Link",
        "description": "Create a symbolic link",
        "icon": "mdi.link",
        "category": "file",
        "params": {
            "dest": {"type": "path", "default": "", "description": "Symlink destination"},
        },
        "supports": ["files", "dirs"],
    },
    "trash": {
        "name": "Trash",
        "description": "Move files to system trash",
        "icon": "mdi.delete-outline",
        "category": "file",
        "params": {},
        "supports": ["files", "dirs"],
    },
    "write": {
        "name": "Write",
        "description": "Write content to a file",
        "icon": "mdi.file-edit-outline",
        "category": "output",
        "params": {
            "outfile": {"type": "path", "default": "", "description": "Output file path"},
            "text": {"type": "string", "default": "", "description": "Text to write"},
            "mode": {"type": "choice", "choices": ["append", "prepend", "overwrite"], "default": "append"},
            "clear_before_first_write": {"type": "bool", "default": False},
        },
        "supports": ["files", "dirs"],
    },
}

# Filter modes for combining multiple filters
FILTER_MODES = {
    "all": {"name": "All (AND)", "description": "All filters must match"},
    "any": {"name": "Any (OR)", "description": "At least one filter must match"},
    "none": {"name": "None", "description": "No filter should match"},
}

# Conflict resolution modes
CONFLICT_MODES = {
    "skip": {"name": "Skip", "description": "Skip the file if destination exists"},
    "overwrite": {"name": "Overwrite", "description": "Overwrite the existing file"},
    "rename_new": {"name": "Rename New", "description": "Rename the new file with a counter"},
    "rename_existing": {"name": "Rename Existing", "description": "Rename the existing file"},
    "deduplicate": {"name": "Deduplicate", "description": "Skip if files are identical, rename otherwise"},
}

# Common file categories for quick filtering
FILE_CATEGORIES = {
    "images": {
        "name": "Images",
        "icon": "mdi.image",
        "extensions": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "ico", "tiff", "tif"],
    },
    "documents": {
        "name": "Documents",
        "icon": "mdi.file-document",
        "extensions": ["pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx"],
    },
    "audio": {
        "name": "Audio",
        "icon": "mdi.music",
        "extensions": ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"],
    },
    "video": {
        "name": "Video",
        "icon": "mdi.video",
        "extensions": ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v"],
    },
    "archives": {
        "name": "Archives",
        "icon": "mdi.folder-zip",
        "extensions": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz"],
    },
    "code": {
        "name": "Code",
        "icon": "mdi.code-braces",
        "extensions": ["py", "js", "ts", "html", "css", "java", "cpp", "c", "go", "rs", "rb"],
    },
}

# Placeholder variables available in templates
TEMPLATE_VARIABLES = {
    "path": "Full path to the current file/folder",
    "relative_path": "Relative path from location",
    "name": "Filename without extension",
    "extension": "File extension (with dot)",
    "env": "Environment variables dictionary",
    "now()": "Current datetime",
    "utcnow()": "Current UTC datetime",
    "today()": "Today's date",
    "created": "Creation datetime (if filter applied)",
    "lastmodified": "Last modified datetime (if filter applied)",
    "size": "File size object (if filter applied)",
    "hash": "File hash (if filter applied)",
    "duplicate.original": "Path to original file (if duplicate filter applied)",
    "exif": "EXIF data dictionary (if filter applied)",
    "regex": "Regex match groups (if filter applied)",
    "filecontent": "Content match groups (if filter applied)",
}
