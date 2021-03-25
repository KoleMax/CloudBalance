from aiogram.dispatcher import Dispatcher
from aioredis import Redis
from redis import Redis as SyncRedis

from application.telegram.fsm import make_redis_change_nickname_key
from application.telegram.menu.main.handlers import settings_handler as return_handler
from .handlers import make_change_nickname_callback, make_change_nickname_handler
from .renderers import CALLBACK_DATA, RETURN_CALLBACK_DATA, MainSettingsMenuCommands


def configure_dispatcher(dispatcher: Dispatcher, redis: Redis, sync_redis: SyncRedis) -> None:
    # redis fsm create project handler
    dispatcher.message_handler(
        lambda message: sync_redis.get(make_redis_change_nickname_key(message.chat.id)) is not None
    )(make_change_nickname_callback(redis))

    # set change nickname state handler
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=MainSettingsMenuCommands.CHANGE_NICKNAME.name))(
        make_change_nickname_handler(redis)
    )
    # return to main menu callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
