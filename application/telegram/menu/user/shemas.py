from pydantic import BaseModel

from application.telegram.menu.base import ListRenderingInfo


class RoleInfo(BaseModel):
    id: int


class ChoseRoleRenderingInfo(ListRenderingInfo):
    callback_data: RoleInfo
