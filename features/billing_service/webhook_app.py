import os
import asyncio

from fastapi import FastAPI, Request
from dotenv import load_dotenv
from yookassa import Payment

from database.payments import mark_paid
from database.users import update_premium
from features.billing_service.yookassa_configuration import configure_yookassa

load_dotenv("keys/.env")

app = FastAPI()


@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    body = await request.json()

    event = body.get("event")
    obj = body.get("object") or {}
    payment_id = obj.get("id")

    if event != "payment.succeeded" or not payment_id:
        return {"ok": True}

    await configure_yookassa()

    def _fetch_payment():
        return Payment.find_one(payment_id)

    payment_resp = await asyncio.to_thread(_fetch_payment)

    if getattr(payment_resp, "status", None) != "succeeded" or not getattr(payment_resp, "paid", False):
        return {"ok": True}

    metadata = getattr(payment_resp, "metadata", None) or {}
    order_id = metadata.get("order_id")
    if not order_id:
        return {"ok": True}

    p = await mark_paid(order_id)
    if p and p.paid:
        await update_premium(p.telegram_id, p.duration)

    return {"ok": True}

@app.get("/")
async def root():
    return {"ok": True}
