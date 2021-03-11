from aiogram.types import CallbackQuery

from aioredis import Redis

from application.telegram.menu.main.renderers import MainMenuRenderer

from application.telegram.menu.main.fsm import make_redis_joining_key, make_redis_creating_key

# This func is needed because we don't have upper level menu and render callback handler for main menu, only command
# respond handler. So, to return here by clicking to a button, we have to use this custom method.
# In other cases in lower level menus we can use rendering handlers from upper level.


def make_return_handler(redis: Redis):
    async def return_handler(query: CallbackQuery):
        parsed_query_data = query.data.split(":")
        user_id = int(parsed_query_data[1])

        chat_id = query.message.chat.id

        main_menu_markup = MainMenuRenderer(user_id)()
        await query.message.edit_text("Cloud balance main menu.")
        await query.message.edit_reply_markup(reply_markup=main_menu_markup)

        # We should turn off all bot interactive states, available in this menu level.
        await redis.delete(
            make_redis_joining_key(chat_id),
            make_redis_creating_key(chat_id)
        )
    return return_handler
