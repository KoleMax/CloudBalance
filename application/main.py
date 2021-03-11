import asyncio

import aioredis
import redis
import uvloop
from aiogram import Bot, Dispatcher, executor, types

from application import db
from application.config import environment
from application.models import User
from application.telegram.menu.main import renderers as main_renderers
from application.telegram.menu.main import router as main_router
from application.telegram.menu.main_settings import router as main_settings_router
from application.telegram.menu.project import router as project_router
from application.telegram.menu.projects import router as projects_router
from application.telegram.menu.tag import router as tag_router
from application.telegram.menu.tags import router as tags_router
from application.telegram.menu.transactions import router as transactions_router
from application.telegram.menu.user import router as user_router
from application.telegram.menu.users import router as users_router


class App:

    def __init__(self):
        uvloop.install()
        self.db = db
        self.sync_r = redis.Redis(host='redis', port=6379, db=0)
        if environment.settings.TELEGRAM_TOKEN:
            self.bot: Bot = Bot(token=environment.settings.TELEGRAM_TOKEN)
            self.dispatcher: Dispatcher = Dispatcher(self.bot)

            self.project_menu_handlers = {

            }

    async def _db_connect(self):
        await self.db.connect()
        await self.db.is_alive()

    async def _redis_connect(self):
        # TODO: redis config
        self.r = await aioredis.create_redis_pool(
            "redis://redis", minsize=5, maxsize=10, loop=asyncio.get_event_loop()
        )

    def run(self):
        el = asyncio.get_event_loop()
        el.run_until_complete(self._db_connect())
        el.run_until_complete(self._redis_connect())
        self._setup()
        executor.start_polling(self.dispatcher, skip_updates=True)

    # TODO: Redis FSM dialog
    async def _login(self, message: types.Message):
        username = message.text.split()[1]
        u = User(telegram_id=message.chat.id, name=username)
        await u.create()
        await message.answer(f"You successfully signed up.")
        await self._start_handler(message)

    @staticmethod
    async def _start_handler(message: types.Message):
        user_tg_id = message.chat.id

        user = await User.query.where(User.telegram_id == user_tg_id).gino.first()

        if user is None:
            await message.answer("Looks like you are not logged in yet.\nType /login yourname to sign up.")
            return

        main_menu_markup = main_renderers.MainMenuRenderer(user_id=user.id)()
        await message.answer("Cloud balance main menu.", reply_markup=main_menu_markup)

    def _setup(self):
        self.dispatcher.message_handler(commands=("start",))(self._start_handler)
        self.dispatcher.message_handler(commands=("login",))(self._login)
        main_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        projects_router.configure_dispatcher(self.dispatcher)
        project_router.configure_dispatcher(self.dispatcher, self.db)
        tags_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        tag_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        main_settings_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        users_router.configure_dispatcher(self.dispatcher)
        user_router.configure_dispatcher(self.dispatcher, self.bot, self.r, self.sync_r)
        transactions_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
