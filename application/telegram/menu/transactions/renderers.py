from enum import Enum
from typing import Dict, Tuple
from typing import List

from aiogram import types
from aiogram.utils.callback_data import CallbackData

from application.enums import UserRoles
from application.telegram.menu.base import MenuRenderer, ListRenderer
from application.telegram.menu.project.renderers import return_button as project_return_button
from application.telegram.menu.tags.shemas import TagsListRenderingInfo, TagInfo
from application.telegram.menu.transactions.shemas import TransactionsListRenderingInfo, TransactionInfo


class TransactionsMenuCommands(Enum):
    ADD_INCOME = 1
    ADD_EXPENSE = 2
    LIST_TRANSACTIONS = 3


CALLBACK_DATA = CallbackData("transactions_menu", "user_id", "project_id", "project_name", "command")


class TransactionsMenuRenderer(MenuRenderer):

    commands: Enum = TransactionsMenuCommands
    commands_with_permissions_to_text: Dict[Tuple[commands, Tuple], str] = {
        (
            TransactionsMenuCommands.ADD_INCOME,
            (UserRoles.USER.value, UserRoles.ADMIN.value, UserRoles.CREATOR.value),
        ): "Add income",
        (
            TransactionsMenuCommands.ADD_EXPENSE,
            (UserRoles.USER.value, UserRoles.ADMIN.value, UserRoles.CREATOR.value),
        ): "Add expense",
        (
            TransactionsMenuCommands.LIST_TRANSACTIONS,
            (UserRoles.ADMIN.value, UserRoles.CREATOR.value),
        ): "List transactions",
    }
    callback_data: CallbackData = CALLBACK_DATA

    def __init__(self, user_id: int, user_role_id: int, project_id: int, project_name: str):
        super().__init__(user_id)
        self.user_role_id = user_role_id
        self.project_id = project_id
        self.project_name = project_name

    def __call__(self, *args, **kwargs) -> types.InlineKeyboardMarkup:
        buttons = [
            self.render_button(command_to_permission[0], text)
            for command_to_permission, text in self.commands_with_permissions_to_text.items()
            if self.user_role_id in command_to_permission[1]
        ]
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(*buttons)
        return project_return_button(markup, self.user_id, self.project_id, self.project_name)

    def add_callback(self, command: commands) -> str:
        return self.callback_data.new(
            user_id=self.user_id, project_id=self.project_id, project_name=self.project_name, command=command.name
        )


RETURN_CALLBACK_DATA = CallbackData("back_to_transactions_menu", "user_id", "project_id", "project_name")


def return_button(
    markup: types.InlineKeyboardMarkup, user_id: int, project_id: int, project_name: str
) -> types.InlineKeyboardMarkup:
    callback_data = RETURN_CALLBACK_DATA.new(user_id=user_id, project_id=project_id, project_name=project_name)
    markup.add(types.InlineKeyboardButton("Back to transactions menu", callback_data=callback_data))
    return markup


CHOSE_TAG_CALLBACK_DATA = CallbackData(
    "chose_tag_menu", "user_id", "project_id", "project_name", "transaction_type_id", "tag_id", "tag_name"
)


class ChoseTagListRenderer(ListRenderer):

    callback_data = CHOSE_TAG_CALLBACK_DATA

    def __init__(self, user_id: int, project_id: int, project_name: str, transaction_type_id: int):
        super().__init__(user_id)
        self.project_id = project_id
        self.project_name = project_name
        self.transaction_type_id = transaction_type_id

    def __call__(self, list_data: List[TagsListRenderingInfo], *args, **kwargs) -> types.InlineKeyboardMarkup:
        list_markup = super().__call__(list_data, *args, **kwargs)
        return return_button(list_markup, self.user_id, self.project_id, self.project_name)

    def add_callback(
        self,
        tag_data: TagInfo,
    ) -> str:
        return self.callback_data.new(
            user_id=self.user_id,
            project_id=self.project_id,
            project_name=self.project_name,
            transaction_type_id=self.transaction_type_id,
            tag_id=tag_data.id,
            tag_name=tag_data.name,
        )


LIST_TRANSACTIONS_CALLBACK_DATA = CallbackData(
    "transactions_list_menu",
    "user_id",
    "project_id",
    "project_name",
    "transaction_id",
)


class TransactionListRenderer(ListRenderer):

    callback_data = LIST_TRANSACTIONS_CALLBACK_DATA
    row_width = 1

    def __init__(self, user_id: int, project_id: int, project_name: str):
        super().__init__(user_id)
        self.project_id = project_id
        self.project_name = project_name

    def __call__(
        self, list_data: List[TransactionsListRenderingInfo], *args, **kwargs
    ) -> types.InlineKeyboardMarkup:
        list_markup = super().__call__(list_data, *args, **kwargs)
        return return_button(list_markup, self.user_id, self.project_id, self.project_name)

    def add_callback(
        self,
        transaction_data: TransactionInfo,
    ) -> str:
        return self.callback_data.new(
            user_id=self.user_id,
            project_id=self.project_id,
            project_name=self.project_name,
            transaction_id=transaction_data.id,
        )


LIST_TRANSACTIONS_RETURN_CALLBACK_DATA = CallbackData(
    "back_to_transactions_list", "user_id", "project_id", "project_name"
)


def list_transactions_return_button(
    markup: types.InlineKeyboardMarkup, user_id: int, project_id: int, project_name: str
) -> types.InlineKeyboardMarkup:
    callback_data = LIST_TRANSACTIONS_RETURN_CALLBACK_DATA.new(
        user_id=user_id, project_id=project_id, project_name=project_name
    )
    markup.add(types.InlineKeyboardButton("Back to transactions list", callback_data=callback_data))
    return markup
