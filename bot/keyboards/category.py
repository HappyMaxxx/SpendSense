from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def build_inline_keyboard_cat(categories: list[dict], type: str, row_width: int = 4) -> InlineKeyboardMarkup:
    if type in ['e', 's']:
        buttons = [
            InlineKeyboardButton(
                text=cat['icon'],
                callback_data=f"category_{cat['value']}_{type}"
            )
            for cat in categories
        ]

        buttons.append(InlineKeyboardButton(
                # text="➕",
                text="+",
                callback_data=f"create_{type}"
            ))

        keyboard_rows = [
            buttons[i:i + row_width]
            for i in range(0, len(buttons), row_width)
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
    else:
        return None
    
def navigation_keyboard(category: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data=f"back_{category}"),
            InlineKeyboardButton(text="➡️ Next", callback_data=f"next_{category}")
        ]
    ])