import json
from typing import List, Tuple

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aioredis import Redis

from application.models import Tag
from application.models import Transaction
from application.telegram.menu.project.renderers import return_button
from application.telegram.menu.tags.shemas import TagInfo, TagsListRenderingInfo
from application.telegram.fsm import TransactionData, make_redis_add_transaction_key, make_redis_add_transaction_description_key, make_redis_delete_transaction_key, DeleteTransactionData
from application.telegram.menu.transactions.renderers import ChoseTagListRenderer, return_button, TransactionListRenderer, list_transactions_return_button
from application.telegram.menu.transactions.shemas import TransactionInfo, TransactionsListRenderingInfo

from datetime import datetime


import pytz

local_tz = pytz.timezone('Europe/Moscow')


DELETE_KEYWORD = 'Yes'


async def chose_tag_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    project_id = int(parsed_query_data[2])
    project_name = str(parsed_query_data[3])
    command = str(parsed_query_data[4])

    # TODO: enum
    transaction_type_id = 1 if command == "ADD_INCOME" else 2

    project_tags: List[Tuple[int, str]] = await Tag.get_by_project_id(project_id)

    tags_data = [TagsListRenderingInfo(**{
        "button_title": tag_data[1],
        "callback_data": TagInfo(**{
                "id": tag_data[0],
                "name": tag_data[1]
            })
    }) for tag_data in project_tags]

    markup = ChoseTagListRenderer(user_id=user_id, project_id=project_id,
                                  project_name=project_name, transaction_type_id=transaction_type_id)(tags_data)
    await query.message.edit_text(f"Chose tag for {'income' if transaction_type_id == 1 else 'expense'} transaction.")
    await query.message.edit_reply_markup(reply_markup=markup)


async def list_transactions_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    project_id = int(parsed_query_data[2])
    project_name = str(parsed_query_data[3])

    last_transactions = await Transaction.query.where(Transaction.project_id == project_id).order_by(Transaction.timestamp.desc()).limit(10).gino.all()

    transactions_data = [
        TransactionsListRenderingInfo(**{
            "button_title": f"{'Expense' if transaction.type_id == 2 else 'Income'} - {transaction.amount} - {transaction.description if transaction.description else ''} "
                            f"- {transaction.timestamp.replace(tzinfo=pytz.utc).astimezone(local_tz).strftime('%d.%m.%Y %H:%M:%S')}",
            "callback_data": TransactionInfo(**{
                "id": transaction.id
            })
        }) for transaction in last_transactions
    ]

    settings_markup = TransactionListRenderer(user_id=user_id, project_id=project_id, project_name=project_name)(transactions_data)
    await query.message.edit_text(f"{project_name} last transactions\nTap to delete")
    await query.message.edit_reply_markup(reply_markup=settings_markup)


def make_transaction_amount_input_handler(redis: Redis):
    async def transaction_amount_input_handler(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        project_id = int(parsed_query_data[2])
        project_name = str(parsed_query_data[3])
        transaction_type_id = int(parsed_query_data[4])
        tag_id = int(parsed_query_data[5])
        tag_name = str(parsed_query_data[6])

        chat_id = query.message.chat.id
        redis_key = make_redis_add_transaction_description_key(chat_id)

        redis_data = TransactionData(**{
            "user_id": user_id,
            "project_id": project_id,
            'project_name': project_name,
            "tag_id": tag_id,
            "tag_name": tag_name,
            "transaction_type_id": transaction_type_id,
        })

        await redis.set(redis_key, redis_data.json())

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name)
        await query.message.edit_text("Input transaction description:")
        await query.message.edit_reply_markup(return_markup)

    return transaction_amount_input_handler


def make_transaction_description_input_callback(redis: Redis):
    async def transaction_description_input(message: Message):
        description = message.text

        transaction_data = await redis.get(make_redis_add_transaction_description_key(message.chat.id))
        transaction_parsed_data = TransactionData(**json.loads(transaction_data))

        await redis.delete(make_redis_add_transaction_description_key(message.chat.id))

        transaction_parsed_data.description = description
        redis_key = make_redis_add_transaction_key(message.chat.id)
        await redis.set(redis_key, transaction_parsed_data.json())

        await message.answer("Input transaction amount:")

    return transaction_description_input


def make_transaction_amount_input_callback(redis: Redis):
    async def transaction_amount_input(message: Message):
        try:
            amount = int(message.text)
        except ValueError:
            await message.answer("You should enter positive number.\nTry again:")
            return

        if amount < 0:
            await message.answer("Amount should be positive.\nTry again:")
            return

        transaction_data = await redis.get(make_redis_add_transaction_key(message.chat.id))
        transaction_parsed_data = TransactionData(**json.loads(transaction_data))

        await redis.delete(make_redis_add_transaction_key(message.chat.id))

        user_id = transaction_parsed_data.user_id
        project_id = transaction_parsed_data.project_id
        project_name = transaction_parsed_data.project_name
        tag_id = transaction_parsed_data.tag_id
        tag_name = transaction_parsed_data.tag_name
        transaction_type_id = transaction_parsed_data.transaction_type_id
        description = transaction_parsed_data.description

        transaction = Transaction(amount=amount, project_id=project_id, user_id=user_id, tag_id=tag_id,
                                  type_id=transaction_type_id, description=description,
                                  timestamp=datetime.utcnow())

        await transaction.create()

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name)
        await message.answer(f"{'Income' if transaction_type_id == 1 else 'Expense'} transaction with tag {tag_name} "
                             f"successfully added for {project_name}.", reply_markup=return_markup)

    return transaction_amount_input


def make_transaction_delete_handler(redis: Redis):
    async def transaction_amount_input_handler(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        project_id = int(parsed_query_data[2])
        project_name = str(parsed_query_data[3])
        transaction_id = int(parsed_query_data[4])

        chat_id = query.message.chat.id
        redis_key = make_redis_delete_transaction_key(chat_id)

        redis_data = DeleteTransactionData(**{
            "id": transaction_id,
            "user_id": user_id,
            "project_id": project_id,
            'project_name': project_name,
        })

        await redis.set(redis_key, redis_data.json())

        return_markup = list_transactions_return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name)
        await query.message.edit_text(f"Type '{DELETE_KEYWORD}' if you want to delete this transaction:")
        await query.message.edit_reply_markup(return_markup)

    return transaction_amount_input_handler


def make_transaction_delete_callback(redis: Redis):
    async def delete_transaction(message: Message):
        chat_id = message.chat.id

        redis_key = make_redis_delete_transaction_key(chat_id)

        user_kick_data = await redis.get(redis_key)
        parsed_user_kick_data = DeleteTransactionData(**json.loads(user_kick_data))
        user_id = parsed_user_kick_data.user_id
        project_id = parsed_user_kick_data.project_id
        project_name = parsed_user_kick_data.project_name
        transaction_id = parsed_user_kick_data.id

        return_markup = list_transactions_return_button(InlineKeyboardMarkup(row_width=3), user_id,
                                                        project_id, project_name,)

        answer = message.text
        if answer != DELETE_KEYWORD:
            await message.delete()
            return

        await Transaction.delete.where(Transaction.id == transaction_id).gino.status()

        await redis.delete(redis_key)
        await message.answer(f"Transaction was deleted.", reply_markup=return_markup)

    return delete_transaction

