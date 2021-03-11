"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from pydantic import BaseModel


class CreateProjectData(BaseModel):
    user_id: int


class JoinToProjectData(BaseModel):
    user_id: int


def make_redis_creating_key(chat_id: int) -> str:
    return f"{chat_id}_creating"


def make_redis_joining_key(chat_id: int) -> str:
    return f"{chat_id}_joining"
