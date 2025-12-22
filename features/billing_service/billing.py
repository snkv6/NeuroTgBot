from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import os
import asyncio
from yookassa import Configuration, Payment

from features.menu.keyboards import BTN_BILLING, CB_BILLING, CB_PREMIUM_START, premium_options_inline_kb
from features.menu.setup import CMD_BILLING
from features.billing_service.yookassa_configuration import configure_yookassa
from database.payments import create_payment_order, attach_provider_payment_id, PLANS

router = Router()


@router.message(Command(CMD_BILLING))
@router.message(F.text == BTN_BILLING)
async def billing_msg(message: Message):
    await message.answer("<b>План / оплата 💳</b>\n\n"
                         "Выберите план подписки:",
                         reply_markup=premium_options_inline_kb(),
                         parse_mode=ParseMode.HTML)


@router.callback_query(F.data == CB_BILLING)
async def billing_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await billing_msg(cb.message)

@router.callback_query(F.data.startswith(CB_PREMIUM_START))
async def buy_plan(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass


    plan_id = cb.data.split(":")[1]
    user_id = cb.from_user.id

    await configure_yookassa()

    order_id = await create_payment_order(user_id, plan_id, "yookassa", PLANS[plan_id]["days"])

    return_url = os.getenv("YOOKASSA_RETURN_URL")
    if not return_url:
        raise RuntimeError("YOOKASSA_RETURN_URL are not set")

    payload = {
        "amount": {
            "value": PLANS[plan_id]["amount"],
            "currency": "RUB",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "capture": True,
        "description": f"Premium на {PLANS[plan_id]['days']} дней",
        "metadata": {
            "order_id": str(order_id),
            "telegram_id": str(user_id),
            "plan_id": str(plan_id),
        },
    }
    def _create_payment():
        return Payment.create(payload, str(order_id))

    yk_payment = await asyncio.to_thread(_create_payment)

    await attach_provider_payment_id(order_id, yk_payment.id)
    pay_url = yk_payment.confirmation.confirmation_url

    await cb.message.answer(f"Оплати по ссылке:\n{pay_url}")
