"""
Logger Module - Centralized logging configuration for the API.

Provides rotating file handlers and console logging with proper formatting.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from typing import Any, Dict


# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Log file configuration
LOG_FILE = LOGS_DIR / "api.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files

# Log format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
  name: str = "api",
  level: int = logging.INFO,
  log_to_console: bool = True,
  log_to_file: bool = True
) -> logging.Logger:
  """
  Set up and configure logger with rotating file handler and console handler.

  Args:
    name: Logger name (default: "api")
    level: Logging level (default: INFO)
    log_to_console: Enable console logging (default: True)
    log_to_file: Enable file logging (default: True)

  Returns:
    Configured logger instance
  """
  logger = logging.getLogger(name)
  logger.setLevel(level)

  # Avoid adding duplicate handlers
  if logger.handlers:
    return logger

  # Create formatter
  formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

  # File handler with rotation
  if log_to_file:
    file_handler = RotatingFileHandler(
      LOG_FILE,
      maxBytes=MAX_BYTES,
      backupCount=BACKUP_COUNT,
      encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

  # Console handler
  if log_to_console:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

  return logger


# Create default API logger
api_logger = setup_logger(
  name="api",
  level=logging.INFO,
  log_to_console=True,
  log_to_file=True
)


def sanitize_request_data(data: Any, sensitive_fields: list = None) -> Any:
  """
  Sanitize sensitive data from request body for logging.

  Args:
    data: Request data (dict, list, or primitive)
    sensitive_fields: List of field names to redact (default: common sensitive fields)

  Returns:
    Sanitized data with sensitive fields redacted
  """
  if sensitive_fields is None:
    sensitive_fields = [
      'password', 'token', 'api_key', 'secret', 'credit_card',
      'ssn', 'pin', 'authorization'
    ]

  if isinstance(data, dict):
    sanitized = {}
    for key, value in data.items():
      key_lower = key.lower()
      if any(sensitive in key_lower for sensitive in sensitive_fields):
        sanitized[key] = "***REDACTED***"
      elif isinstance(value, (dict, list)):
        sanitized[key] = sanitize_request_data(value, sensitive_fields)
      else:
        sanitized[key] = value
    return sanitized
  elif isinstance(data, list):
    return [sanitize_request_data(item, sensitive_fields) for item in data]
  else:
    return data


def format_request_log(
  method: str,
  path: str,
  query_params: Dict[str, Any] = None,
  body: Any = None,
  headers: Dict[str, str] = None
) -> str:
  """
  Format request information for logging.

  Args:
    method: HTTP method (GET, POST, etc.)
    path: Request path
    query_params: Query parameters dict
    body: Request body (will be sanitized)
    headers: Request headers (optional)

  Returns:
    Formatted log string
  """
  log_parts = [f"{method} {path}"]

  if query_params:
    query_str = ", ".join([f"{k}={v}" for k, v in query_params.items()])
    log_parts.append(f"Params: {{{query_str}}}")

  if body:
    sanitized_body = sanitize_request_data(body)
    try:
      body_str = json.dumps(sanitized_body, ensure_ascii=False)
      if len(body_str) > 200:
        body_str = body_str[:200] + "..."
      log_parts.append(f"Body: {body_str}")
    except (TypeError, ValueError):
      log_parts.append(f"Body: {str(sanitized_body)[:200]}")

  return " | ".join(log_parts)


def format_response_log(
  status_code: int,
  response_size: int = None,
  duration_ms: float = None
) -> str:
  """
  Format response information for logging.

  Args:
    status_code: HTTP status code
    response_size: Response size in bytes
    duration_ms: Request duration in milliseconds

  Returns:
    Formatted log string
  """
  log_parts = [f"Status: {status_code}"]

  if response_size is not None:
    if response_size < 1024:
      log_parts.append(f"Size: {response_size}B")
    else:
      log_parts.append(f"Size: {response_size / 1024:.2f}KB")

  if duration_ms is not None:
    log_parts.append(f"Duration: {duration_ms:.2f}ms")

  return " | ".join(log_parts)


def log_request(
  method: str,
  path: str,
  query_params: Dict[str, Any] = None,
  body: Any = None
) -> None:
  """
  Log incoming request information.

  Args:
    method: HTTP method
    path: Request path
    query_params: Query parameters
    body: Request body
  """
  log_message = format_request_log(method, path, query_params, body)
  api_logger.info(f"INCOMING REQUEST: {log_message}")


def log_response(
  method: str,
  path: str,
  status_code: int,
  response_size: int = None,
  duration_ms: float = None
) -> None:
  """
  Log outgoing response information.

  Args:
    method: HTTP method
    path: Request path
    status_code: HTTP status code
    response_size: Response size in bytes
    duration_ms: Request duration in milliseconds
  """
  log_message = format_response_log(status_code, response_size, duration_ms)

  # Use appropriate log level based on status code
  if status_code >= 500:
    api_logger.error(f"OUTGOING RESPONSE: {method} {path} | {log_message}")
  elif status_code >= 400:
    api_logger.warning(f"OUTGOING RESPONSE: {method} {path} | {log_message}")
  else:
    api_logger.info(f"OUTGOING RESPONSE: {method} {path} | {log_message}")


def log_error(
  method: str,
  path: str,
  error: Exception,
  include_traceback: bool = True
) -> None:
  """
  Log error information with optional traceback.

  Args:
    method: HTTP method
    path: Request path
    error: Exception object
    include_traceback: Include full traceback (default: True)
  """
  error_message = f"ERROR: {method} {path} | {type(error).__name__}: {str(error)}"

  if include_traceback:
    import traceback
    tb = traceback.format_exc()
    api_logger.error(f"{error_message}\n{tb}")
  else:
    api_logger.error(error_message)


def get_logger(name: str = "api") -> logging.Logger:
  """
  Get or create a logger with the given name.

  Args:
    name: Logger name

  Returns:
    Logger instance
  """
  return logging.getLogger(name)


# Module-level convenience functions
def debug(message: str) -> None:
  """Log debug message."""
  api_logger.debug(message)


def info(message: str) -> None:
  """Log info message."""
  api_logger.info(message)


def warning(message: str) -> None:
  """Log warning message."""
  api_logger.warning(message)


def error(message: str) -> None:
  """Log error message."""
  api_logger.error(message)


def critical(message: str) -> None:
  """Log critical message."""
  api_logger.critical(message)
