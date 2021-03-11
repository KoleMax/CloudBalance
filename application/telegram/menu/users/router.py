from aiogram.dispatcher import Dispatcher

from .handlers import user_menu_handler, return_handler
from .renderers import RETURN_CALLBACK_DATA, CALLBACK_DATA


def configure_dispatcher(dispatcher: Dispatcher) -> None:
    # tag menu - check permission in router
    # TODO: enum
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(current_user_role_id='1'))(user_menu_handler)
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(current_user_role_id='2'))(user_menu_handler)

    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
