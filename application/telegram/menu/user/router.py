from aiogram.dispatcher import Dispatcher
from aiogram import Bot
from aioredis import Redis
from redis import Redis as SyncRedis

from application.telegram.menu.user.fsm import make_redis_kick_key
from .handlers import make_return_handler, make_kick_handler,  make_kick_callback, chose_role_handler, make_set_role_handler
from .renderers import CALLBACK_DATA, UserMenuCommands, RETURN_CALLBACK_DATA, CHOSE_ROLE_CALLBACK_DATA


def configure_dispatcher(dispatcher: Dispatcher, bot: Bot, redis: Redis, sync_redis: SyncRedis) -> None:
    # redis fsm kick user handler
    dispatcher.message_handler(lambda message: sync_redis.get(make_redis_kick_key(message.chat.id)) is not None) \
        (make_kick_callback(redis, bot))
    # change role
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=UserMenuCommands.CHANGE_ROLE.name))(chose_role_handler)
    # set chosen role
    dispatcher.callback_query_handler(CHOSE_ROLE_CALLBACK_DATA.filter())(make_set_role_handler(bot))
    # kick user callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=UserMenuCommands.KICK.name))(make_kick_handler(redis))
    # return callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(make_return_handler(redis))
