"""
Comprehensive TRACE logging system for AI Code Flow.

Provides JSONL-formatted logging with maximum debugging information
and no data sanitization for complete transparency.
"""

import json
import logging
import sys
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, List
import threading
import time

from pythonjsonlogger import jsonlogger


class LogRotator:
    """Log rotation and cleanup management."""

    def __init__(
        self,
        logs_dir: Path,
        max_file_size_mb: int = 100,  # Rotate when log file exceeds 100MB
        max_files: int = 30,         # Keep maximum 30 rotated files
        retention_days: int = 30,    # Keep logs for 30 days
        compression_enabled: bool = True
    ):
        self.logs_dir = logs_dir
        self.max_file_size_mb = max_file_size_mb
        self.max_files = max_files
        self.retention_days = retention_days
        self.compression_enabled = compression_enabled

        # Threading lock for rotation operations
        self._rotation_lock = threading.Lock()

        # Background cleanup thread
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_cleanup = threading.Event()

    def should_rotate(self, log_file: Path) -> bool:
        """Check if log file should be rotated based on size."""
        if not log_file.exists():
            return False

        file_size_mb = log_file.stat().st_size / (1024 * 1024)
        return file_size_mb >= self.max_file_size_mb

    def rotate_log(self, log_file: Path) -> None:
        """Rotate the log file."""
        with self._rotation_lock:
            if not log_file.exists():
                return

            # Generate rotated filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = log_file.stem
            extension = log_file.suffix

            rotated_name = f"{base_name}_{timestamp}{extension}"
            rotated_file = log_file.parent / rotated_name

            try:
                # Move current log to rotated file
                shutil.move(log_file, rotated_file)

                # Compress if enabled
                if self.compression_enabled:
                    compressed_file = rotated_file.with_suffix(f"{extension}.gz")
                    with open(rotated_file, 'rb') as f_in:
                        with gzip.open(compressed_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    # Remove uncompressed rotated file
                    rotated_file.unlink()

                self.info(f"日志文件已轮转: {rotated_file.name}")

                # Cleanup old files
                self._cleanup_old_files()

            except Exception as e:
                self.error(f"日志轮转失败: {e}")

    def _cleanup_old_files(self) -> None:
        """Clean up old rotated log files."""
        try:
            # Find all rotated log files
            pattern = "system_trace_*.jsonl*"
            rotated_files = list(self.logs_dir.glob(pattern))

            # Sort by modification time (newest first)
            rotated_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

            # Remove files beyond max_files limit
            files_to_remove = rotated_files[self.max_files:]
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    self.debug(f"删除过期日志文件: {file_path.name}")
                except Exception as e:
                    self.warning(f"删除日志文件失败 {file_path.name}: {e}")

            # Remove files older than retention_days
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            for file_path in rotated_files[:self.max_files]:  # Only check kept files
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_path.unlink()
                        self.debug(f"删除过期日志文件 (时间): {file_path.name}")
                except Exception as e:
                    self.warning(f"检查日志文件时间失败 {file_path.name}: {e}")

        except Exception as e:
            self.error(f"日志清理失败: {e}")

    def start_background_cleanup(self, interval_hours: int = 24) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return

        def cleanup_worker():
            while not self._stop_cleanup.is_set():
                try:
                    self._cleanup_old_files()
                except Exception as e:
                    self.error(f"后台清理失败: {e}")

                # Wait for next cleanup cycle
                self._stop_cleanup.wait(interval_hours * 3600)

        self._cleanup_thread = threading.Thread(
            target=cleanup_worker,
            name="LogCleanupWorker",
            daemon=True
        )
        self._cleanup_thread.start()
        self.info(f"日志后台清理已启动 (间隔: {interval_hours} 小时)")

    def stop_background_cleanup(self) -> None:
        """Stop background cleanup thread."""
        if self._cleanup_thread:
            self._stop_cleanup.set()
            self._cleanup_thread.join(timeout=5.0)
            if self._cleanup_thread.is_alive():
                self.warning("后台清理线程未能正常停止")
            else:
                self.info("日志后台清理已停止")

    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about log files."""
        try:
            pattern = "system_trace*.jsonl*"
            all_files = list(self.logs_dir.glob(pattern))

            total_size = 0
            file_count = len(all_files)

            for file_path in all_files:
                total_size += file_path.stat().st_size

            return {
                "total_files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "max_file_size_mb": self.max_file_size_mb,
                "max_files": self.max_files,
                "retention_days": self.retention_days,
                "compression_enabled": self.compression_enabled
            }
        except Exception as e:
            self.error(f"获取日志统计失败: {e}")
            return {"error": str(e)}

    # Logging methods for internal use
    def debug(self, message: str) -> None:
        logging.getLogger('ai_code_flow.rotator').debug(message)

    def info(self, message: str) -> None:
        logging.getLogger('ai_code_flow.rotator').info(message)

    def warning(self, message: str) -> None:
        logging.getLogger('ai_code_flow.rotator').warning(message)

    def error(self, message: str) -> None:
        logging.getLogger('ai_code_flow.rotator').error(message)


class TraceLogger:
    """TRACE-level logging with JSONL output and complete data transparency."""

    def __init__(self, log_file: Path, enable_rotation: bool = True):
        self.log_file = log_file
        self.enable_rotation = enable_rotation

        # Initialize log rotator
        self.log_rotator = LogRotator(log_file.parent) if enable_rotation else None

        self._setup_logger()

        # Start background cleanup if rotation is enabled
        if self.log_rotator:
            self.log_rotator.start_background_cleanup()

    def _setup_logger(self) -> None:
        """Configure TRACE logging with JSONL format."""

        # Create custom formatter for JSONL output
        class JsonFormatter(jsonlogger.JsonFormatter):
            def add_fields(self, log_record, record, message_dict):
                super().add_fields(log_record, record, message_dict)

                # Add comprehensive TRACE information
                log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
                log_record['level'] = record.levelname
                log_record['logger'] = record.name
                log_record['function'] = record.funcName
                log_record['line'] = record.lineno
                log_record['module'] = record.module

                # Include all extra fields without sanitization
                if hasattr(record, 'extra_data'):
                    log_record['extra_data'] = record.extra_data

                # Include exception info if present
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)

        # Create logger
        self.logger = logging.getLogger('ai_code_flow')
        self.logger.setLevel(logging.DEBUG)  # Allow all levels including custom TRACE

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # File handler for JSONL logs
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JsonFormatter())

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Prevent duplicate logs from parent loggers
        self.logger.propagate = False

    def _check_rotation(self) -> None:
        """Check if log rotation is needed and perform if necessary."""
        if self.log_rotator and self.log_rotator.should_rotate(self.log_file):
            self.log_rotator.rotate_log(self.log_file)

    def trace(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log TRACE level message with optional extra data."""
        self._check_rotation()
        if extra_data:
            self.logger.log(5, message, extra={'extra_data': extra_data})
        else:
            self.logger.log(5, message)

    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log DEBUG level message."""
        self._check_rotation()
        if extra_data:
            self.logger.debug(message, extra={'extra_data': extra_data})
        else:
            self.logger.debug(message)

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log INFO level message."""
        self._check_rotation()
        if extra_data:
            self.logger.info(message, extra={'extra_data': extra_data})
        else:
            self.logger.info(message)

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log WARNING level message."""
        self._check_rotation()
        if extra_data:
            self.logger.warning(message, extra={'extra_data': extra_data})
        else:
            self.logger.warning(message)

    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log ERROR level message."""
        self._check_rotation()
        if extra_data:
            self.logger.error(message, extra={'extra_data': extra_data})
        else:
            self.logger.error(message)

    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log CRITICAL level message."""
        self._check_rotation()
        if extra_data:
            self.logger.critical(message, extra={'extra_data': extra_data})
        else:
            self.logger.critical(message)

    def get_log_stats(self) -> Dict[str, Any]:
        """Get log rotation and cleanup statistics."""
        if self.log_rotator:
            return self.log_rotator.get_log_stats()
        return {"rotation_enabled": False}

    def cleanup(self) -> None:
        """Clean up resources and stop background threads."""
        if self.log_rotator:
            self.log_rotator.stop_background_cleanup()


# Global logger instance
_trace_logger: Optional[TraceLogger] = None


def get_logger() -> TraceLogger:
    """Get the global TRACE logger instance."""
    global _trace_logger
    if _trace_logger is None:
        # Initialize with default log file path
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "system_trace.jsonl"
        _trace_logger = TraceLogger(log_file)
    return _trace_logger


def setup_logging(log_level: str = "TRACE", logs_dir: Optional[Path] = None) -> TraceLogger:
    """Setup logging system with specified configuration."""
    global _trace_logger

    if logs_dir is None:
        logs_dir = Path(__file__).parent.parent.parent / "logs"

    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "system_trace.jsonl"

    _trace_logger = TraceLogger(log_file)

    # Set Python logging level
    level_map = {
        "TRACE": 5,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    # Add TRACE level
    logging.addLevelName(5, "TRACE")

    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(level_map.get(log_level, logging.INFO))

    return _trace_logger


# Convenience functions for global access
def trace(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global TRACE logging function."""
    get_logger().trace(message, extra_data)


def debug(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global DEBUG logging function."""
    get_logger().debug(message, extra_data)


def info(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global INFO logging function."""
    get_logger().info(message, extra_data)


def warning(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global WARNING logging function."""
    get_logger().warning(message, extra_data)


def error(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global ERROR logging function."""
    get_logger().error(message, extra_data)


def critical(message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Global CRITICAL logging function."""
    get_logger().critical(message, extra_data)
