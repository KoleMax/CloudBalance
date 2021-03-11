from enum import Enum
from functools import wraps
from typing import List, Callable

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.telegram.menu.base import ListRenderer
from application.telegram.menu.project.renderers import return_button as project_return_button
from application.telegram.menu.users.shemas import UserInfo, UsersListRenderingInfo


CALLBACK_DATA = CallbackData('users_list', 'current_user_id', 'current_user_role_id', 'project_id', 'project_name',
                             'user_id', 'user_name')


# Trick for not handling unwanted buttons
MOCK_CALLBACK_DATA = CallbackData('mock_callback_data', 'mock')


class UsersListRenderer(ListRenderer):

    callback_data = CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name

    def __call__(self, list_data: List[UsersListRenderingInfo], *args, **kwargs) -> types.InlineKeyboardMarkup:
        buttons = list()
        for info in list_data:
            if self.user_id == info.callback_data.id:
                buttons.append(types.InlineKeyboardButton(f'{info.button_title} (You)',
                                                          callback_data=MOCK_CALLBACK_DATA.new(mock=True)))
                continue
            button_title = info.button_title
            # TODO: enum
            if info.callback_data.role_id == 1:
                button_title += ' (Creator)'
            elif info.callback_data.role_id == 2:
                button_title += ' (Admin)'
            if self.user_role_id <= info.callback_data.role_id:
                buttons.append(self.render_button(button_title, info.callback_data))
            else:
                buttons.append(types.InlineKeyboardButton(button_title,
                                                          callback_data=MOCK_CALLBACK_DATA.new(mock=True)))

        # chunkify buttons list for rendering 3 in a row
        chunks = [buttons[x:x + 3] for x in range(0, len(buttons), 3)]
        markup = types.InlineKeyboardMarkup(row_width=3)
        for buttons_chunk in chunks:
            markup.add(*buttons_chunk)
        return project_return_button(markup, self.user_id, self.project_id, self.project_name)

    def add_callback(self, user_data: UserInfo, ) -> str:
        return self.callback_data.new(current_user_id=self.user_id,
                                      current_user_role_id=self.user_role_id,
                                      project_id=self.project_id,
                                      project_name=self.project_name,
                                      user_id=user_data.id,
                                      user_name=user_data.name
                                      )


RETURN_CALLBACK_DATA = CallbackData('back_to_users_list', 'current_user_id', 'project_id', 'project_name')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int,
                  project_id: int, project_name: str) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(current_user_id=user_id, project_id=project_id,
                                             project_name=project_name)
    markup.add(types.InlineKeyboardButton("Back to users list", callback_data=callback_data))
    return markup


# TODO: remove fucking decorator everywhere, use overload and return_button instead
def return_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance: UsersListRenderer, *args, **kwargs) -> types.InlineKeyboardMarkup:
        markup = func(instance, *args, **kwargs)
        return return_button(markup, instance.user_id, instance.project_id, instance.project_name)
    return wrapper
