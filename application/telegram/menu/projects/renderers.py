from enum import Enum
from functools import wraps
from typing import List, Callable

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.telegram.menu.base import ListRenderer
from application.telegram.menu.main import renderers as main_renderers
from application.telegram.menu.projects.shemas import ProjectInfo, ProjectsListRenderingInfo

CALLBACK_DATA = CallbackData('projects_list', 'user_id', 'project_id', 'project_name')


class ProjectsListRenderer(ListRenderer):

    callback_data = CALLBACK_DATA

    @main_renderers.return_decorator
    def __call__(self, list_data: List[ProjectsListRenderingInfo], *args, **kwargs) -> types.InlineKeyboardMarkup:
        return super().__call__(list_data, *args, **kwargs)

    def add_callback(self, project_data: ProjectInfo) -> str:
        return self.callback_data.new(user_id=self.user_id, project_id=project_data.id, project_name=project_data.name)


class ReturnToProjectsListCommand(Enum):
    RETURN = 1


RETURN_CALLBACK_DATA = CallbackData('back_to_projects_list', 'user_id', 'command')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, command=ReturnToProjectsListCommand.RETURN.name)
    markup.add(types.InlineKeyboardButton("Back to projects list", callback_data=callback_data))
    return markup


def return_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance: ProjectsListRenderer, *args, **kwargs) -> types.InlineKeyboardMarkup:
        markup = func(instance, *args, **kwargs)
        return return_button(markup, instance.user_id)
    return wrapper
