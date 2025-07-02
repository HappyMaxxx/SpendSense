from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.category import navigation_keyboard, build_inline_keyboard

category_router = Router()

@category_router.callback_query(lambda c: c.data.startswith("category_"))
async def process_category_callback(callback_query: CallbackQuery):
    category = callback_query.data.split("category_")[1]
    cat, type = category.split("_")

    await callback_query.message.delete()
    await callback_query.answer()

    keyboard = navigation_keyboard(category)

    await callback_query.message.answer(
        f"You have selected a category: {cat}, type: {await get_type(type)}",
        reply_markup=keyboard
    )

async def get_type(type: str):
    return 'spent' if type == 's' else 'earn' if type == 'e' else None

@category_router.callback_query(lambda c: c.data.startswith("back_"))
async def back_to_categories(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.answer()

    data = await state.get_data()
    cats = data.get("last_categories")
    cat_type = data.get("category_type")

    if cats:
        keyboard = build_inline_keyboard(cats, type='s' if cat_type == 'spent' else 'e' if cat_type == 'earn' else None)
        await callback_query.message.answer("⬅️ Select the category again:", reply_markup=keyboard)
    else:
        await callback_query.message.answer("⚠️ There are no saved categories. Try again using Expense or Income.")


@category_router.callback_query(lambda c: c.data.startswith("next_"))
async def ask_for_amount(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.answer()

    await callback_query.message.answer("Enter the amount:")