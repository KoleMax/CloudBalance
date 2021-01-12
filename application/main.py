from typing import Dict, Tuple, Callable
import asyncio
from aiogram import Bot, Dispatcher, executor, types

from application import db
from application.config import environment


class App:
    def __init__(self):  # TODO: install uvloop
        if environment.settings.TELEGRAM_TOKEN:
            self.bot: Bot = Bot(token=environment.settings.TELEGRAM_TOKEN)
            self.dispatcher: Dispatcher = Dispatcher(self.bot)
            self.command_to_handlers: Dict[Tuple[str], Callable] = {("start",): self._start_message}
            self._setup_bot()
        db_settings = db.database_config_from_app_config(environment.settings)
        self.db = db.get_database(db_settings)

    async def _db_connect(self):
        await self.db.connect()
        await self.db.is_alive()

    def run(self):
        el = asyncio.get_event_loop()
        el.run_until_complete(self._db_connect())
        executor.start_polling(self.dispatcher, skip_updates=True)

    async def _start_message(self, message: types.Message):
        await message.answer("/start command mock")
        await message.answer(f"db response: {await self.db.scalar('SELECT 1')}")

    def _setup_bot(self):
        for commands, handler in self.command_to_handlers.items():
            self.dispatcher.message_handler(commands=commands)(handler)

