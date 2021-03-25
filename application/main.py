import asyncio


import aioredis
import redis
import uvloop
from aiogram import Bot, Dispatcher, executor, types

from application import db
from application.config import environment, logging
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


logger = logging.get_app_logger()


class App:
    def __init__(self):
        # logging
        logging.configure_logging()
        # Using uvloop for better performance
        uvloop.install()
        self.db = db
        self.sync_r = redis.Redis(
            host=environment.settings.REDIS_HOST,
            port=environment.settings.REDIS_PORT,
            db=environment.settings.REDIS_DB,
        )
        if not environment.settings.TELEGRAM_TOKEN:
            raise Exception("Telegram token should be provided")
        self.bot: Bot = Bot(token=environment.settings.TELEGRAM_TOKEN)
        self.dispatcher: Dispatcher = Dispatcher(self.bot)

    async def _db_connect(self):
        await self.db.connect()

    async def _redis_connect(self):
        self.r = await aioredis.create_redis_pool(
            f"redis://{environment.settings.REDIS_HOST}:{environment.settings.REDIS_PORT}",
            minsize=environment.settings.REDIS_POOL_MIN_SIZE,
            maxsize=environment.settings.REDIS_POOL_MAX_SIZE,
            db=environment.settings.REDIS_DB,
            loop=asyncio.get_event_loop(),
        )

    def run(self):
        self._setup()
        executor.start_polling(self.dispatcher, skip_updates=True)

    def _setup(self):
        el = asyncio.get_event_loop()
        el.run_until_complete(self._db_connect())
        el.run_until_complete(self._redis_connect())

        self._configure_dispatcher()

    def _configure_dispatcher(self):
        # commands
        self.dispatcher.message_handler(commands=("start",))(self._start_handler)
        self.dispatcher.message_handler(commands=("login",))(self._login)

        # menus
        main_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r, self.db)
        projects_router.configure_dispatcher(self.dispatcher)
        project_router.configure_dispatcher(self.dispatcher, self.db)
        tags_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        tag_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        main_settings_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)
        users_router.configure_dispatcher(self.dispatcher)
        user_router.configure_dispatcher(self.dispatcher, self.bot, self.r, self.sync_r)
        transactions_router.configure_dispatcher(self.dispatcher, self.r, self.sync_r)

    async def _login(self, message: types.Message) -> None:
        username = message.text.split()[1]
        user = User(telegram_id=message.chat.id, name=username)
        await user.create()
        logger.info(f"New user signed in", extra={"telegram_id": message.chat.id})
        await message.answer(f"You successfully signed up.")
        await self._start_handler(message)

    @staticmethod
    async def _start_handler(message: types.Message) -> None:
        user_tg_id = message.chat.id
        user = await User.query.where(User.telegram_id == user_tg_id).gino.first()

        if user is None:
            await message.answer("Looks like you are not logged in yet.\nType /login yourname to sign up.")
            return

        main_menu_markup = main_renderers.MainMenuRenderer(user_id=user.id)()
        await message.answer("Cloud balance main menu.", reply_markup=main_menu_markup)
