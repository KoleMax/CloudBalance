from enum import Enum
from typing import Dict, Tuple, List

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from pydantic import BaseModel

from application.enums import UserRoles
from application.telegram.menu.base import MenuRenderer, ListRenderer
from application.telegram.menu.users.renderers import return_button as users_return_button

from application.telegram.menu.user.shemas import ChoseRoleRenderingInfo, RoleInfo


class UserMenuCommands(Enum):
    CHANGE_ROLE = 1
    KICK = 2


# TODO: hash or remove
class CommandToPermission(BaseModel):
    command: UserMenuCommands
    permissions: Tuple[int, ...]

    def __hash__(self):
        return hash(self.command)


CALLBACK_DATA = CallbackData('user_menu', 'current_user_id', 'current_user_role_id', 'project_id', 'project_name',
                             'user_id', 'user_role_id', 'user_name', 'command')


class UserMenuRenderer(MenuRenderer):

    commands: Enum = UserMenuCommands
    commands_with_permissions_to_text: Dict[CommandToPermission, str] = {
        CommandToPermission(**{"command": UserMenuCommands.CHANGE_ROLE,
                               "permissions": (UserRoles.ADMIN.value, UserRoles.CREATOR.value)}): 'Change role',
        CommandToPermission(**{"command": UserMenuCommands.KICK, "permissions": (UserRoles.CREATOR.value, UserRoles.ADMIN.value)}): 'Kick',
    }
    callback_data: CallbackData = CALLBACK_DATA

    def __init__(self, current_user_id: int, current_user_role_id: int,
                 project_id: int, project_name: str,
                 target_user_id: int, target_user_role_id: int, target_user_name: str):
        super().__init__(current_user_id)
        self.user_role_id = current_user_role_id
        self.project_id = project_id
        self.project_name = project_name
        self.target_user_id = target_user_id
        self.target_user_role_id = target_user_role_id
        self.target_user_name = target_user_name

    def __call__(self, *args, **kwargs) -> types.InlineKeyboardMarkup:
        buttons = [self.render_button(command_to_permission.command, text) for command_to_permission, text in
                   self.commands_with_permissions_to_text.items()
                   if self.user_role_id in command_to_permission.permissions]

        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*buttons)
        return users_return_button(markup, self.user_id, self.project_id, self.project_name)

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(
            current_user_id=self.user_id, current_user_role_id=self.user_role_id,
            project_id=self.project_id, project_name=self.project_name,
            user_id=self.target_user_id, user_role_id=self.target_user_role_id, user_name=self.target_user_name,
            command=command.name)


RETURN_CALLBACK_DATA = CallbackData('back_to_user_menu', 'current_user_id', 'current_user_role_id', 'project_id',
                                    'project_name', 'user_id', 'user_name')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int, user_role_id: int,
                  project_id: int, project_name: str,
                  target_user_id: int, target_user_name: str) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(
        current_user_id=user_id, current_user_role_id=user_role_id,
        project_id=project_id, project_name=project_name,
        user_id=target_user_id, user_name=target_user_name)
    markup.add(types.InlineKeyboardButton("Back to user menu", callback_data=callback_data))
    return markup


CHOSE_ROLE_CALLBACK_DATA = CallbackData('chose_role_menu', 'current_user_id', 'current_user_role_id',
                                        'project_id', 'project_name', 'user_id', 'user_role_id', 'user_name',
                                        'wanted_role_id')


class ChoseRoleListRenderer(ListRenderer):

    callback_data = CHOSE_ROLE_CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str, target_user_id: int,
                 target_user_role_id: int, target_user_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name
        self.target_user_id = target_user_id
        self.target_user_role_id = target_user_role_id
        self.target_user_name = target_user_name

    def __call__(self, list_data: List[ChoseRoleRenderingInfo], *args, **kwargs) -> types.InlineKeyboardMarkup:
        list_markup = super().__call__(list_data, *args, **kwargs)
        return return_button(list_markup, self.user_id, self.user_role_id, self.project_id, self.project_name,
                             self.target_user_id, self.target_user_name)

    def add_callback(self, role_data: RoleInfo, ) -> str:
        return self.callback_data.new(
            current_user_id=self.user_id,
            current_user_role_id=self.user_role_id,
            project_id=self.project_id,
            project_name=self.project_name,
            user_id=self.target_user_id,
            user_role_id=self.target_user_role_id,
            user_name=self.target_user_name,
            wanted_role_id=role_data.id
        )