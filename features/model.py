from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_MODEL, CB_MODEL
from features.menu.setup import CMD_MODEL

router = Router()


@router.message(Command(CMD_MODEL))
@router.message(F.text == BTN_MODEL)
async def model_msg(message: Message):
    await message.answer("<b>Сменить модель 👾</b>\n\n"
                         "Доступные модели:\n(TODO)",
                         parse_mode=ParseMode.HTML)


@router.callback_query(F.data == CB_MODEL)
async def model_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await model_msg(cb.message)
