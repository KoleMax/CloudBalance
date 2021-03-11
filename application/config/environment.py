import pydantic

from typing import Optional


class Settings(pydantic.BaseSettings):
    # App config
    SERVICE_NAME: str = "Cloud-Balance"
    TELEGRAM_TOKEN: Optional[str]

    # Logging config
    # Debug mod + log level 'debug'
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    SYSLOG_HOST: str = "127.0.0.1"
    SYSLOG_PORT: int = 514

    # Database config
    DB_URL: pydantic.PostgresDsn = "postgres://postgres:cloudbalance@db:5432/db"  # pylint: disable=no-member

    DB_POOL_MIN_SIZE: int = 1
    DB_POOL_MAX_SIZE: int = 5

    DB_ECHO: bool = DEBUG
    DB_USE_SSL: bool = False
    DB_RETRY_LIMIT: int = 5
    DB_RETRY_INTERVAL: int = 1

    DB_CONNECTION_PER_REQUEST: bool = True

    # TODO: redis config

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
