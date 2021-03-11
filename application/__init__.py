from .config.environment import settings

from .db import get_database, database_config_from_app_config

db = get_database(database_config_from_app_config(settings))
