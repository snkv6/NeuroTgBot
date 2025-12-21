from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_DELETE_CONTEXT, CB_DELETE_CONTEXT
from features.menu.setup import CMD_DELETE_CONTEXT
from database.users import delete_context

router = Router()

@router.message(Command(CMD_DELETE_CONTEXT))
@router.message(F.text == BTN_DELETE_CONTEXT)
async def model_msg(message: Message):
    await delete_context(message.from_user.id)
    await message.answer("Контекст удален! 🔄")


@router.callback_query(F.data == CB_DELETE_CONTEXT)
async def model_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await model_msg(cb.message)