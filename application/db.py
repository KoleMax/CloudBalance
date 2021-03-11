import asyncio
import logging
from dataclasses import asdict, dataclass
from typing import Optional

from gino.ext.starlette import Gino

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    dsn: str
    pool_min_size: Optional[int]
    pool_max_size: Optional[int]
    echo: Optional[bool]
    ssl: Optional[bool]
    use_connection_for_request: Optional[bool]
    retry_limit: Optional[int]
    retry_interval: Optional[int]


class Database(Gino):
    async def connect(self, **kwargs):
        config = self.config

        logger.debug("Connecting to the database: %s", config["dsn"])

        retries = 0
        while True:
            retries += 1
            # noinspection PyBroadException
            try:
                await self.set_bind(
                    config["dsn"],
                    echo=config["echo"],
                    min_size=config["min_size"],
                    max_size=config["max_size"],
                    # ssl=config["ssl"],  TODO: ssl?
                    **kwargs,
                )
                break
            except Exception:
                if retries < config["retry_limit"]:
                    logger.info("Waiting for the database to start...")
                    await asyncio.sleep(config["retry_interval"])
                else:
                    logger.error("Cannot connect to the database; max retries reached.")
                    raise

        logger.info("Database connection pool created: %s", repr(self.bind))
        return self

    async def disconnect(self):
        if self._bind is None:
            logger.info("Database connection already close")
            return

        logger.debug("Closing database connection: %s", self.bind)

        _bind = self.pop_bind()
        await _bind.close()

        logger.info("Closed database connection: %s", _bind.repr())

    def acquire(self, *args, **kwargs):
        return self.bind.acquire(*args, **kwargs)

    async def is_alive(self) -> bool:
        res = await self.scalar("SELECT 1")
        return res == 1


def database_config_from_app_config(settings) -> DatabaseConfig:
    return DatabaseConfig(
        dsn=settings.DB_URL,
        pool_min_size=settings.DB_POOL_MIN_SIZE,
        pool_max_size=settings.DB_POOL_MAX_SIZE,
        echo=settings.DB_ECHO,
        ssl=settings.DB_USE_SSL,  # TODO: ssl?
        use_connection_for_request=settings.DB_CONNECTION_PER_REQUEST,
        retry_limit=settings.DB_RETRY_LIMIT,
        retry_interval=settings.DB_RETRY_INTERVAL,
    )


def get_database(config: DatabaseConfig) -> Database:
    return Database(**asdict(config))
