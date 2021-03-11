from pydantic import BaseModel
from application.telegram.menu.base import ListRenderingInfo


class ProjectInfo(BaseModel):
    id: int
    name: str


class ProjectsListRenderingInfo(ListRenderingInfo):
    callback_data: ProjectInfo
