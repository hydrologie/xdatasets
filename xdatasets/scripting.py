import pathlib
import sys
from datetime import datetime as dt

MiB = int(pow(2, 20))

_CONSOLE_FORMAT = "%(message)s"
_LOGFILE_FORMAT = "%(asctime)s: [%(levelname)s]: %(filename)s(%(funcName)s:%(lineno)s) >>> %(message)s"

__all__ = ["LOGGING_CONFIG"]

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": _CONSOLE_FORMAT},
        "logfile": {"format": _LOGFILE_FORMAT},
    },
    "handlers": {
        "default": {
            "level": "INFO",
    },
    }
}