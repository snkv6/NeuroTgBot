from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from features.menu.keyboards import BTN_PROFILE, CB_PROFILE
from features.menu.setup import CMD_PROFILE

router = Router()


@router.message(Command(CMD_PROFILE))
@router.message(F.text == BTN_PROFILE)
async def profile_msg(message: Message):
    # TODO: реализовать
    await message.answer(
        "Ваш Профиль\n\n"
        "Роль:\n"
        "Модель:\n"
        "Подписка:"
    )


@router.callback_query(F.data == CB_PROFILE)
async def profile_cb(cb: CallbackQuery):
    await cb.answer()
    await profile_msg(cb.message)
