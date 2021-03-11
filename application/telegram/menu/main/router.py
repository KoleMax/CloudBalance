from aiogram.dispatcher import Dispatcher
from aioredis import Redis
from redis import Redis as SyncRedis

from .fsm import make_redis_joining_key, make_redis_creating_key
from .handlers import projects_handler, settings_handler, make_join_to_project_handler, make_join_to_project_callback, \
    make_create_project_handler, make_create_project_callback
from .renderers import CALLBACK_DATA, RETURN_CALLBACK_DATA, MainMenuCommands
from .utils import make_return_handler


def configure_dispatcher(dispatcher: Dispatcher, redis: Redis, sync_redis: SyncRedis) -> None:
    # redis fsm create project handler
    dispatcher.message_handler(lambda message: sync_redis.get(make_redis_creating_key(message.chat.id)) is not None) \
        (make_create_project_callback(redis))
    # redis fsm join to project handler
    dispatcher.message_handler(lambda message: sync_redis.get(make_redis_joining_key(message.chat.id)) is not None)\
        (make_join_to_project_callback(redis))

    # set create project state handler
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=MainMenuCommands.NEW.name))\
        (make_create_project_handler(redis))
    # projects list callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=MainMenuCommands.PROJECTS.name))(projects_handler)
    # set join to project state handler
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=MainMenuCommands.JOIN.name))\
        (make_join_to_project_handler(redis))
    # settings callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=MainMenuCommands.SETTINGS.name))(settings_handler)
    # return to main menu callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(make_return_handler(redis))
