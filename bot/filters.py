from aiogram.filters import BaseFilter
from aiogram.types import Message

class Text(BaseFilter):
    def __init__(self, text: list[str] | str):
        if isinstance(text, str):
            text = [text]
        self.text_set = set(map(str.lower, text))

    async def __call__(self, message: Message) -> bool:
        return (
            message.text is not None and
            message.text.lower() in self.text_set
        )