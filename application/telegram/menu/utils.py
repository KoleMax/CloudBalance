from typing import List, Tuple

from application.models import Tag
from application.telegram.menu.tags.shemas import TagInfo, TagsListRenderingInfo


UNHANDLED_PROBLEM_MESSAGE = "Something went wrong. Try to het to main menu by /start command."


async def get_tags_rendering_info(project_id: int) -> List[TagsListRenderingInfo]:
    project_tags: List[Tuple[int, str]] = await Tag.get_by_project_id(project_id)

    return [
        TagsListRenderingInfo(button_title=tag_data[1], callback_data=TagInfo(id=tag_data[0], name=tag_data[1]))
        for tag_data in project_tags
    ]
