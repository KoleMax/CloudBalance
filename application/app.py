from typing import Dict, Tuple, Callable

from aiogram import Bot, Dispatcher, executor, types

from application import config


# TODO: install uvloop
class App:

    def __init__(self, bot_token: str = None):
        if not (bot_token is None):
            self.bot: Bot = Bot(token=bot_token)
            self.dispatcher: Dispatcher = Dispatcher(self.bot)
            self.command_to_handlers: Dict[Tuple[str], Callable] = {
                ("start",): self._start_message
            }
            self._setup_bot()

    def run(self):
        executor.start_polling(self.dispatcher, skip_updates=True)

    async def _start_message(self, message: types.Message):
        await message.answer('/start command mock')

    def _setup_bot(self):
        for commands, handler in self.command_to_handlers.items():
            self.dispatcher.message_handler(commands=commands)(self._start_message)


if __name__ == "__main__":
    app = App(config.settings.TELEGRAM_TOKEN)
    app.run()
