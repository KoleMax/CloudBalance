from aiogram.dispatcher import Dispatcher
from .renderers import CALLBACK_DATA, RETURN_CALLBACK_DATA
from .handlers import project_menu_handler, return_handler


def configure_dispatcher(dispatcher: Dispatcher) -> None:
    # project menu callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter())(project_menu_handler)
    # return to projects list callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
