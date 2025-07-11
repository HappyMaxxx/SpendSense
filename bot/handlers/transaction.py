from aiogram import Router, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import UserLinkState
import aiohttp
import asyncio
from services.linking import get_user_profile_sync

transaction_router = Router()

async def create_transaction(callback_query: CallbackQuery, state: FSMContext, account: str):
    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=callback_query.from_user.id)

    if not profile or not profile.telegram_id:
        await callback_query.message.delete()
        await callback_query.answer()
        await state.set_state(UserLinkState.unlinked)
        await callback_query.message.answer(
            "Your account is not linked. Use /link <token> to link.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    data = await state.get_data()
    selected_category = data.get("selected_category")
    category_type = data.get("category_type")
    amount = data.get("amount")

    if not all([selected_category, category_type, amount, account]):
        await callback_query.message.delete()
        await callback_query.answer()
        await callback_query.message.answer("⚠️ Missing transaction data. Please start over.")
        await state.set_state(UserLinkState.linked)
        return

    url = "http://web:8000/api/v1/transactions/create/"
    params = {
        "account": account,
        "category": selected_category,
        "amount": str(amount),
        "type": category_type
    }
    headers = {"Authorization": f"Bearer {profile.api_key}"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            resp_data = await response.json()
            if response.status == 200:
                if resp_data.get("status") == "ok":
                    msg = (
                        f"✅ Transaction saved!\n"
                        f"Category: {selected_category}\n"
                        f"Type: {category_type}\n"
                        f"Amount: {amount}\n"
                        f"Account: {account}"
                    )
                else:
                    msg = f"❌ Failed to save transaction: {resp_data.get('error', 'Unknown error')}"
            else:
                msg = f"❌ Failed to save transaction: {resp_data.get('error', 'Unknown error')}"

    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(msg)

    await state.set_state(UserLinkState.linked)
    await state.update_data(selected_category=None, category_type=None, amount=None)