import logging
from sqlalchemy import Column, Integer, String, Boolean
from database.base import Base, SessionLocal
from features.menu.keyboards import CB_PREMIUM_31D, CB_PREMIUM_365D

logger = logging.getLogger(__name__)

PLANS = {
    CB_PREMIUM_31D: {"days": 31, "amount": "599"},
    CB_PREMIUM_365D: {"days": 365, "amount": "1999"},
}


class Payment(Base):
    __tablename__ = "payments"

    order_id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, index=True)
    plan_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    provider_payment_id = Column(String, unique=True, nullable=True)
    paid = Column(Boolean, default=False, nullable=False)
    duration = Column(Integer, nullable=False)


async def create_payment_order(telegram_id, plan_id, provider, time):
    async with SessionLocal() as session:
        async with session.begin():
            p = Payment(
                telegram_id=telegram_id,
                plan_id=plan_id,
                provider=provider,
                provider_payment_id=None,
                paid=False,
                duration=time
            )
            session.add(p)
            await session.flush()
            logger.info("db_payment_order_created tg_id=%s plan=%s order_id=%s provider=%s", telegram_id, plan_id,
                        p.order_id, provider)
            return p.order_id


async def attach_provider_payment_id(order_id, provider_payment_id):
    async with SessionLocal() as session:
        async with session.begin():
            p = await session.get(Payment, order_id)
            if not p:
                return False
            p.provider_payment_id = provider_payment_id
            logger.info("db_payment_attached order_id=%s provider_payment_id=%s", order_id, provider_payment_id)
            return True


async def mark_paid(order_id):
    async with SessionLocal() as session:
        async with session.begin():
            p = await session.get(Payment, order_id)
            if not p:
                return None
            if not p.paid:
                p.paid = True
                logger.info("db_payment_marked_paid order_id=%s tg_id=%s plan=%s", order_id, p.telegram_id, p.plan_id)
            return p
