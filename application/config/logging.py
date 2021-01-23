from logging import config

from application.config.environment import settings

handlers = ['syslog', ] if not settings.DEBUG else ['console']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s',
        },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        },
        'syslog': {
            'format': 'breeze %(levelname)s %(module)s: %(message)s',
        }
    },
    'handlers': {
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'facility': 'local4',
            'formatter': 'syslog',
            'address': (settings.SYSLOG_HOST, settings.SYSLOG_PORT)
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': handlers,
            'level': 'INFO' if not settings.DEBUG else 'DEBUG',
            'propagate': True
        },
    },
}


def configure_logging():
    config.dictConfig(LOGGING)
