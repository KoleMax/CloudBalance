from pydantic import BaseModel

from application.telegram.menu.base import ListRenderingInfo


class UserInfo(BaseModel):
    id: int
    role_id: int
    name: str


class UsersListRenderingInfo(ListRenderingInfo):
    callback_data: UserInfo
