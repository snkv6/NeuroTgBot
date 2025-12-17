from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from features.menu.keyboards import BTN_BILLING, CB_BILLING
from features.menu.setup import CMD_BILLING

router = Router()


@router.message(Command(CMD_BILLING))
@router.message(F.text == BTN_BILLING)
async def billing_msg(message: Message):
    await message.answer("План / оплата\n\nТут будет выбор плана и оплата.\n(TODO)")


@router.callback_query(F.data == CB_BILLING)
async def billing_cb(cb: CallbackQuery):
    await cb.answer()
    await billing_msg(cb.message)
