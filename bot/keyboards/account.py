from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def build_inline_keyboard_acc(accounts: list[dict], row_width: int = 2) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=acc['name'],
            callback_data=f"account_{acc['name']}"
        )
        for acc in accounts
    ]

    keyboard_rows = [
        buttons[i:i + row_width]
        for i in range(0, len(buttons), row_width)
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)