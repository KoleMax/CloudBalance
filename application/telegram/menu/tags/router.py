from aiogram.dispatcher import Dispatcher
from aioredis import Redis
from redis import Redis as SyncRedis

from application import enums
from application.telegram.fsm import make_redis_create_tag_key
from .handlers import make_create_tag_handler, make_return_handler, make_create_tag_callback, tag_menu_handler
from .renderers import RETURN_CALLBACK_DATA, CREATE_TAG_CALLBACK_DATA, CALLBACK_DATA


def configure_dispatcher(dispatcher: Dispatcher, redis: Redis, sync_redis: SyncRedis) -> None:
    # redis fsm create project handler
    dispatcher.message_handler(
        lambda message: sync_redis.get(make_redis_create_tag_key(message.chat.id)) is not None
    )(make_create_tag_callback(redis))
    # set create tag state handler
    dispatcher.callback_query_handler(CREATE_TAG_CALLBACK_DATA.filter())(make_create_tag_handler(redis))
    # return to tags list callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(make_return_handler(redis))

    # tag menu - check permission in router
    dispatcher.callback_query_handler(
        CALLBACK_DATA.filter(user_role_id=(str(enums.UserRoles.CREATOR.value), str(enums.UserRoles.ADMIN.value)))
    )(tag_menu_handler)
