from aiogram.fsm.state import StatesGroup, State

class role_form(StatesGroup):
    waiting_text = State()

class message_form(StatesGroup):
    waiting_text = State()
    target = None
    message = None