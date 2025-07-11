from aiogram.fsm.state import State, StatesGroup

class UserLinkState(StatesGroup):
    linked = State()
    unlinked = State()

class TransactionState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_account = State()

class CategoryCreationState(StatesGroup):
    waiting_for_icon = State()
    waiting_for_name = State()