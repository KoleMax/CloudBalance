from aiogram.dispatcher import Dispatcher
from aioredis import Redis
from redis import Redis as SyncRedis

from application.telegram.menu.project.handlers import transactions_handler as return_handler
from .handlers import chose_tag_handler, make_transaction_amount_input_handler, make_transaction_amount_input_callback, make_transaction_description_input_callback, list_transactions_handler, make_transaction_delete_handler, make_transaction_delete_callback
from .renderers import CALLBACK_DATA, TransactionsMenuCommands, RETURN_CALLBACK_DATA, CHOSE_TAG_CALLBACK_DATA, LIST_TRANSACTIONS_CALLBACK_DATA, LIST_TRANSACTIONS_RETURN_CALLBACK_DATA
from application.telegram.fsm import make_redis_add_transaction_key, make_redis_add_transaction_description_key, make_redis_delete_transaction_key


def configure_dispatcher(dispatcher: Dispatcher, redis: Redis, sync_redis: SyncRedis) -> None:
    dispatcher.message_handler(lambda message: sync_redis.get(make_redis_add_transaction_key(message.chat.id)) is not None) \
        (make_transaction_amount_input_callback(redis))
    dispatcher.message_handler(lambda message: sync_redis.get(make_redis_add_transaction_description_key(message.chat.id)) is not None) \
        (make_transaction_description_input_callback(redis))
    dispatcher.message_handler(
        lambda message: sync_redis.get(make_redis_delete_transaction_key(message.chat.id)) is not None) \
        (make_transaction_delete_callback(redis))
    dispatcher.callback_query_handler(RETURN_CALLBACK_DATA.filter())(return_handler)
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=TransactionsMenuCommands.ADD_INCOME.name))(chose_tag_handler)
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=TransactionsMenuCommands.ADD_EXPENSE.name))(chose_tag_handler)
    dispatcher.callback_query_handler(CALLBACK_DATA.filter(command=TransactionsMenuCommands.LIST_TRANSACTIONS.name))(list_transactions_handler)
    dispatcher.callback_query_handler(LIST_TRANSACTIONS_RETURN_CALLBACK_DATA.filter())(list_transactions_handler)
    dispatcher.callback_query_handler(CHOSE_TAG_CALLBACK_DATA.filter())(make_transaction_amount_input_handler(redis))
    dispatcher.callback_query_handler(LIST_TRANSACTIONS_CALLBACK_DATA.filter())(make_transaction_delete_handler(redis))
