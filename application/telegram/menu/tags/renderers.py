from functools import wraps
from typing import List, Callable

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.telegram.menu.base import ListRenderer
from application.telegram.menu.project.renderers import return_button as project_return_button
from application.telegram.menu.tags.shemas import TagInfo, TagsListRenderingInfo

# Have to pass user_role_id here because i want not to render menu on button click instead of rendering empty
# menu if person doesn't have permissions
CALLBACK_DATA = CallbackData(
    "tags_list", "user_id", "project_id", "project_name", "tag_id", "tag_name", "user_role_id"
)

CREATE_TAG_CALLBACK_DATA = CallbackData("create_tag", "user_id", "project_id", "project_name", "command")
CREATE_TAG_COMMAND = "create_tag"


class TagsListRenderer(ListRenderer):

    callback_data = CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name

    def __call__(self, list_data: List[TagsListRenderingInfo], *args, **kwargs) -> types.InlineKeyboardMarkup:
        list_markup = super().__call__(list_data, *args, **kwargs)
        create_tag_callback_data = CREATE_TAG_CALLBACK_DATA.new(
            user_id=self.user_id,
            project_id=self.project_id,
            project_name=self.project_name,
            command=CREATE_TAG_COMMAND,
        )
        if self.user_role_id in [1, 2]:
            list_markup.add(types.InlineKeyboardButton("+ Create tag", callback_data=create_tag_callback_data))
        return project_return_button(list_markup, self.user_id, self.project_id, self.project_name)

    def add_callback(
        self,
        tag_data: TagInfo,
    ) -> str:
        return self.callback_data.new(
            user_id=self.user_id,
            project_id=self.project_id,
            project_name=self.project_name,
            user_role_id=self.user_role_id,
            tag_id=tag_data.id,
            tag_name=tag_data.name,
        )


RETURN_TO_PROJECT_LIST_COMMAND = "return_to_projects"
RETURN_CALLBACK_DATA = CallbackData(
    "back_to_tags_list", "current_user_id", "project_id", "project_name", "command"
)


def return_button(
    markup: types.InlineKeyboardMarkup, user_id: int, project_id: int, project_name: str
) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(
        current_user_id=user_id,
        project_id=project_id,
        project_name=project_name,
        command=RETURN_TO_PROJECT_LIST_COMMAND,
    )
    markup.add(types.InlineKeyboardButton("Back to tags list", callback_data=callback_data))
    return markup


def return_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance: TagsListRenderer, *args, **kwargs) -> types.InlineKeyboardMarkup:
        markup = func(instance, *args, **kwargs)
        return return_button(markup, instance.user_id, instance.project_id, instance.project_name)

    return wrapper
