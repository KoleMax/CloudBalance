from enum import Enum
from functools import wraps
from typing import Callable, Dict

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from application.telegram.menu.main import renderers as main_renderers

from application.telegram.menu.base import MenuRenderer


class MainSettingsMenuCommands(Enum):
    CHANGE_NICKNAME = "change_nickname"


CALLBACK_DATA = CallbackData("main_menu_settings", "user_id", "command")


class MainSettingsMenuRenderer(MenuRenderer):

    commands: Enum = MainSettingsMenuCommands
    commands_to_text: Dict[commands, str] = {
        MainSettingsMenuCommands.CHANGE_NICKNAME: "Change nickname",
    }
    callback_data: CallbackData = CALLBACK_DATA
    row_width = 1

    @main_renderers.return_decorator
    def __call__(self, *args, **kwargs) -> types.InlineKeyboardMarkup:
        return super().__call__(*args, **kwargs)

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(user_id=self.user_id, command=command.name)


class ReturnToMainSettingsMenuCommand(Enum):
    RETURN = 1


RETURN_CALLBACK_DATA = CallbackData("back_to_main_menu_settings", "user_id", "command")


def return_button(markup: types.InlineKeyboardMarkup, user_id: int) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, command=ReturnToMainSettingsMenuCommand.RETURN.name)
    markup.add(types.InlineKeyboardButton("Back to settings", callback_data=callback_data))
    return markup


def return_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance: MenuRenderer, *args, **kwargs) -> types.InlineKeyboardMarkup:
        markup = func(instance, *args, **kwargs)
        return return_button(markup, instance.user_id)

    return wrapper
