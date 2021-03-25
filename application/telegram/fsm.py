"""
Contains funcs for handling fsm-driven dialogs with bot.
"""
from typing import Optional

from pydantic import BaseModel

from application.enums import TransactionTypes


class CreateProjectData(BaseModel):
    user_id: int


class JoinToProjectData(BaseModel):
    user_id: int


def make_redis_creating_key(chat_id: int) -> str:
    return f"{chat_id}_creating"


def make_redis_joining_key(chat_id: int) -> str:
    return f"{chat_id}_joining"


class ChangeNicknameData(BaseModel):
    user_id: int


def make_redis_change_nickname_key(chat_id: int) -> str:
    return f"{chat_id}_change_nickname"


class AddMoneyData(BaseModel):
    user_id: int
    project_id: int
    tag: Optional[int]
    transaction_type: TransactionTypes


def make_redis_choosing_tag_key(chat_id: int) -> str:
    return f"{chat_id}_choosing_tag"


def make_redis_entering_amount_key(chat_id: int) -> str:
    return f"{chat_id}_entering_amount"


class CreateTagData(BaseModel):
    user_id: int
    project_id: int
    project_name: str


def make_redis_create_tag_key(chat_id: int) -> str:
    return f"{chat_id}_create_tag"


class TransactionData(BaseModel):
    user_id: int
    project_id: int
    project_name: str
    tag_id: int
    tag_name: str
    transaction_type_id: int
    description: Optional[str]


class DeleteTransactionData(BaseModel):
    id: int
    user_id: int
    project_id: int
    project_name: str


def make_redis_add_transaction_description_key(chat_id: int) -> str:
    return f"{chat_id}_adding_transaction_desc"


def make_redis_add_transaction_key(chat_id: int) -> str:
    return f"{chat_id}_adding_transaction"


def make_redis_delete_transaction_key(chat_id: int) -> str:
    return f"{chat_id}_delete_transaction"


class RenameTagData(BaseModel):
    user_id: int
    project_id: int
    project_name: str
    tag_id: int
    tag_name: str


def make_redis_rename_tag_key(chat_id: int) -> str:
    return f"{chat_id}_rename_tag"


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


CREATE_KEY_FUNCS = [
    make_redis_creating_key,
    make_redis_create_tag_key,
    make_redis_change_nickname_key,
    make_redis_add_transaction_key,
    make_redis_add_transaction_description_key,
    make_redis_entering_amount_key,
    make_redis_choosing_tag_key,
    make_redis_joining_key,
    make_redis_delete_transaction_key,
    make_redis_rename_tag_key,
    make_redis_change_role_key,
    make_redis_kick_key,
]
