import json

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aioredis import Redis

from application.models import User
from application.telegram.menu.main_settings.fsm import ChangeNicknameData, make_redis_change_nickname_key
from application.telegram.menu.main_settings.renderers import return_button


def make_change_nickname_handler(redis: Redis):
    async def set_join_to_project_state(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await query.message.edit_text("Please, enter your new nickname:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        redis_data = ChangeNicknameData(user_id=user_id)
        await redis.set(make_redis_change_nickname_key(chat_id), redis_data.json())

    return set_join_to_project_state


def make_change_nickname_callback(redis: Redis):
    async def change_nickname(message: Message):
        nickname = message.text
        chat_id = message.chat.id

        redis_key = make_redis_change_nickname_key(chat_id)
        user_data = await redis.get(redis_key)
        parsed_user_data = ChangeNicknameData(**json.loads(user_data))
        user_id = parsed_user_data.user_id

        await User.update.values(name=nickname).where(User.id == user_id).gino.status()

        await redis.delete(redis_key)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id)
        await message.answer(f"You successfully changed your nickname to {nickname}!", reply_markup=return_markup)

    return change_nickname

