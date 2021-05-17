from aiogram.dispatcher import Dispatcher

from application import enums
from .handlers import user_menu_handler, return_handler
from .renderers import RETURN_CALLBACK_DATA, CALLBACK_DATA


def configure_dispatcher(dispatcher: Dispatcher) -> None:
    # tag menu - check permission in router
    dispatcher.callback_query_handler(
        CALLBACK_DATA.filter(current_user_role_id=(str(enums.UserRoles.CREATOR.value), str(enums.UserRoles.ADMIN.value)))
    )(user_menu_handler)

    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
