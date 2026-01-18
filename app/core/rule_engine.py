"""
Rule execution engine that interfaces with the organize library.
Provides asynchronous execution with progress reporting and logging.
"""

import os
import sys
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Set, Callable, List, Dict, Any
from enum import Enum, auto

from organize import Config
from organize.output import Output
from organize.resource import Resource


class ExecutionStatus(Enum):
    """Execution status enumeration."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    STOPPING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class LogEntry:
    """Log entry for execution output."""
    timestamp: datetime
    level: str  # info, warning, error, success, debug
    message: str
    rule_name: Optional[str] = None
    file_path: Optional[str] = None
    action_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "rule_name": self.rule_name,
            "file_path": self.file_path,
            "action_name": self.action_name,
        }


@dataclass
class ExecutionResult:
    """Result of an execution run."""
    success_count: int = 0
    error_count: int = 0
    skipped_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logs: List[LogEntry] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Get execution duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def total_processed(self) -> int:
        """Get total number of processed items."""
        return self.success_count + self.error_count + self.skipped_count


class GuiOutput(Output):
    """
    Custom output handler for the GUI application.
    Captures organize output and sends it to the GUI via callbacks.
    """
    
    def __init__(
        self,
        on_msg: Optional[Callable[[LogEntry], None]] = None,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
    ):
        """
        Initialize GUI output handler.
        
        Args:
            on_msg: Callback for log messages
            on_progress: Callback for progress updates (rule_name, current, total)
        """
        self._on_msg = on_msg
        self._on_progress = on_progress
        self._simulate = False
        self._current_rule = ""
        self._processed = 0
    
    def start(
        self,
        simulate: bool,
        config_path: Optional[Path],
        working_dir: Path,
    ) -> None:
        """Called when execution starts."""
        self._simulate = simulate
        mode = "Simulating" if simulate else "Running"
        self._log("info", f"{mode} organize rules...")
        if config_path:
            self._log("debug", f"Config: {config_path}")
        self._log("debug", f"Working directory: {working_dir}")
    
    def end(self, success: int, errors: int) -> None:
        """Called when execution ends."""
        self._log(
            "success" if errors == 0 else "warning",
            f"Completed: {success} successful, {errors} errors"
        )
    
    def msg(
        self,
        res: Resource,
        msg: str,
        level: str = "info",
        sender: Any = None,
    ) -> None:
        """Called for each log message."""
        file_path = str(res.path) if res.path else None
        action_name = sender.action_config.name if sender and hasattr(sender, "action_config") else None
        rule_name = res.rule.name if res.rule and hasattr(res.rule, "name") else None
        
        self._log(
            level,
            msg,
            rule_name=rule_name,
            file_path=file_path,
            action_name=action_name,
        )
    
    def _log(
        self,
        level: str,
        message: str,
        rule_name: Optional[str] = None,
        file_path: Optional[str] = None,
        action_name: Optional[str] = None,
    ) -> None:
        """Create and emit a log entry."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            rule_name=rule_name,
            file_path=file_path,
            action_name=action_name,
        )
        
        if self._on_msg:
            self._on_msg(entry)


class RuleEngine:
    """
    Engine for executing organize rules.
    
    Provides:
    - Asynchronous execution in a separate thread
    - Progress reporting
    - Cancellation support
    - Log collection
    """
    
    def __init__(self):
        """Initialize the rule engine."""
        self._status = ExecutionStatus.IDLE
        self._thread: Optional[threading.Thread] = None
        self._cancel_event = threading.Event()
        self._result = ExecutionResult()
        self._logs: List[LogEntry] = []
        
        # Callbacks
        self._on_status_change: Optional[Callable[[ExecutionStatus], None]] = None
        self._on_log: Optional[Callable[[LogEntry], None]] = None
        self._on_progress: Optional[Callable[[str, int, int], None]] = None
        self._on_complete: Optional[Callable[[ExecutionResult], None]] = None
    
    @property
    def status(self) -> ExecutionStatus:
        """Get the current execution status."""
        return self._status
    
    @property
    def is_running(self) -> bool:
        """Check if execution is in progress."""
        return self._status in (ExecutionStatus.RUNNING, ExecutionStatus.PAUSED)
    
    @property
    def result(self) -> ExecutionResult:
        """Get the last execution result."""
        return self._result
    
    @property
    def logs(self) -> List[LogEntry]:
        """Get all log entries."""
        return self._logs
    
    def set_callbacks(
        self,
        on_status_change: Optional[Callable[[ExecutionStatus], None]] = None,
        on_log: Optional[Callable[[LogEntry], None]] = None,
        on_progress: Optional[Callable[[str, int, int], None]] = None,
        on_complete: Optional[Callable[[ExecutionResult], None]] = None,
    ) -> None:
        """
        Set callback functions.
        
        Args:
            on_status_change: Called when status changes
            on_log: Called for each log entry
            on_progress: Called for progress updates
            on_complete: Called when execution completes
        """
        self._on_status_change = on_status_change
        self._on_log = on_log
        self._on_progress = on_progress
        self._on_complete = on_complete
    
    def run(
        self,
        config: Config,
        simulate: bool = True,
        tags: Optional[Set[str]] = None,
        skip_tags: Optional[Set[str]] = None,
        working_dir: Optional[Path] = None,
    ) -> None:
        """
        Start executing rules asynchronously.
        
        Args:
            config: Organize Config object
            simulate: Whether to simulate (dry run)
            tags: Tags to include
            skip_tags: Tags to exclude
            working_dir: Working directory
        """
        if self.is_running:
            return
        
        self._cancel_event.clear()
        self._logs = []
        self._result = ExecutionResult(start_time=datetime.now())
        
        self._thread = threading.Thread(
            target=self._execute,
            args=(config, simulate, tags or set(), skip_tags or set(), working_dir),
            daemon=True,
        )
        self._thread.start()
    
    def run_from_string(
        self,
        config_string: str,
        config_path: Optional[Path] = None,
        simulate: bool = True,
        tags: Optional[Set[str]] = None,
        skip_tags: Optional[Set[str]] = None,
        working_dir: Optional[Path] = None,
    ) -> None:
        """
        Start executing rules from a config string.
        
        Args:
            config_string: YAML config content
            config_path: Optional config file path
            simulate: Whether to simulate
            tags: Tags to include
            skip_tags: Tags to exclude
            working_dir: Working directory
        """
        try:
            config = Config.from_string(config=config_string, config_path=config_path)
            self.run(config, simulate, tags, skip_tags, working_dir)
        except Exception as e:
            self._log_entry(LogEntry(
                timestamp=datetime.now(),
                level="error",
                message=f"Failed to parse config: {e}",
            ))
            self._set_status(ExecutionStatus.FAILED)
    
    def cancel(self) -> None:
        """Cancel the current execution."""
        if self.is_running:
            self._cancel_event.set()
            self._set_status(ExecutionStatus.STOPPING)
    
    def clear_logs(self) -> None:
        """Clear all log entries."""
        self._logs = []
    
    def _execute(
        self,
        config: Config,
        simulate: bool,
        tags: Set[str],
        skip_tags: Set[str],
        working_dir: Optional[Path],
    ) -> None:
        """Execute rules in a separate thread."""
        self._set_status(ExecutionStatus.RUNNING)
        
        try:
            # Create custom output handler
            output = GuiOutput(
                on_msg=self._log_entry,
                on_progress=self._on_progress,
            )
            
            # Set working directory
            work_dir = working_dir or Path(".")
            
            # Execute the config
            config.execute(
                simulate=simulate,
                output=output,
                tags=tags,
                skip_tags=skip_tags,
                working_dir=work_dir,
            )
            
            if self._cancel_event.is_set():
                self._set_status(ExecutionStatus.CANCELLED)
            else:
                self._set_status(ExecutionStatus.COMPLETED)
                
        except Exception as e:
            self._log_entry(LogEntry(
                timestamp=datetime.now(),
                level="error",
                message=f"Execution failed: {e}",
            ))
            self._set_status(ExecutionStatus.FAILED)
        
        finally:
            self._result.end_time = datetime.now()
            self._result.logs = self._logs.copy()
            
            if self._on_complete:
                self._on_complete(self._result)
    
    def _set_status(self, status: ExecutionStatus) -> None:
        """Set status and notify callback."""
        self._status = status
        if self._on_status_change:
            self._on_status_change(status)
    
    def _log_entry(self, entry: LogEntry) -> None:
        """Add log entry and notify callback."""
        self._logs.append(entry)
        
        # Update result counts
        if entry.level == "error":
            self._result.error_count += 1
        elif entry.level == "success":
            self._result.success_count += 1
        
        if self._on_log:
            self._on_log(entry)
    
    def export_logs(self, path: Path, format: str = "txt") -> bool:
        """
        Export logs to a file.
        
        Args:
            path: Output file path
            format: Export format (txt, json, csv)
            
        Returns:
            True if successful
        """
        try:
            if format == "txt":
                lines = []
                for entry in self._logs:
                    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    lines.append(f"[{timestamp}] [{entry.level.upper()}] {entry.message}")
                path.write_text("\n".join(lines), encoding="utf-8")
                
            elif format == "json":
                import json
                data = [entry.to_dict() for entry in self._logs]
                path.write_text(json.dumps(data, indent=2), encoding="utf-8")
                
            elif format == "csv":
                import csv
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Level", "Message", "Rule", "File", "Action"])
                    for entry in self._logs:
                        writer.writerow([
                            entry.timestamp.isoformat(),
                            entry.level,
                            entry.message,
                            entry.rule_name or "",
                            entry.file_path or "",
                            entry.action_name or "",
                        ])
            
            return True
        except Exception:
            return False
