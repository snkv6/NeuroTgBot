import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from features.menu.admin_keyboards import BTN_STAT
from features.menu.admin_setup import CMD_STAT
from database.users import get_total_users_count, get_premium_users_count

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command(CMD_STAT))
@router.message(F.text == BTN_STAT)
async def stat_msg(message: Message):
    logger.info("admin_stat_open tg_id=%s", message.from_user.id)
    total = await get_total_users_count()
    premium = await get_premium_users_count()
    non_premium = total - premium
    await message.answer(f"Статистика:\n\nВсего пользователей: {total}\nС подпиской: {premium}\nБез подписки: {non_premium}")


