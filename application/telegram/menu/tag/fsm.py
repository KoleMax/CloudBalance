"""
Contains funcs for handling fsm-driven dialogs with bot.
"""

from pydantic import BaseModel


class RenameTagData(BaseModel):
    user_id: int
    project_id: int
    project_name: str
    tag_id: int
    tag_name: str


def make_redis_rename_tag_key(chat_id: int) -> str:
    return f"{chat_id}_rename_tag"
