from aiogram import types

from services import link_account, unlink_account

async def link_handler(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide a link token. Usage: /link <token>")
        return

    token = args[1].strip()
    await link_account(token, message)

async def unlink_handler(message: types.Message):
    await unlink_account(message)