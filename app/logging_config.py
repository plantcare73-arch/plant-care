"""
Structured logging configuration.

Logs are formatted as JSON in production for machine parsing,
and as readable text in development.

Security: Never logs passwords, API keys, or sensitive PII.
"""

import logging
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""

    def format(self, record):
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add extra fields if present
        for key in ('request_id', 'user_id', 'prediction_id', 'model_version'):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info and record.exc_info[0]:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Readable text formatter for development."""

    FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt='%Y-%m-%d %H:%M:%S')


def setup_logging(app):
    """Configure application logging."""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_format = app.config.get('LOG_FORMAT', 'text')

    # Clear default handlers
    app.logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format == 'json':
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())

    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Reduce noise from third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.getLogger('tensorflow').setLevel(logging.WARNING)
