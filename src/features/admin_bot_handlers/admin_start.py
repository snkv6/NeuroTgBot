import logging
from aiogram import Router
from aiogram.filters import CommandStart
from src.features.menu.admin_keyboards import main_reply_kb

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start(message):
    logger.info("admin_start tg_id=%s", message.from_user.id)
    await message.answer(
        "Вы находитесь в боте администратора\n"
        "Появились доступные действия",
        reply_markup=main_reply_kb(),
    )
