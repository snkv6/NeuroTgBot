from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from src.config.const import MODELS
from src.database.users import check_premium, get_model

BTN_HELP = "Помощь 🫂"
BTN_PROFILE = "Посмотреть профиль ℹ️"
BTN_ROLE = "Задать / удалить роль 📝"
BTN_MODEL = "Сменить модель 👾"
BTN_BILLING = "План / оплата 💳"
BTN_DELETE_CONTEXT = "Удалить текущий контекст 🔄"

BTN_CANCEL_ROLE = "Отмена ❌"
BTN_DELETE_ROLE = "Удалить роль ⛔"

BTN_PREMIUM_30D = "1 месяц за ₽599"
BTN_PREMIUM_365D = "1 год за ₽1999"
BTN_CANCEL_BILLING = "Отмена ❌"

BTN_CANCEL_MODEL = "Выход ❌"

BTN_TEXTS = {BTN_HELP, BTN_PROFILE, BTN_ROLE, BTN_MODEL, BTN_BILLING, BTN_DELETE_CONTEXT}

CB_HELP = "help"
CB_PROFILE = "profile"
CB_ROLE = "role"
CB_MODEL = "model"
CB_BILLING = "billing"
CB_DELETE_CONTEXT = "delete_context"

CB_CANCEL_ROLE = "cancel_role"
CB_DELETE_ROLE = "delete_role"

CB_PREMIUM_START = "buy:"
CB_PREMIUM_31D = "31"
CB_PREMIUM_365D = "365"
CB_CANCEL_BILLING = "cancel_billing"

CB_MODEL_START = "change_model:"
CB_CANCEL_MODEL = "cancel_model"

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
    kb.button(text=BTN_CANCEL_ROLE, callback_data=CB_CANCEL_ROLE)
    kb.button(text=BTN_DELETE_ROLE, callback_data=CB_DELETE_ROLE)
    kb.adjust(2)
    return kb.as_markup()

def premium_options_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_PREMIUM_30D, callback_data=CB_PREMIUM_START+CB_PREMIUM_31D)
    kb.button(text=BTN_PREMIUM_365D, callback_data=CB_PREMIUM_START+CB_PREMIUM_365D)
    kb.button(text=BTN_CANCEL_BILLING, callback_data=CB_CANCEL_BILLING)
    kb.adjust(2, 1)
    return kb.as_markup()

async def model_inline_kb(telegram_id):
    kb = InlineKeyboardBuilder()
    for model, model_data in MODELS.items():
        symbol = ""
        if (not (await check_premium(telegram_id)) and model_data.premium_only):
            symbol = "🔒"
        if (model == await get_model(telegram_id)):
            symbol = "✅"
        kb.button(text=symbol + model, callback_data=CB_MODEL_START + model)
    kb.button(text=BTN_CANCEL_MODEL, callback_data=CB_CANCEL_MODEL)
    kb.adjust(1)
    return kb.as_markup()


