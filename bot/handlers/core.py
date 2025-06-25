from aiogram import types
from aiogram.filters.command import CommandObject

from services import link_account

async def start_handler(message: types.Message, command: CommandObject):
    if command.args:
        token = command.args
        await link_account(token, message)
        return

    await message.answer("Hello! I will start working very soon!")
    
async def help_handler(message: types.Message):
    await message.answer("This is help on command...")