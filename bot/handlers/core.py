import asyncio
from aiogram import types
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from services.linking import get_user_profile_sync
from keyboards.main import get_linked_user_keyboard
from states import UserLinkState, TransactionState

async def start_handler(message: types.Message, command: CommandObject, state: FSMContext):
    if command.args:
        token = command.args
        from services.linking import link_account
        await link_account(token, message, state)
        return

    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)
    
    if profile and profile.telegram_id:
        await state.set_state(UserLinkState.linked)
        await message.answer(
            f"Welcome back, {profile.user.username}! What would you like to do?",
            reply_markup=get_linked_user_keyboard()
        )
    else:
        await state.set_state(UserLinkState.unlinked)
        await message.answer(
            "Hello! Please link your account using /link <token> to get started.",
            reply_markup=types.ReplyKeyboardRemove()
        )

async def help_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    reply_markup = get_linked_user_keyboard() if current_state == UserLinkState.linked else types.ReplyKeyboardRemove()
    await message.answer("This is help on commands...", reply_markup=reply_markup)

async def text_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == TransactionState.waiting_for_amount:
        return
    
    profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)
    
    if current_state == UserLinkState.linked and profile and profile.telegram_id:
        await message.answer(
            "Choose an action:",
            reply_markup=get_linked_user_keyboard()
        )
    else:
        await state.set_state(UserLinkState.unlinked)
        await message.answer(
            "Your account is not linked. Use /link <token> to link.",
            reply_markup=types.ReplyKeyboardRemove()
        )