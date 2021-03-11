"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from pydantic import BaseModel


class ChangeNicknameData(BaseModel):
    user_id: int


def make_redis_change_nickname_key(chat_id: int) -> str:
    return f"{chat_id}_change_nickname"
