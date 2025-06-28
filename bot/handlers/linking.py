from aiogram import types
from aiogram.fsm.context import FSMContext
from services.linking import link_account, unlink_account
from keyboards.main import get_linked_user_keyboard

from states import UserState

async def link_handler(message: types.Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide a link token. Usage: /link <token>")
        current_state = await state.get_state()
        reply_markup = get_linked_user_keyboard() if current_state == UserState.linked else types.ReplyKeyboardRemove()
        await message.answer("Use /link <token> to link your account.", reply_markup=reply_markup)
        return

    token = args[1].strip()
    await link_account(token, message, state)

async def unlink_handler(message: types.Message, state: FSMContext):
    await unlink_account(message, state)