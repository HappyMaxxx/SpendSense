'''
Linked user keyboard handlers
'''
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from services.linking import get_user_profile_sync
from states import UserState

async def keyboard_buttons_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)

    if current_state == UserState.linked and profile and profile.telegram_id:
        if message.text == "Profile":
            await message.answer(f"Your profile: {profile.user.username}")
        elif message.text == "Expense":
            await message.answer("You selected Expense. Enter expense details.") 
        elif message.text == "Income":
            await message.answer("You selected Income. Enter income details.")
    else:
        await state.set_state(UserState.unlinked)
        await message.answer(
            "Your account is not linked. Use /link <token> to link.",
            reply_markup=types.ReplyKeyboardRemove()
        )