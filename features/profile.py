from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_PROFILE, CB_PROFILE
from features.menu.setup import CMD_PROFILE
from database.users import get_remaining_premium_days, check_premium, get_model, get_role

router = Router()


@router.message(Command(CMD_PROFILE))
@router.message(F.text == BTN_PROFILE)
async def profile_msg(message: Message):
    tg_id = message.from_user.id
    role = await get_role(tg_id)
    if role is None:
        role = "нет роли"
    model = await get_model(tg_id)
    if model is None:
        model = "нет действующей модели"
    if await check_premium(tg_id):
        premium = f"подписка действует еще {await get_remaining_premium_days(tg_id)} д."
    else:
        premium = "нет премиум подписки"
    await message.answer(
        "Ваш Профиль ℹ️\n\n"
        f"Роль: {role}\n"
        f"Модель: {model}\n"
        f"Подписка: {premium}"
    )


@router.callback_query(F.data == CB_PROFILE)
async def profile_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await profile_msg(cb.message)
