"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from typing import Optional

from pydantic import BaseModel

from application.enums import TransactionTypes


class AddMoneyData(BaseModel):
    user_id: int
    project_id: int
    tag: Optional[int]
    transaction_type: TransactionTypes


def make_redis_choosing_tag_key(chat_id: int) -> str:
    return f"{chat_id}_choosing_tag"


def make_redis_entering_amount_key(chat_id: int) -> str:
    return f"{chat_id}_entering_amount"
