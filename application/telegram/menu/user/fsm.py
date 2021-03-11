"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from pydantic import BaseModel


class ChangeRoleData(BaseModel):
    user_id: int
    user_name: str
    project_id: int
    project_name: str


class KickData(BaseModel):
    user_id: int
    user_role_id: int
    project_id: int
    project_name: str
    target_user_id: int
    target_user_name: str


def make_redis_change_role_key(chat_id: int) -> str:
    return f"{chat_id}_change_role"


def make_redis_kick_key(chat_id: int) -> str:
    return f"{chat_id}_kick"
