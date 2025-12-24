import logging
from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from src.features.menu.keyboards import BTN_PROFILE, CB_PROFILE
from src.features.menu.setup import CMD_PROFILE
from src.database.users import get_remaining_premium_days, check_premium, get_model, get_role, get_request_cnt

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command(CMD_PROFILE))
@router.message(F.text == BTN_PROFILE)
async def profile_msg(message):
    tg_id = message.from_user.id
    logger.info("ui_profile_open tg_id=%s", tg_id)
    role = await get_role(tg_id)
    if role is None:
        role = "нет роли"
    model = await get_model(tg_id)
    cnt = await get_request_cnt(tg_id)
    if model is None:
        model = "нет действующей модели"
    if await check_premium(tg_id):
        premium = f"подписка действует еще {await get_remaining_premium_days(tg_id)} д."
    else:
        premium = "нет премиум подписки"
    await message.answer(
        "<b>Ваш Профиль ℹ️</b>\n\n"
        f"<b>Роль</b> 👨: {role}\n\n"
        f"<b>Модель</b> 👾: {model}\n\n"
        f"<b>Сделано запросов</b> 📞: {cnt}\n\n"
        f"<b>Подписка</b> 💳: {premium}",
        parse_mode=ParseMode.HTML
    )


@router.callback_query(F.data == CB_PROFILE)
async def profile_cb(cb):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await profile_msg(cb.message)
