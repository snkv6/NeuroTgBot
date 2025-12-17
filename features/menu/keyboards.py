from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

BTN_HELP = "Помощь 🫂"
BTN_PROFILE = "Посмотреть профиль ℹ️"
BTN_ROLE = "Задать роль 📝"
BTN_MODEL = "Сменить модель 👾"
BTN_BILLING = "План / оплата 💳"
BTN_CANSEL_ROLE = "Отмена ❌"

CB_HELP = "help"
CB_PROFILE = "profile"
CB_ROLE = "role"
CB_MODEL = "model"
CB_BILLING = "billing"
CB_CANSEL_ROLE = "cansel_role"

BTN_TEXTS = {BTN_HELP, BTN_PROFILE, BTN_ROLE, BTN_MODEL, BTN_BILLING, BTN_CANSEL_ROLE}
CB_TEXTS = {CB_HELP, CB_PROFILE, CB_ROLE, CB_MODEL, CB_BILLING, CB_CANSEL_ROLE}


def main_reply_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_HELP)
    kb.button(text=BTN_PROFILE)
    kb.button(text=BTN_ROLE)
    kb.button(text=BTN_MODEL)
    kb.button(text=BTN_BILLING)
    kb.adjust(2, 2, 1)
    return kb.as_markup(resize_keyboard=True)


def actions_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_HELP, callback_data=CB_HELP)
    kb.button(text=BTN_PROFILE, callback_data=CB_PROFILE)
    kb.button(text=BTN_ROLE, callback_data=CB_ROLE)
    kb.button(text=BTN_MODEL, callback_data=CB_MODEL)
    kb.button(text=BTN_BILLING, callback_data=CB_BILLING)
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def cancel_role_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_CANSEL_ROLE, callback_data=CB_CANSEL_ROLE)
    return kb.as_markup()
