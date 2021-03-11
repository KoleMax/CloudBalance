from enum import Enum
from functools import wraps
from typing import Callable, Dict

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.telegram.menu.base import MenuRenderer


class MainMenuCommands(Enum):
    NEW = 1
    PROJECTS = 2
    JOIN = 3
    SETTINGS = 4


CALLBACK_DATA = CallbackData('main_menu', 'user_id', 'command')


class MainMenuRenderer(MenuRenderer):

    commands: Enum = MainMenuCommands
    commands_to_text: Dict[commands, str] = {
        MainMenuCommands.NEW: "Create project",
        MainMenuCommands.PROJECTS: "My projects",
        MainMenuCommands.JOIN: "Join",
        MainMenuCommands.SETTINGS: "Settings",
    }
    callback_data: CallbackData = CALLBACK_DATA
    row_width = 1

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(user_id=self.user_id, command=command.name)


class ReturnToMainMenuCommand(Enum):
    RETURN = 1


RETURN_CALLBACK_DATA = CallbackData('back_to_main_menu', 'user_id', 'command')


def return_button(markup: types.InlineKeyboardMarkup, user_id: int) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, command=ReturnToMainMenuCommand.RETURN.name)
    markup.add(types.InlineKeyboardButton("Back to main menu", callback_data=callback_data))
    return markup


def return_decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(instance: MenuRenderer, *args, **kwargs) -> types.InlineKeyboardMarkup:
        markup = func(instance, *args, **kwargs)
        return return_button(markup, instance.user_id)
    return wrapper

