from aiogram import types
from aiogram.filters import Command

async def start_handler(message: types.Message):
    await message.answer("Hello! I will start working very soon")

async def help_handler(message: types.Message):
    await message.answer("This is help on command...")