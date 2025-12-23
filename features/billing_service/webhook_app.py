import os
import asyncio
import logging

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from yookassa import Payment

from database.payments import mark_paid
from database.users import update_premium
from features.billing_service.yookassa_configuration import configure_yookassa
from bot_instance import client_bot

load_dotenv("keys/.env")

app = FastAPI()

logger = logging.getLogger(__name__)


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    try:
        body = await request.json()
    except Exception:
        logger.warning("yookassa_webhook_bad_json")
        return {"ok": False}

    event = body.get("event")
    obj = body.get("object") or {}
    payment_id = obj.get("id")

    if event != "payment.succeeded" or not payment_id:
        return {"ok": True}

    try:
        await configure_yookassa()

        def _fetch_payment():
            return Payment.find_one(payment_id)

        payment_resp = await asyncio.to_thread(_fetch_payment)
    except Exception:
        logger.exception("yookassa_fetch_failed payment_id=%s", payment_id)
        return {"ok": False}

    if getattr(payment_resp, "status", None) != "succeeded" or not getattr(payment_resp, "paid", False):
        return {"ok": True}

    metadata = getattr(payment_resp, "metadata", None) or {}
    order_id = metadata.get("order_id")
    if not order_id:
        return {"ok": True}

    try:
        p = await mark_paid(order_id)
        if p and p.paid:
            await update_premium(p.telegram_id, p.duration)
            await client_bot.send_message(
                p.telegram_id,
                f"✅ Оплата прошла!\nПремиум активирован на {p.duration} дней."
            )
            logger.info(
                "payment_succeeded tg_id=%s order_id=%s duration_days=%s",
                p.telegram_id,
                order_id,
                p.duration,
            )
    except Exception:
        logger.exception("yookassa_update_failed order_id=%s payment_id=%s", order_id, payment_id)
        return {"ok": False}

    return {"ok": True}

@app.get("/")
async def root():
    return {"ok": True}

@app.on_event("shutdown")
async def shutdown():
    await client_bot.session.close()
