from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    linked = State()
    unlinked = State()