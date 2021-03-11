from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram import Bot
from aioredis import Redis

from application.models import UsersToProjects, User
from application.telegram.menu.user.fsm import KickData
from application.telegram.menu.user.fsm import make_redis_kick_key, make_redis_change_role_key
from application.telegram.menu.user.renderers import return_button, ChoseRoleListRenderer
from application.telegram.menu.users.handlers import user_menu_handler
from application.telegram.menu.users.renderers import return_button as users_list_return_button
from application.telegram.menu.user.shemas import ChoseRoleRenderingInfo, RoleInfo

import json

DELETE_KEYWORD = 'Yes'


def make_return_handler(redis: Redis):
    async def return_handler(query: CallbackQuery):
        await user_menu_handler(query)

        chat_id = query.message.chat.id
        await redis.delete(make_redis_kick_key(chat_id), make_redis_change_role_key(chat_id))
    return return_handler


async def chose_role_handler(query: CallbackQuery):
    parsed_query_data = query.data.split(":")
    user_id = int(parsed_query_data[1])
    user_role_id = int(parsed_query_data[2])
    project_id = int(parsed_query_data[3])
    project_name = str(parsed_query_data[4])
    target_user_id = int(parsed_query_data[5])
    target_user_role_id = int(parsed_query_data[6])
    target_user_name = str(parsed_query_data[7])

    print(target_user_role_id)
    # TODO: from db
    if target_user_role_id == 3:
        roles = [
            ChoseRoleRenderingInfo(**{
                "button_title": 'Admin',
                'callback_data': RoleInfo(**{
                    'id': 2
                })
            }),
        ]
    elif target_user_role_id == 2:
        roles = [
            ChoseRoleRenderingInfo(**{
                "button_title": 'User',
                'callback_data': RoleInfo(**{
                    'id': 3
                })
            }),
        ]
    else:
        roles = []

    markup = ChoseRoleListRenderer(user_id=user_id, user_role_id=user_role_id,
                                   project_id=project_id, project_name=project_name,
                                   target_user_id=target_user_id, target_user_role_id=target_user_role_id,
                                   target_user_name=target_user_name)(roles)
    await query.message.edit_text(f"Chose role for {target_user_name}:")
    await query.message.edit_reply_markup(reply_markup=markup)


def make_set_role_handler(bot: Bot):
    async def set_role_handler(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        user_role_id = int(parsed_query_data[2])
        project_id = int(parsed_query_data[3])
        project_name = str(parsed_query_data[4])
        target_user_id = int(parsed_query_data[5])
        target_user_name = str(parsed_query_data[7])
        wanted_role_id = int(parsed_query_data[8])

        await UsersToProjects.update.values(role_id=wanted_role_id).where((UsersToProjects.user_id == target_user_id)
                                                                          & (UsersToProjects.project_id == project_id)).gino.status()

        # Notify user whos role was changed
        changed_user: User = await User.query.where(User.id == target_user_id).gino.first()
        if wanted_role_id == 2:
            await bot.send_message(changed_user.telegram_id, f"You were promoted to admin in {project_name}.")
        elif wanted_role_id == 3:
            await bot.send_message(changed_user.telegram_id, f"You were downgraded to user in {project_name}.")

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, user_role_id,
                                      project_id, project_name,
                                      target_user_id, target_user_name)

        await query.message.edit_text(f"{target_user_name}'s role was changed!")
        await query.message.edit_reply_markup(reply_markup=return_markup)

    return set_role_handler


def make_kick_handler(redis: Redis):
    async def set_kick_state(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])
        user_role_id = int(parsed_query_data[2])
        project_id = int(parsed_query_data[3])
        project_name = str(parsed_query_data[4])
        target_user_id = int(parsed_query_data[5])
        target_user_role_id = int(parsed_query_data[6])
        target_user_name = str(parsed_query_data[7])

        chat_id = int(query.message.chat.id)

        return_markup = return_button(InlineKeyboardMarkup(row_width=3), user_id, user_role_id, project_id, project_name,
                                      target_user_id, target_user_name)
        await query.message.edit_text(f"Please, type '{DELETE_KEYWORD}' if you want to kick {target_user_name} "
                                      f"from {project_name}:")
        await query.message.edit_reply_markup(reply_markup=return_markup)

        redis_data = KickData(user_id=user_id, user_role_id=user_role_id,
                              project_id=project_id, project_name=project_name,
                              target_user_id=target_user_id, target_user_name=target_user_name,)
        await redis.set(make_redis_kick_key(chat_id), redis_data.json())

    return set_kick_state


def make_kick_callback(redis: Redis, bot: Bot):
    async def kick(message: Message):
        chat_id = message.chat.id

        redis_key = make_redis_kick_key(chat_id)

        user_kick_data = await redis.get(redis_key)
        parsed_user_kick_data = KickData(**json.loads(user_kick_data))
        user_id = parsed_user_kick_data.user_id
        project_id = parsed_user_kick_data.project_id
        project_name = parsed_user_kick_data.project_name
        target_user_id = parsed_user_kick_data.target_user_id
        target_user_name = parsed_user_kick_data.target_user_name

        return_markup = users_list_return_button(InlineKeyboardMarkup(row_width=3), user_id,
                                      project_id, project_name,)

        answer = message.text
        if answer != DELETE_KEYWORD:
            await message.delete()
            return

        await UsersToProjects.delete.where((UsersToProjects.user_id == target_user_id) &
                                           (UsersToProjects.project_id == project_id)).gino.status()

        # Notify user that he was kicked)
        kicked_user: User = await User.query.where(User.id == target_user_id).gino.first()
        await bot.send_message(kicked_user.telegram_id, f"You were kicked from {project_name} by admin.")

        await redis.delete(redis_key)
        await message.answer(f"User {target_user_name} was kicked from {project_name}!", reply_markup=return_markup)

    return kick

