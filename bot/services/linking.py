import logging
import asyncio
from aiogram import types
from django.db import transaction

from finance.models import UserProfile

logger = logging.getLogger(__name__)

def get_user_profile_sync(token: str = None, tg_id: int = None):
    try:
        if token is not None:
            return UserProfile.objects.get(api_key=token)
        elif tg_id is not None:
            return UserProfile.objects.get(telegram_id=tg_id)
        else:
            return None
    except UserProfile.DoesNotExist:
        return None

def is_profile_linked_sync(profile):
    return profile.telegram_id is not None

@transaction.atomic
def link_profile_to_telegram_sync(profile, telegram_id):
    profile.telegram_id = telegram_id
    profile.save()
    return profile

@transaction.atomic
def unlink_profile_to_telegram_sync(profile):
    profile.telegram_id = None
    profile.save()
    return profile

async def link_account(token: str, message: types.Message):
    try:
        profile = await asyncio.to_thread(get_user_profile_sync, token=token)
        
        if profile is None:
            await message.answer("Invalid or expired token. Please generate a new token from the SpendSense website.")
            return

        is_linked = await asyncio.to_thread(is_profile_linked_sync, profile)
        if is_linked:
            await message.answer("This account is already linked to a Telegram account.")
            return

        updated_profile = await asyncio.to_thread(link_profile_to_telegram_sync, profile, message.from_user.id)
        await message.answer(f"Success! Your Telegram account is now linked to {updated_profile.user.username}.")

    except Exception as e:
        logger.error(f"Error during linking: {e}")
        await message.answer("An error occurred while linking your account. Please try again later.")

async def unlink_account(message: types.Message):
    try:
        profile = await asyncio.to_thread(get_user_profile_sync, tg_id=message.from_user.id)
        
        if profile is None:
            await message.answer("You're not even linked!")
            return

        updated_profile = await asyncio.to_thread(unlink_profile_to_telegram_sync, profile)
        await message.answer(f"Success! Your Telegram account has been disconnected from {updated_profile.user.username}.")

    except Exception as e:
        logger.error(f"Error during linking: {e}")
        await message.answer("An error occurred while linking your account. Please try again later.")