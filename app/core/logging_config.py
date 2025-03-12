import logging
import os
import sys
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler
import uuid
from typing import Optional, Dict, Any
from contextvars import ContextVar

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Context variable to store request ID
request_id_var: ContextVar[str] = ContextVar('request_id', default='')

class RequestIDFilter(logging.Filter):
    """Filter that adds request_id to log records."""

    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing."""

    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', ''),
        }

        # Add extra fields if available
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms

        # Include exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Include any additional attributes from the extra parameter
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'id', 'levelname', 'levelno', 'lineno',
                          'module', 'msecs', 'message', 'msg', 'name', 'pathname',
                          'process', 'processName', 'relativeCreated', 'stack_info',
                          'thread', 'threadName', 'request_id', 'duration_ms']:
                log_data[key] = value

        return json.dumps(log_data)

def get_request_id() -> str:
    """Get the current request ID or generate a new one."""
    request_id = request_id_var.get()
    if not request_id:
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
    return request_id

def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    request_id_var.set(request_id)

def setup_logging(app_name="items_api", log_level=None):
    """
    Configure application logging with console and file handlers.

    Args:
        app_name: Name of the application for logging
        log_level: Optional override for log level (defaults to environment setting)
    """
    if log_level is None:
        # Default to ERROR instead of INFO
        log_level = os.getenv("LOG_LEVEL", "ERROR")

    # Get numeric log level
    numeric_level = getattr(logging, log_level.upper(), logging.ERROR)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplication
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add filter for request ID
    request_id_filter = RequestIDFilter()

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.addFilter(request_id_filter)

    # Choose formatter based on environment
    # For production, use JSON formatter
    # console_handler.setFormatter(JSONFormatter())

    # For development, use a more readable format
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # JSON file handler for structured logging
    log_file = os.path.join(logs_dir, f"{app_name}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(JSONFormatter())

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Create separate error log file for errors and higher
    error_log_file = os.path.join(logs_dir, f"{app_name}_errors.log")
    error_file_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_file_handler.setLevel(logging.ERROR)  # This will always be ERROR level regardless of main setting
    error_file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(error_file_handler)

    # Log startup message (only visible if ERROR level is set)
    logging.error(f"Logging configured with level: {log_level}")

    return root_logger

def get_logger(name):
    """
    Get a logger with the given name, configured with proper handlers.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        A properly configured logger instance
    """
    logger = logging.getLogger(name)

    # Add context information helper
    def log_with_context(self, level, msg, *args, **kwargs):
        """Add context data to log records."""
        extra = kwargs.get('extra', {})
        if 'extra' not in kwargs:
            kwargs['extra'] = extra
        extra['context'] = getattr(self, 'context', {})
        original_log = getattr(logging.Logger, level)
        return original_log(self, msg, *args, **kwargs)

    logger.debug_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'debug', msg, *args, **kwargs)
    logger.info_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'info', msg, *args, **kwargs)
    logger.warning_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'warning', msg, *args, **kwargs)
    logger.error_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'error', msg, *args, **kwargs)
    logger.critical_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'critical', msg, *args, **kwargs)
    logger.exception_with_context = lambda msg, *args, **kwargs: log_with_context(logger, 'exception', msg, *args, **kwargs)

    return logger

# Helper methods for common logging patterns
def log_operation_start(logger: logging.Logger, operation: str, **kwargs) -> None:
    """Log the start of an operation with context information."""
    logger.info(f"Operation started: {operation}", extra=kwargs)

def log_operation_success(logger: logging.Logger, operation: str, duration_ms: Optional[float] = None, **kwargs) -> None:
    """Log the successful completion of an operation with duration if available."""
    extra = kwargs.copy()
    if duration_ms is not None:
        extra['duration_ms'] = duration_ms
    logger.info(f"Operation completed successfully: {operation}", extra=extra)

def log_operation_failed(logger: logging.Logger, operation: str, error: Optional[Exception] = None, duration_ms: Optional[float] = None, **kwargs) -> None:
    """Log the failure of an operation with error details and duration if available."""
    extra = kwargs.copy()
    if duration_ms is not None:
        extra['duration_ms'] = duration_ms

    if error:
        logger.error(f"Operation failed: {operation} - {str(error)}", exc_info=error, extra=extra)
    else:
        logger.error(f"Operation failed: {operation}", extra=extra)

def log_database_operation(logger: logging.Logger, operation: str, collection: str, query: Dict[str, Any] = None, duration_ms: Optional[float] = None, **kwargs) -> None:
    """Log database operations with query information and duration."""
    extra = kwargs.copy()
    extra['collection'] = collection
    if query:
        extra['query'] = query
    if duration_ms is not None:
        extra['duration_ms'] = duration_ms

    logger.debug(f"Database operation: {operation}", extra=extra)