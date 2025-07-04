from aiogram import Router, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import UserLinkState, TransactionState
from keyboards.category import navigation_keyboard, build_inline_keyboard_cat
from keyboards.account import build_inline_keyboard_acc
from services.linking import get_user_profile_sync
import aiohttp
import asyncio

category_router = Router()

@category_router.callback_query(lambda c: c.data.startswith("category_"))
async def process_category_callback(callback_query: CallbackQuery, state: FSMContext):
    category = callback_query.data.split("category_")[1]
    cat, type_ = category.split("_")

    await callback_query.message.delete()
    await callback_query.answer()

    await state.update_data(selected_category=cat, category_type=await get_type(type_))

    keyboard = navigation_keyboard(category)

    await callback_query.message.answer(
        f"You have selected a category: {cat}, type: {await get_type(type_)}",
        reply_markup=keyboard
    )

async def get_type(type_: str):
    return 'spent' if type_ == 's' else 'earn' if type_ == 'e' else None

@category_router.callback_query(lambda c: c.data.startswith("back_"))
async def back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.answer()

    data = await state.get_data()
    cats = data.get("last_categories")
    cat_type = data.get("category_type")

    if cats:
        keyboard = build_inline_keyboard_cat(cats, type='s' if cat_type == 'spent' else 'e' if cat_type == 'earn' else None)
        await callback_query.message.answer("⬅️ Select the category again:", reply_markup=keyboard)
    else:
        await callback_query.message.answer("⚠️ There are no saved categories. Try again using Expense or Income.")

@category_router.callback_query(lambda c: c.data.startswith("next_"))
async def ask_for_amount(callback_query: CallbackQuery, state: FSMContext):
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

    await callback_query.message.delete()
    await callback_query.answer()

    await state.set_state(TransactionState.waiting_for_amount)
    amount_prompt = await callback_query.message.answer("Enter the amount:")
    await state.update_data(amount_prompt_message_id=amount_prompt.message_id)

@category_router.message(TransactionState.waiting_for_amount) 
async def process_amount(message: Message, state: FSMContext):
    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)
    
    if not profile or not profile.telegram_id:
        await state.set_state(UserLinkState.unlinked) 
        await message.answer(
            "Your account is not linked. Use /link <token> to link.",
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    data = await state.get_data()
    amount_prompt_message_id = data.get("amount_prompt_message_id")

    await message.delete()

    if amount_prompt_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=amount_prompt_message_id)
        except Exception as e:
            print(f"Failed to delete amount prompt message: {e}")

    amount_text = message.text
    try:
        amount = float(amount_text)
        if amount <= 0:
            await message.answer("⚠️ Please enter a positive number for the amount.")
            return

        await state.update_data(amount=amount)
        await state.set_state(TransactionState.waiting_for_account)

        url = 'http://web:8000/api/v1/accounts/'
        headers = {"Authorization": f"Bearer {profile.api_key}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    accs = data['accounts']
                    keyboard = build_inline_keyboard_acc(accs)
                    await message.answer("Select an account:", reply_markup=keyboard)
                else:
                    await message.answer("❌ Failed to fetch accounts.")
                    await state.set_state(UserLinkState.linked)

    except ValueError:
        await message.answer("⚠️ Please enter a valid number for the amount.")

@category_router.callback_query(lambda c: c.data.startswith("account_"))
async def process_account_callback(callback_query: CallbackQuery, state: FSMContext):
    account = callback_query.data.split("account_")[1]
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
        await callback_query.message.answer("⚠️ Missing transaction data. Please start over.")
        await state.set_state(UserLinkState.linked)
        return

    await callback_query.message.delete()
    await callback_query.answer()
    await callback_query.message.answer(
        f"✅ Transaction saved!\n"
        f"Category: {selected_category}\n"
        f"Type: {category_type}\n"
        f"Amount: {amount}\n"
        f"Account: {account}"
    )

    await state.set_state(UserLinkState.linked)
    await state.update_data(selected_category=None, category_type=None, amount=None)