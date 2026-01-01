"""
Comprehensive TRACE logging system for AI Code Flow.

Provides JSONL-formatted logging with maximum debugging information
and no data sanitization for complete transparency.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class TraceLogger:
    """TRACE-level logging with JSONL output and complete data transparency."""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self._setup_logger()

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

    def trace(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log TRACE level message with optional extra data."""
        if extra_data:
            self.logger.log(5, message, extra={'extra_data': extra_data})
        else:
            self.logger.log(5, message)

    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log DEBUG level message."""
        if extra_data:
            self.logger.debug(message, extra={'extra_data': extra_data})
        else:
            self.logger.debug(message)

    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log INFO level message."""
        if extra_data:
            self.logger.info(message, extra={'extra_data': extra_data})
        else:
            self.logger.info(message)

    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log WARNING level message."""
        if extra_data:
            self.logger.warning(message, extra={'extra_data': extra_data})
        else:
            self.logger.warning(message)

    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log ERROR level message."""
        if extra_data:
            self.logger.error(message, extra={'extra_data': extra_data})
        else:
            self.logger.error(message)

    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """Log CRITICAL level message."""
        if extra_data:
            self.logger.critical(message, extra={'extra_data': extra_data})
        else:
            self.logger.critical(message)


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
