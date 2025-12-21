from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

BTN_HELP = "Помощь 🫂"
BTN_PROFILE = "Посмотреть профиль ℹ️"
BTN_ROLE = "Задать / удалить роль 📝"
BTN_MODEL = "Сменить модель 👾"
BTN_BILLING = "План / оплата 💳"
BTN_DELETE_CONTEXT = "Удалить текущий контекст 🔄"

BTN_CANSEL_ROLE = "Отмена ❌"
BTN_DELETE_ROLE = "Удалить роль ⛔"

BTN_PREMIUM_30D = "30 дней"
BTN_PREMIUM_365D = "365 дней"

BTN_TEXTS = {BTN_HELP, BTN_PROFILE, BTN_ROLE, BTN_MODEL, BTN_BILLING, BTN_DELETE_CONTEXT}

CB_HELP = "help"
CB_PROFILE = "profile"
CB_ROLE = "role"
CB_MODEL = "model"
CB_BILLING = "billing"
CB_DELETE_CONTEXT = "delete_context"

CB_CANSEL_ROLE = "cansel_role"
CB_DELETE_ROLE = "delete_role"

CB_PREMIUM_START = "buy:"
CB_PREMIUM_30D = "30"
CB_PREMIUM_365D = "365"

def main_reply_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_HELP)
    kb.button(text=BTN_PROFILE)
    kb.button(text=BTN_ROLE)
    kb.button(text=BTN_MODEL)
    kb.button(text=BTN_BILLING)
    kb.button(text=BTN_DELETE_CONTEXT)
    kb.adjust(2, 2, 2)
    return kb.as_markup(resize_keyboard=True)


def actions_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_HELP, callback_data=CB_HELP)
    kb.button(text=BTN_PROFILE, callback_data=CB_PROFILE)
    kb.button(text=BTN_ROLE, callback_data=CB_ROLE)
    kb.button(text=BTN_MODEL, callback_data=CB_MODEL)
    kb.button(text=BTN_BILLING, callback_data=CB_BILLING)
    kb.button(text=BTN_DELETE_CONTEXT, callback_data=CB_DELETE_CONTEXT)
    kb.adjust(1, 1, 1, 1, 1, 1)
    return kb.as_markup()


def special_role_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_CANSEL_ROLE, callback_data=CB_CANSEL_ROLE)
    kb.button(text=BTN_DELETE_ROLE, callback_data=CB_DELETE_ROLE)
    kb.adjust(2)
    return kb.as_markup()

def premium_options_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_PREMIUM_30D, callback_data=CB_PREMIUM_START+CB_PREMIUM_30D)
    kb.button(text=BTN_PREMIUM_365D, callback_data=CB_PREMIUM_START+CB_PREMIUM_365D)
    kb.adjust(2)
    return kb.as_markup()
