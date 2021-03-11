"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from typing import Optional

from pydantic import BaseModel

from application.enums import TransactionTypes


class TransactionData(BaseModel):
    user_id: int
    project_id: int
    project_name: str
    tag_id: int
    tag_name: str
    transaction_type_id: int


def make_redis_add_transaction_key(chat_id: int) -> str:
    return f"{chat_id}_adding_expense"

