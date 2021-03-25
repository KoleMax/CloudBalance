import pydantic


class Settings(pydantic.BaseSettings):
    # App config
    SERVICE_NAME: str
    TELEGRAM_TOKEN: str

    # Logging config
    DEBUG: bool
    LOG_LEVEL: str

    SYSLOG_HOST: str
    SYSLOG_PORT: int

    # Database config
    DB_URL: pydantic.PostgresDsn

    DB_POOL_MIN_SIZE: int
    DB_POOL_MAX_SIZE: int

    DB_ECHO: bool
    DB_USE_SSL: bool
    DB_RETRY_LIMIT: int
    DB_RETRY_INTERVAL: int

    DB_CONNECTION_PER_REQUEST: bool

    # Redis config
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    REDIS_POOL_MIN_SIZE: int
    REDIS_POOL_MAX_SIZE: int

    # class Config:
    #     env_file = ".env"
    #     env_file_encoding = "utf-8"


settings = Settings()
