from pydantic import BaseModel

from application.telegram.menu.base import ListRenderingInfo


class TagInfo(BaseModel):
    id: int
    name: str


class TagsListRenderingInfo(ListRenderingInfo):
    callback_data: TagInfo
