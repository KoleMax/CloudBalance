"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from pydantic import BaseModel


class CreateTagData(BaseModel):
    user_id: int
    project_id: int
    project_name: str


def make_redis_create_tag_key(chat_id: int) -> str:
    return f"{chat_id}_create_tag"
