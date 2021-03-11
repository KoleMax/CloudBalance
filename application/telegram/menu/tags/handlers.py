import json

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aioredis import Redis

from application.models import Tag
from application.models import UsersToProjects
from application.telegram.menu.project.handlers import tags_handler
from application.telegram.menu.tag.renderers import TagMenuRenderer
from application.telegram.menu.tags.fsm import CreateTagData, make_redis_create_tag_key
from application.telegram.menu.tags.renderers import return_button


def make_return_handler(redis: Redis):
    async def return_handler(query: CallbackQuery):
        await tags_handler(query)

        chat_id = query.message.chat.id
        await redis.delete(make_redis_create_tag_key(chat_id))
    return return_handler


def make_create_tag_handler(redis: Redis):
    async def set_create_tag_state(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        project_id = int(parsed_query_data[2])
        project_name = str(parsed_query_data[3])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name)
        await query.message.edit_text(f"Please, enter name of a tag you want to create for {project_name}:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        # set fsm to join to project dialog and save user data to redis
        redis_data = CreateTagData(user_id=user_id, project_id=project_id, project_name=project_name)
        await redis.set(make_redis_create_tag_key(chat_id), redis_data.json())

    return set_create_tag_state


def make_create_tag_callback(redis: Redis):
    async def create_tag(message: Message):
        tag_name = message.text
        chat_id = message.chat.id

        redis_key = make_redis_create_tag_key(chat_id)

        tag_data = await redis.get(redis_key)
        parsed_tag_data = CreateTagData(**json.loads(tag_data))
        user_id = parsed_tag_data.user_id
        project_id = parsed_tag_data.project_id
        project_name = parsed_tag_data.project_name

        new_tag = Tag(name=tag_name, project_id=project_id)
        await new_tag.create()

        await redis.delete(redis_key)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, project_id, project_name)
        await message.answer(f"Tag {tag_name} was successfully created!", reply_markup=return_markup)

    return create_tag


async def tag_menu_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    project_id = int(parsed_query_data[2])
    project_name = str(parsed_query_data[3])
    tag_id = int(parsed_query_data[4])
    tag_name = str(parsed_query_data[5])

    user_role_id = await UsersToProjects.get_user_role_id_in_project(user_id, project_id)

    project_menu_markup = TagMenuRenderer(user_id, user_role_id, project_id, project_name, tag_id, tag_name)()
    await query.message.edit_text(f"Tag {tag_name} menu.")
    await query.message.edit_reply_markup(reply_markup=project_menu_markup)

