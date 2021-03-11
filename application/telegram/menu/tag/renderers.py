from enum import Enum
from functools import wraps
from typing import Callable, Dict, Tuple

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.enums import UserRoles
from application.telegram.menu.base import MenuRenderer
from application.telegram.menu.tags.renderers import return_decorator as tags_return_decorator


class TagMenuCommands(Enum):
    RENAME = 1


CALLBACK_DATA = CallbackData('tag_menu', 'user_id', 'project_id', 'project_name', 'tag_id', 'tag_name', 'command')


class TagMenuRenderer(MenuRenderer):

    commands: Enum = TagMenuCommands
    commands_with_permissions_to_text: Dict[Tuple[commands, Tuple], str] = {
        (TagMenuCommands.RENAME, (UserRoles.ADMIN.value, UserRoles.CREATOR.value)): 'Rename',
    }
    callback_data: CallbackData = CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str, tag_id: int, tag_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name
        self.tag_id = tag_id
        self.tag_name = tag_name

    @tags_return_decorator
    def __call__(self, *args, **kwargs) -> types.InlineKeyboardMarkup:
        buttons = [self.render_button(command_to_permission[0], text) for command_to_permission, text in
                   self.commands_with_permissions_to_text.items() if self.user_role_id in command_to_permission[1]]
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*buttons)
        return markup

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(user_id=self.user_id, project_id=self.project_id, project_name=self.project_name,
                                      tag_id=self.tag_id, tag_name=self.tag_name, command=command.name)


class ReturnToProjectMenuCommand(Enum):
    RETURN = 1


RETURN_CALLBACK_DATA = CallbackData('back_to_tag_menu', 'user_id', 'project_id', 'project_name',
                                    'tag_id', 'tag_name', 'command')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int, project_id: int, project_name: str,
                  tag_id: int, tag_name: str) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, project_id=project_id,
                                             project_name=project_name, tag_id=tag_id, tag_name=tag_name,
                                             command=ReturnToProjectMenuCommand.RETURN.name)
    markup.add(types.InlineKeyboardButton("Back to tag menu", callback_data=callback_data))
    return markup
