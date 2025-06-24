import os
import django
import sys
from decouple import config
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import asyncio
import logging

from handlers import start_handler, help_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append("/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spendsense.settings")
django.setup()

BOT_TOKEN = config('BOT_TOKEN', default=None)
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is not set in the .env file. Exiting...")
    sys.exit(1) 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

commands = [
    types.BotCommand(command="start", description="Get started"),
    types.BotCommand(command="help", description="Get help"),
]

async def on_startup():
    await bot.set_my_commands(commands)

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(help_handler, Command(commands=["help"]))

async def main():
    try:
        await on_startup()
        register_handlers(dp)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
