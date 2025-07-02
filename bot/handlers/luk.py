'''
Linked user keyboard handlers
'''
import asyncio
import aiohttp
from aiogram import types
from aiogram.fsm.context import FSMContext
from services.linking import get_user_profile_sync
from states import UserState
from keyboards.category import build_inline_keyboard

async def keyboard_buttons_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)

    if current_state == UserState.linked and profile and profile.telegram_id:
        if message.text == "Profile":
            await profile_handler(message, profile)
        elif message.text == "Expense":
            await expense_handler(message, profile, state)
        elif message.text == "Income":
            await income_handler(message, profile, state)
    else:
        await state.set_state(UserState.unlinked)
        await message.answer(
            "Your account is not linked. Use /link <token> to link.",
            reply_markup=types.ReplyKeyboardRemove()
        )

async def profile_handler(message: types.Message, profile):
    url = 'http://web:8000/api/v1/profile-data/'
    headers = {
        "Authorization": f"Bearer {profile.api_key}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                text = (
                        f"<b>{profile.user.username}</b>\n"
                        f"You use <b>SpendSens</b> since <b>{profile.user.date_joined.strftime('%B %d, %Y')}</b>.\n"
                        f"You've <b>spent</b> <code>{data['total_all_spending']}₴</code>\n"
                        f"You've <b>earned</b> <code>{data['total_all_earning']}₴</code>\n"
                        f"Overall balance change: <b>{data['total_all_diff']}₴</b>"
                    )
                await message.answer(text, parse_mode="HTML")
            else:
                await message.answer("❌ Failed to get profile data.")

from aiogram.fsm.context import FSMContext

async def expense_handler(message: types.Message, profile, state: FSMContext):
    url = 'http://web:8000/api/v1/categories/get/'
    headers = {"Authorization": f"Bearer {profile.api_key}"}
    params = {'type': 'spent'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                cats = data['categories']

                await state.update_data(last_categories=cats, category_type='spent')

                keyboard = build_inline_keyboard(cats, type='s', )
                await message.answer("Select a category:", reply_markup=keyboard)
            else:
                await message.answer("❌ Failed to get spent categories.")



async def income_handler(message: types.Message, profile, state: FSMContext):
    url = 'http://web:8000/api/v1/categories/get/'
    headers = {
        "Authorization": f"Bearer {profile.api_key}"
    }
    params = {
        'type': 'earn'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                cats = data['categories']

                await state.update_data(last_categories=cats, category_type='earn')

                keyboard = build_inline_keyboard(cats, type='e')
                await message.answer("Select a category:", reply_markup=keyboard)
            else:
                await message.answer("❌ Failed to get spent categories.")