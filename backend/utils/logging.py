"""Structured logging setup with automated secret masking."""

import logging
import structlog
from typing import Any

SENSITIVE_KEYS = {
    "password", "secret", "api_key", "key", "token", "authorization",
    "jwt", "secret_key", "cookie", "card_number", "cvv", "db_password"
}


def sanitize_sensitive_data(logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive keys from log output."""
    for k, v in list(event_dict.items()):
        if any(sensitive in k.lower() for sensitive in SENSITIVE_KEYS):
            event_dict[k] = "***REDACTED***"
    return event_dict


def setup_logging(level: str = "INFO"):
    """Configure structured logging with PII/secret protection."""
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            sanitize_sensitive_data,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


def get_logger(name: str = None):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
