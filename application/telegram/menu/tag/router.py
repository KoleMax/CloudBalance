from aiogram.dispatcher import Dispatcher
from aioredis import Redis
from redis import Redis as SyncRedis

from application.telegram.fsm import make_redis_rename_tag_key
from .handlers import make_rename_tag_callback, make_rename_tag_handler, make_return_handler
from .renderers import CALLBACK_DATA, RETURN_CALLBACK_DATA
from .renderers import TagMenuCommands


def configure_dispatcher(dispatcher: Dispatcher, redis: Redis, sync_redis: SyncRedis) -> None:
    # redis fsm rename tag handler
    dispatcher.message_handler(
        lambda message: sync_redis.get(make_redis_rename_tag_key(message.chat.id)) is not None
    )(make_rename_tag_callback(redis))

    # set rename tag state handler
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=TagMenuCommands.RENAME.name))(
        make_rename_tag_handler(redis)
    )

    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(make_return_handler(redis))
