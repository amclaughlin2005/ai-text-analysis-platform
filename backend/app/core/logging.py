"""
Logging configuration for the AI-Powered Text Analysis Platform
Provides structured logging with correlation IDs and multiple output formats.
"""

import logging
import logging.config
import json
import sys
from typing import Optional
from datetime import datetime
import uuid
from contextvars import ContextVar
from .config import get_settings

# Get application settings
settings = get_settings()

# Context variable for correlation ID tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to log records for request tracing"""
    
    def filter(self, record):
        record.correlation_id = correlation_id.get() or 'no-correlation-id'
        return True

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    Outputs logs in JSON format for better parsing and analysis
    """
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'correlation_id': getattr(record, 'correlation_id', 'no-correlation-id'),
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class StandardFormatter(logging.Formatter):
    """
    Standard formatter for human-readable logs
    Used in development and when JSON format is not preferred
    """
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(correlation_id)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

def setup_logging():
    """
    Configure application logging based on settings
    Sets up formatters, handlers, and log levels
    """
    
    # Choose formatter based on configuration
    if settings.LOG_FORMAT.lower() == 'json':
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(CorrelationIdFilter())
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    configure_logger('uvicorn', logging.INFO)
    configure_logger('uvicorn.access', logging.INFO)
    configure_logger('sqlalchemy.engine', logging.WARNING)  # Reduce SQL noise
    configure_logger('celery', logging.INFO)
    configure_logger('nltk', logging.WARNING)  # Reduce NLTK noise
    
    # Configure our application loggers
    configure_logger('app', getattr(logging, settings.LOG_LEVEL.upper()))
    configure_logger('analysis', getattr(logging, settings.LOG_LEVEL.upper()))
    configure_logger('websocket', getattr(logging, settings.LOG_LEVEL.upper()))
    
    logging.info(f"✅ Logging configured with level: {settings.LOG_LEVEL}")

def configure_logger(name: str, level: int):
    """Configure specific logger with given name and level"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Don't add handlers here - they inherit from root logger

def get_logger(name: str) -> logging.Logger:
    """
    Get logger with the given name
    Convenience function for creating module-specific loggers
    """
    return logging.getLogger(name)

def set_correlation_id(corr_id: str = None) -> str:
    """
    Set correlation ID for current context
    Returns the correlation ID that was set
    """
    if corr_id is None:
        corr_id = str(uuid.uuid4())[:8]  # Short correlation ID
    
    correlation_id.set(corr_id)
    return corr_id

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context"""
    return correlation_id.get()

class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter for adding extra context to log messages
    Useful for adding structured data to log entries
    """
    
    def process(self, msg, kwargs):
        # Add extra fields to the log record
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        # Add any additional context from the adapter
        kwargs['extra'].update(self.extra)
        
        return msg, kwargs

def create_logger_adapter(logger: logging.Logger, extra_context: dict) -> LoggerAdapter:
    """
    Create logger adapter with extra context
    Useful for adding request-specific or module-specific context
    """
    return LoggerAdapter(logger, extra_context)

# Performance logging utilities
class PerformanceLogger:
    """
    Utility class for logging performance metrics
    Useful for tracking execution times and resource usage
    """
    
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            
            if exc_type is not None:
                self.logger.error(
                    f"Operation failed: {self.operation_name}",
                    extra={
                        'extra_fields': {
                            'operation': self.operation_name,
                            'duration_seconds': duration,
                            'status': 'failed',
                            'error': str(exc_val)
                        }
                    }
                )
            else:
                self.logger.info(
                    f"Operation completed: {self.operation_name}",
                    extra={
                        'extra_fields': {
                            'operation': self.operation_name,
                            'duration_seconds': duration,
                            'status': 'success'
                        }
                    }
                )

def log_performance(logger: logging.Logger, operation_name: str):
    """
    Decorator for logging function performance
    Usage: @log_performance(logger, "my_function")
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with PerformanceLogger(logger, operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Security logging utilities
def log_security_event(event_type: str, details: dict, level: int = logging.WARNING):
    """
    Log security-related events
    Used for audit trails and security monitoring
    """
    security_logger = get_logger('security')
    
    log_entry = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'correlation_id': get_correlation_id(),
        'details': details
    }
    
    security_logger.log(
        level,
        f"Security event: {event_type}",
        extra={'extra_fields': log_entry}
    )

# Business logic logging utilities
def log_business_event(event_type: str, details: dict):
    """
    Log business-related events
    Used for analytics and business intelligence
    """
    business_logger = get_logger('business')
    
    log_entry = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'correlation_id': get_correlation_id(),
        'details': details
    }
    
    business_logger.info(
        f"Business event: {event_type}",
        extra={'extra_fields': log_entry}
    )

# Export commonly used objects
__all__ = [
    'setup_logging',
    'get_logger',
    'set_correlation_id',
    'get_correlation_id',
    'create_logger_adapter',
    'PerformanceLogger',
    'log_performance',
    'log_security_event',
    'log_business_event'
]
