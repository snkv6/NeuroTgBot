from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_MODEL, CB_MODEL, CB_MODEL_START, model_inline_kb
from features.menu.setup import CMD_MODEL
from database.users import update_model

router = Router()


@router.message(Command(CMD_MODEL))
@router.message(F.text == BTN_MODEL)
async def model_msg(message: Message):
    inline_kb = await model_inline_kb(message.from_user.id)
    await message.answer("<b>Сменить модель 👾</b>\n\n"
                         "Доступные модели:\n(TODO)",
                         parse_mode=ParseMode.HTML,
                         reply_markup=inline_kb)


@router.callback_query(F.data == CB_MODEL)
async def model_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await model_msg(cb.message)

@router.callback_query(F.data.startswith(CB_MODEL_START))
async def change_model_cb_(cb: CallbackQuery):
    await cb.answer()
    model = cb.split(":")[1]
    await update_model(cb.from_user.id, model)
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await cb.answer("Модель изменена")
