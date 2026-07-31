import os
import logging
import logging.config


def setup_logging():
    os.makedirs("/app/logs", exist_ok=True)
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "normal_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "/app/logs/normal.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 7,
                "formatter": "default",
            },
            "error_file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "/app/logs/error.log",
                "when": "midnight",
                "interval": 1,
                "backupCount": 14,
                "level": "ERROR",
                "formatter": "default",
            },
        },
        "root": {
            "handlers": ["console", "normal_file", "error_file"],
            "level": "INFO",
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    