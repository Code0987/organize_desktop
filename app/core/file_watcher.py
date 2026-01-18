"""
File system watcher for monitoring directories and config file changes.
Uses the watchdog library for cross-platform file system events.
"""

import threading
from pathlib import Path
from typing import Optional, Callable, Set, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum, auto

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
    DirCreatedEvent,
    DirDeletedEvent,
    DirModifiedEvent,
    DirMovedEvent,
)


class FileEventType(Enum):
    """Type of file system event."""
    CREATED = auto()
    MODIFIED = auto()
    DELETED = auto()
    MOVED = auto()


@dataclass
class FileEvent:
    """File system event data."""
    event_type: FileEventType
    path: Path
    is_directory: bool
    dest_path: Optional[Path] = None  # For move events
    
    def __str__(self) -> str:
        if self.event_type == FileEventType.MOVED:
            return f"{self.event_type.name}: {self.path} -> {self.dest_path}"
        return f"{self.event_type.name}: {self.path}"


class FileEventHandler(FileSystemEventHandler):
    """
    Handler for file system events.
    Converts watchdog events to FileEvent objects.
    """
    
    def __init__(
        self,
        on_event: Callable[[FileEvent], None],
        patterns: Optional[Set[str]] = None,
        ignore_patterns: Optional[Set[str]] = None,
        ignore_directories: bool = False,
    ):
        """
        Initialize the event handler.
        
        Args:
            on_event: Callback for file events
            patterns: File patterns to include (e.g., {'*.yaml', '*.yml'})
            ignore_patterns: File patterns to ignore
            ignore_directories: Whether to ignore directory events
        """
        super().__init__()
        self._on_event = on_event
        self._patterns = patterns or set()
        self._ignore_patterns = ignore_patterns or set()
        self._ignore_directories = ignore_directories
    
    def _should_process(self, path: str, is_directory: bool) -> bool:
        """Check if the event should be processed."""
        if is_directory and self._ignore_directories:
            return False
        
        if self._patterns:
            name = Path(path).name
            if not any(self._matches_pattern(name, p) for p in self._patterns):
                return False
        
        if self._ignore_patterns:
            name = Path(path).name
            if any(self._matches_pattern(name, p) for p in self._ignore_patterns):
                return False
        
        return True
    
    @staticmethod
    def _matches_pattern(name: str, pattern: str) -> bool:
        """Check if a name matches a glob pattern."""
        import fnmatch
        return fnmatch.fnmatch(name, pattern)
    
    def _emit_event(self, event_type: FileEventType, src_path: str, is_dir: bool, dest_path: Optional[str] = None):
        """Emit a file event."""
        if self._should_process(src_path, is_dir):
            event = FileEvent(
                event_type=event_type,
                path=Path(src_path),
                is_directory=is_dir,
                dest_path=Path(dest_path) if dest_path else None,
            )
            self._on_event(event)
    
    def on_created(self, event):
        is_dir = isinstance(event, DirCreatedEvent)
        self._emit_event(FileEventType.CREATED, event.src_path, is_dir)
    
    def on_modified(self, event):
        is_dir = isinstance(event, DirModifiedEvent)
        self._emit_event(FileEventType.MODIFIED, event.src_path, is_dir)
    
    def on_deleted(self, event):
        is_dir = isinstance(event, DirDeletedEvent)
        self._emit_event(FileEventType.DELETED, event.src_path, is_dir)
    
    def on_moved(self, event):
        is_dir = isinstance(event, DirMovedEvent)
        self._emit_event(FileEventType.MOVED, event.src_path, is_dir, event.dest_path)


@dataclass
class WatchedPath:
    """Information about a watched path."""
    path: Path
    recursive: bool = True
    patterns: Set[str] = field(default_factory=set)
    ignore_patterns: Set[str] = field(default_factory=set)
    ignore_directories: bool = False


class FileWatcher:
    """
    File system watcher for monitoring directories.
    
    Provides:
    - Multi-path watching
    - Pattern-based filtering
    - Event callbacks
    - Thread-safe operation
    """
    
    def __init__(self):
        """Initialize the file watcher."""
        self._observer: Optional[Observer] = None
        self._watches: Dict[str, Any] = {}
        self._watched_paths: Dict[str, WatchedPath] = {}
        self._lock = threading.Lock()
        
        # Callbacks
        self._on_event: Optional[Callable[[FileEvent], None]] = None
        self._on_error: Optional[Callable[[Exception], None]] = None
    
    @property
    def is_running(self) -> bool:
        """Check if the watcher is running."""
        return self._observer is not None and self._observer.is_alive()
    
    @property
    def watched_paths(self) -> List[Path]:
        """Get list of watched paths."""
        return [wp.path for wp in self._watched_paths.values()]
    
    def set_callbacks(
        self,
        on_event: Optional[Callable[[FileEvent], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """
        Set callback functions.
        
        Args:
            on_event: Called for each file event
            on_error: Called when an error occurs
        """
        self._on_event = on_event
        self._on_error = on_error
    
    def start(self) -> bool:
        """
        Start the file watcher.
        
        Returns:
            True if started successfully
        """
        with self._lock:
            if self.is_running:
                return True
            
            try:
                self._observer = Observer()
                self._observer.start()
                
                # Re-add existing watches
                for key, watched in self._watched_paths.items():
                    self._add_watch_impl(watched)
                
                return True
            except Exception as e:
                if self._on_error:
                    self._on_error(e)
                return False
    
    def stop(self) -> None:
        """Stop the file watcher."""
        with self._lock:
            if self._observer:
                self._observer.stop()
                self._observer.join(timeout=5)
                self._observer = None
                self._watches.clear()
    
    def add_path(
        self,
        path: Path,
        recursive: bool = True,
        patterns: Optional[Set[str]] = None,
        ignore_patterns: Optional[Set[str]] = None,
        ignore_directories: bool = False,
    ) -> bool:
        """
        Add a path to watch.
        
        Args:
            path: Directory path to watch
            recursive: Whether to watch subdirectories
            patterns: File patterns to include
            ignore_patterns: File patterns to ignore
            ignore_directories: Whether to ignore directory events
            
        Returns:
            True if added successfully
        """
        path = Path(path).resolve()
        if not path.exists() or not path.is_dir():
            return False
        
        key = str(path)
        
        with self._lock:
            watched = WatchedPath(
                path=path,
                recursive=recursive,
                patterns=patterns or set(),
                ignore_patterns=ignore_patterns or set(),
                ignore_directories=ignore_directories,
            )
            self._watched_paths[key] = watched
            
            if self.is_running:
                return self._add_watch_impl(watched)
            
            return True
    
    def _add_watch_impl(self, watched: WatchedPath) -> bool:
        """Internal method to add a watch."""
        try:
            handler = FileEventHandler(
                on_event=self._handle_event,
                patterns=watched.patterns,
                ignore_patterns=watched.ignore_patterns,
                ignore_directories=watched.ignore_directories,
            )
            
            watch = self._observer.schedule(
                handler,
                str(watched.path),
                recursive=watched.recursive,
            )
            
            self._watches[str(watched.path)] = watch
            return True
            
        except Exception as e:
            if self._on_error:
                self._on_error(e)
            return False
    
    def remove_path(self, path: Path) -> bool:
        """
        Remove a watched path.
        
        Args:
            path: Path to stop watching
            
        Returns:
            True if removed successfully
        """
        key = str(Path(path).resolve())
        
        with self._lock:
            if key not in self._watched_paths:
                return False
            
            del self._watched_paths[key]
            
            if key in self._watches and self._observer:
                try:
                    self._observer.unschedule(self._watches[key])
                    del self._watches[key]
                except Exception:
                    pass
            
            return True
    
    def clear(self) -> None:
        """Remove all watched paths."""
        with self._lock:
            paths = list(self._watched_paths.keys())
        
        for path in paths:
            self.remove_path(Path(path))
    
    def _handle_event(self, event: FileEvent) -> None:
        """Handle a file event."""
        if self._on_event:
            try:
                self._on_event(event)
            except Exception as e:
                if self._on_error:
                    self._on_error(e)


class ConfigFileWatcher(FileWatcher):
    """
    Specialized watcher for organize configuration files.
    Watches for changes to YAML config files.
    """
    
    def __init__(self):
        """Initialize the config file watcher."""
        super().__init__()
        self._config_path: Optional[Path] = None
        self._on_config_changed: Optional[Callable[[Path], None]] = None
    
    def set_config_callback(self, callback: Callable[[Path], None]) -> None:
        """Set callback for config file changes."""
        self._on_config_changed = callback
    
    def watch_config(self, config_path: Path) -> bool:
        """
        Start watching a config file.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            True if started successfully
        """
        config_path = Path(config_path).resolve()
        
        # Stop watching previous config
        if self._config_path:
            self.remove_path(self._config_path.parent)
        
        self._config_path = config_path
        
        # Set up event handler
        def on_event(event: FileEvent):
            if event.path == self._config_path:
                if event.event_type in (FileEventType.MODIFIED, FileEventType.CREATED):
                    if self._on_config_changed:
                        self._on_config_changed(event.path)
        
        self.set_callbacks(on_event=on_event)
        
        # Watch the config file's directory
        return self.add_path(
            config_path.parent,
            recursive=False,
            patterns={"*.yaml", "*.yml"},
        )
    
    def unwatch_config(self) -> None:
        """Stop watching the config file."""
        if self._config_path:
            self.remove_path(self._config_path.parent)
            self._config_path = None
