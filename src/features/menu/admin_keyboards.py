from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

BTN_STAT = "Статистика"
BTN_MESSAGE = "Отправить сообщение"

BTN_MESSAGE_ALL = "Всем"
BTN_MESSAGE_PREMIUM = "Всем с подпиской"
BTN_MESSAGE_NON_PREMIUM = "Всем без подписки"
BTN_MESSAGE_CANCEL = "Отмена"

BTN_PREVIEW_CONFIRM = "Подтвердить"
BTN_PREVIEW_CANCEL = "Отмена"

CB_MESSAGE_START = "message:"
CB_MESSAGE_ALL = "all"
CB_MESSAGE_PREMIUM = "premium"
CB_MESSAGE_NON_PREMIUM = "non_premium"
CB_MESSAGE_CANCEL = "message_cancel"

CB_PREVIEW_CONFIRM = "preview_confirm"
CB_PREVIEW_CANCEL = "preview_cancel"



def main_reply_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_STAT)
    kb.button(text=BTN_MESSAGE)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def message_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_MESSAGE_ALL, callback_data=CB_MESSAGE_START + CB_MESSAGE_ALL)
    kb.button(text=BTN_MESSAGE_PREMIUM, callback_data=CB_MESSAGE_START + CB_MESSAGE_PREMIUM)
    kb.button(text=BTN_MESSAGE_NON_PREMIUM, callback_data=CB_MESSAGE_START + CB_MESSAGE_NON_PREMIUM)
    kb.button(text=BTN_MESSAGE_CANCEL, callback_data=CB_MESSAGE_CANCEL)
    kb.adjust(3, 1)
    return kb.as_markup()

def preview_inline_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text=BTN_PREVIEW_CONFIRM, callback_data=CB_PREVIEW_CONFIRM)
    kb.button(text=BTN_PREVIEW_CANCEL, callback_data=CB_PREVIEW_CANCEL)
    kb.adjust(2)
    return kb.as_markup()

