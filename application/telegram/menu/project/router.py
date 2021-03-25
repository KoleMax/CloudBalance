from aiogram.dispatcher import Dispatcher

from application.db import Database
from application.telegram.menu.projects.handlers import project_menu_handler as return_handler
from .handlers import (
    users_handler,
    tags_handler,
    get_token_handler,
    revoke_token_handler,
    make_quick_report_handler,
    transactions_handler,
    make_detailed_report_handler,
)
from .renderers import CALLBACK_DATA, ProjectMenuCommands, RETURN_CALLBACK_DATA


def configure_dispatcher(dispatcher: Dispatcher, db: Database) -> None:
    # list users callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.LIST_USERS.name))(
        users_handler
    )
    # list tags callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.LIST_TAGS.name))(
        tags_handler
    )
    # get project token
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.GET_TOKEN.name))(
        get_token_handler
    )
    # revoke project token
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.REVOKE_TOKEN.name))(
        revoke_token_handler
    )
    # money flow records
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.TRANSACTIONS.name))(
        transactions_handler
    )
    # quick report callback
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.QUICK_REPORT.name))(
        make_quick_report_handler(db)
    )
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=ProjectMenuCommands.DETAILED_REPORT.name))(
        make_detailed_report_handler(db)
    )
    # return callback
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
