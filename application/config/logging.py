from logging import config, getLogger, Logger

from application.config.environment import settings
from typing import Dict, Any, Optional

handlers = ["syslog", "console"] if not settings.DEBUG else ["console", "syslog"]


APP_LOGGER_NAME = "application"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s %(module)s %(message)s",
        },
        "simple": {"format": "%(asctime)s - %(levelname)s - %(message)s"},
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(module)s %(levelname)s %(message)s",
        },
        "syslog": {
            "format": "%(levelname)s %(module)s: %(message)s",
        },
    },
    "handlers": {
        "syslog": {
            "class": "rfc5424logging.Rfc5424SysLogHandler",
            "formatter": "json",
            "address": (settings.SYSLOG_HOST, settings.SYSLOG_PORT),
            "msg_as_utf8": False,
        },
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "aiogram": {"handlers": handlers, "level": "WARNING", "propagate": True},
        "aioredis": {"handlers": handlers, "level": "WARNING", "propagate": True},
        APP_LOGGER_NAME: {"handlers": handlers, "level": settings.LOG_LEVEL, "propagate": True},
    },
}


class JsonLoggerWrapper:
    def __init__(self, logger: Logger, extra_fields: Optional[Dict[str, Any]]):
        self.logger = logger
        self.extra_fields = extra_fields

    def _add_extra(self, extra: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if extra and self.extra_fields:
            extra += self.extra_fields
        elif extra is None and self.extra_fields:
            extra = self.extra_fields
        return extra

    def debug(self, *args, **kwargs):
        kwargs["extra"] = self._add_extra(kwargs.get("extra"))
        self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        kwargs["extra"] = self._add_extra(kwargs.get("extra"))
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        kwargs["extra"] = self._add_extra(kwargs.get("extra"))
        self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        kwargs["extra"] = self._add_extra(kwargs.get("extra"))
        self.logger.error(*args, **kwargs)


def configure_logging():
    config.dictConfig(LOGGING)


def get_app_logger(extra: Optional[Dict[str, Any]] = None):
    return JsonLoggerWrapper(getLogger(APP_LOGGER_NAME), extra)
