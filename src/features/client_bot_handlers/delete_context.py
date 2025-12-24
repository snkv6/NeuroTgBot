import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from src.features.menu.keyboards import BTN_DELETE_CONTEXT, CB_DELETE_CONTEXT
from src.features.menu.setup import CMD_DELETE_CONTEXT
from src.database.users import delete_context

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command(CMD_DELETE_CONTEXT))
@router.message(F.text == BTN_DELETE_CONTEXT)
async def delete_context_msg(message):
    logger.info("ui_delete_context_open tg_id=%s", message.from_user.id)
    await delete_context(message.from_user.id)
    await message.answer("Контекст удален! 🔄")


@router.callback_query(F.data == CB_DELETE_CONTEXT)
async def delete_context_cb(cb):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await delete_context_msg(cb.message)