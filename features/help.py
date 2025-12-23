import logging
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_HELP, CB_HELP
from features.menu.setup import CMD_HELP

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command(CMD_HELP))
@router.message(F.text == BTN_HELP)
async def help_msg(message: Message):
    logger.info("help_open tg_id=%s", message.from_user.id)
    await message.answer(
        "<b>🫂 Помощь</b>\n\n"
        "Я могу помочь с учёбой, кодом и идеями.\n\n"
        "<b>Как начать:</b>\n"
        "👉 Просто напиши сообщение обычным текстом.\n\n"
        "<b>Что можно попросить:</b>\n"
        "• объяснение темы\n"
        "• помощь с кодом\n"
        "• генерацию идей\n"
        "• конспект или краткий разбор\n\n"
        "<b>Команды:</b>\n"
        "/start — запуск и главное меню\n"
        "/profile — профиль\n"
        "/role — выбрать роль помощника\n"
        "/model — выбрать модель\n"
        "/billing — оплата\n"
        "/delete_context — удалить контекст\n",
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == CB_HELP)
async def help_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await help_msg(cb.message)
