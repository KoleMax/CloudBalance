from aiogram import types
from aiogram.utils.callback_data import CallbackData
from enum import Enum
from typing import Callable, Dict, Tuple
from functools import wraps

from application.telegram.menu.projects.renderers import return_decorator as projects_return_decorator

from application.telegram.menu.base import MenuRenderer

from application.enums import UserRoles


class ProjectMenuCommands(Enum):
    LIST_USERS = 1
    LIST_TAGS = 2
    TRANSACTIONS = 3
    GET_TOKEN = 4
    REVOKE_TOKEN = 5
    QUICK_REPORT = 6
    DETAILED_REPORT = 7
    # TODO: delete and quit scenarios
    QUIT = 8
    DELETE = 9
    EXIT = 10


CALLBACK_DATA = CallbackData('tag_menu', 'user_id', 'project_id', 'project_name', 'command')


class ProjectMenuRenderer(MenuRenderer):

    commands: Enum = ProjectMenuCommands
    commands_with_permissions_to_text: Dict[Tuple[commands, Tuple], str] = {
        (ProjectMenuCommands.LIST_USERS, (UserRoles.ADMIN.value, UserRoles.CREATOR.value, UserRoles.USER.value)): 'List users',
        (ProjectMenuCommands.LIST_TAGS, (UserRoles.ADMIN.value, UserRoles.CREATOR.value, UserRoles.USER.value)): 'List tags',
        (ProjectMenuCommands.TRANSACTIONS, (UserRoles.ADMIN.value, UserRoles.CREATOR.value, UserRoles.USER.value)): 'Transactions',
        (ProjectMenuCommands.GET_TOKEN, (UserRoles.ADMIN.value, UserRoles.CREATOR.value)): 'Get token',
        (ProjectMenuCommands.REVOKE_TOKEN, (UserRoles.ADMIN.value, UserRoles.CREATOR.value)): 'Revoke token',
        (ProjectMenuCommands.QUICK_REPORT, (UserRoles.ADMIN.value, UserRoles.CREATOR.value)): 'Quick report',
        (ProjectMenuCommands.DETAILED_REPORT, (UserRoles.ADMIN.value, UserRoles.CREATOR.value)): 'Detailed report',
    }
    callback_data: CallbackData = CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name

    @projects_return_decorator
    def __call__(self, *args, **kwargs) -> types.InlineKeyboardMarkup:
        buttons = [self.render_button(command_to_permission[0], text) for command_to_permission, text in
                   self.commands_with_permissions_to_text.items() if self.user_role_id in command_to_permission[1]]
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*buttons)
        return markup

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(user_id=self.user_id, project_id=self.project_id,
                                      project_name=self.project_name, command=command.name)


RETURN_CALLBACK_DATA = CallbackData('back_to_project_menu', 'user_id', 'project_id', 'project_name')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int, project_id: int, project_name: str) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, project_id=project_id, project_name=project_name)
    markup.add(types.InlineKeyboardButton("Back to project menu", callback_data=callback_data))
    return markup

