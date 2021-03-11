import json

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aioredis import Redis

from application.models import Tag
from application.telegram.menu.tag.fsm import RenameTagData, make_redis_rename_tag_key
from application.telegram.menu.tag.renderers import return_button
from application.telegram.menu.tags.handlers import tag_menu_handler


def make_return_handler(redis: Redis):
    async def return_handler(query: CallbackQuery):
        await tag_menu_handler(query)

        chat_id = query.message.chat.id
        await redis.delete(make_redis_rename_tag_key(chat_id))
    return return_handler


def make_rename_tag_handler(redis: Redis):
    async def set_rename_tag_state(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        project_id = int(parsed_query_data[2])
        project_name = str(parsed_query_data[3])
        tag_id = int(parsed_query_data[4])
        tag_name = str(parsed_query_data[5])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name,
                                      tag_id, tag_name)
        await query.message.edit_text(f"Please, enter new name of a tag {tag_name}:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        redis_data = RenameTagData(user_id=user_id, project_id=project_id, project_name=project_name,
                                   tag_id=tag_id, tag_name=tag_name)
        await redis.set(make_redis_rename_tag_key(chat_id), redis_data.json())

    return set_rename_tag_state


def make_rename_tag_callback(redis: Redis):
    async def rename_tag(message: Message):
        new_tag_name = message.text
        chat_id = message.chat.id

        redis_key = make_redis_rename_tag_key(chat_id)

        tag_data = await redis.get(redis_key)
        parsed_tag_data = RenameTagData(**json.loads(tag_data))
        user_id = parsed_tag_data.user_id
        project_id = parsed_tag_data.project_id
        project_name = parsed_tag_data.project_name
        tag_id = parsed_tag_data.tag_id
        tag_name = parsed_tag_data.tag_name

        await Tag.update.values(name=new_tag_name).where(Tag.id == tag_id).gino.status()

        await redis.delete(redis_key)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name,
                                      tag_id, new_tag_name)
        await message.answer(f"Tag {tag_name} was successfully renamed to {new_tag_name}!", reply_markup=return_markup)

    return rename_tag
