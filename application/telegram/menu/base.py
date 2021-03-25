from enum import Enum
from typing import Dict, List, Any, Optional

from aiogram import types
from aiogram.utils.callback_data import CallbackData
from pydantic import BaseModel


class BaseRenderer:

    commands: Enum
    commands_to_text: Dict[Enum, str]
    callback_data: CallbackData

    def __init__(self, user_id: int):
        self.user_id = user_id

    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> types.InlineKeyboardMarkup:
        raise NotImplementedError

    def add_callback(self, command: Enum) -> str:
        raise NotImplementedError


class MenuRenderer(BaseRenderer):

    commands: Enum
    commands_to_text: Dict[Enum, str]
    callback_data: CallbackData
    row_width = 3

    def __call__(self, *args: List[Any], **kwargs: Dict[str, Any]) -> types.InlineKeyboardMarkup:
        buttons = [self.render_button(command, text) for command, text in self.commands_to_text.items()]
        markup = types.InlineKeyboardMarkup(row_width=self.row_width)
        markup.add(*buttons)
        return markup

    def render_button(self, command: Enum, text: str) -> types.InlineKeyboardButton:
        return types.InlineKeyboardButton(text, callback_data=self.add_callback(command))

    def add_callback(self, command: Enum) -> str:
        raise NotImplementedError


class ListRenderingInfo(BaseModel):
    button_title: str
    callback_data: Any


class ListRenderer(BaseRenderer):

    callback_data: CallbackData = None
    row_width = 3

    def __call__(
        self, list_data: List[ListRenderingInfo], *args: List[Any], **kwargs: Dict[str, Any]
    ) -> types.InlineKeyboardMarkup:
        buttons = [self.render_button(info.button_title, info.callback_data) for info in list_data]
        # chunkify buttons list for rendering 3 in a row
        chunks = [buttons[x : x + 3] for x in range(0, len(buttons), 3)]
        markup = types.InlineKeyboardMarkup(row_width=self.row_width)
        for buttons_chunk in chunks:
            markup.add(*buttons_chunk)
        return markup

    def render_button(self, title: str, data: Any) -> types.InlineKeyboardButton:
        return types.InlineKeyboardButton(title, callback_data=self.add_callback(data))

    def add_callback(self, data: Any) -> str:
        raise NotImplementedError
