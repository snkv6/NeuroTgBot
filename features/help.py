from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_HELP, CB_HELP
from features.menu.setup import CMD_HELP

router = Router()


@router.message(Command(CMD_HELP))
@router.message(F.text == BTN_HELP)
async def help_msg(message: Message):
    await message.answer("Помощь\n\n"
                         "• Просто напиши запрос обычным текстом — я отвечу.\n"
                         "• Можно просить: объяснить тему, написать/исправить код, идеи, конспект.\n\n"
                         "Команды:\n"
                         "/start — запуск и меню\n"
                         "/profile — профиль\n"
                         "/role — выбрать роль\n"
                         "/model — выбрать модель\n"
                         "/billing — оплата\n")


@router.callback_query(F.data == CB_HELP)
async def help_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await help_msg(cb.message)
