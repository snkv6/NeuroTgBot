from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import os
import logging
import asyncio
from yookassa import Payment

from src.features.menu import BTN_BILLING, CB_BILLING, CB_PREMIUM_START, CB_CANCEL_BILLING, premium_options_inline_kb
from src.features.menu import CMD_BILLING
from src.billing_service.yookassa_configuration import configure_yookassa
from src.database.payments import create_payment_order, attach_provider_payment_id, PLANS

router = Router()

logger = logging.getLogger(__name__)

@router.message(Command(CMD_BILLING))
@router.message(F.text == BTN_BILLING)
async def billing_msg(message: Message):
    logger.info("ui_billing_open tg_id=%s", message.from_user.id)
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

@router.callback_query(F.data == CB_CANCEL_BILLING)
async def cancel_billing(cb: CallbackQuery):
    logger.info("ui_cancel_billing tg_id=%s", cb.from_user.id)
    await cb.answer("Отменено")
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass

@router.callback_query(F.data.startswith(CB_PREMIUM_START))
async def buy_plan(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass

    user_id = cb.from_user.id
    try:
        plan_id = cb.data.split(":")[1]
    except ValueError:
        logger.warning("bad_callback tg_id=%s data=%r", user_id, cb.data)
        await cb.message.answer("Кнопка устарела. Откройте меню оплаты заново.")
        return

    if plan_id not in PLANS:
        logger.warning("unknown_plan_in_callback tg_id=%s plan_id=%r data=%r", user_id, plan_id, cb.data)
        await cb.message.answer("Этот план недоступен. Откройте меню оплаты заново.")
        return
    logger.info("ui_plan_selected tg_id=%s plan_id=%s", user_id, plan_id)
    try:

        await configure_yookassa()

        order_id = await create_payment_order(user_id, plan_id, "yookassa", PLANS[plan_id]["days"])

        return_url = os.getenv("YOOKASSA_RETURN_URL")
        if not return_url:
            raise RuntimeError("YOOKASSA_RETURN_URL is not set")

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
        logger.info("pay_url_created tg_id=%s plan_id=%s", user_id, plan_id)

        await cb.message.answer(f"Оплати по ссылке:\n{pay_url}")
    except Exception:
        logger.exception("buy_plan_failed tg_id=%s plan_id=%s", user_id, plan_id)
        await cb.message.answer("Не удалось создать платёж. Попробуйте ещё раз чуть позже.")