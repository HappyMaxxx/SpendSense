from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_linked_user_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Profile")],
            [KeyboardButton(text="Expense"), KeyboardButton(text="Income")]
        ],
        resize_keyboard=True
    )