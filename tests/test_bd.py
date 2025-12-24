from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_users_crud_and_missing_branches():
    import database.users as users

    telegram_id = 100_001
    missing_id = 999_999_999
    any_model = next(iter(users.MODELS.keys()))

    assert await users.add_user(telegram_id) is True
    assert await users.add_user(telegram_id) is False

    user = await users.get_user(telegram_id)
    assert user is not False
    assert user.telegram_id == telegram_id

    assert await users.update_role(telegram_id, "teacher") is True
    assert await users.get_role(telegram_id) == "teacher"

    assert await users.update_model(telegram_id, any_model) is True
    assert await users.get_model(telegram_id) == any_model

    assert await users.get_request_cnt(telegram_id) == 0
    assert await users.update_request_cnt(telegram_id) is True
    assert await users.get_request_cnt(telegram_id) == 1

    assert await users.get_user(missing_id) is False
    assert await users.update_role(missing_id, "x") is False
    assert await users.update_model(missing_id, any_model) is False
    assert await users.update_request_cnt(missing_id) is False
    assert await users.get_role(missing_id) is None
    assert await users.get_model(missing_id) is None
    assert await users.get_request_cnt(missing_id) == 0

    all_ids = await users.get_all_tg_ids()
    assert telegram_id in all_ids


@pytest.mark.asyncio
async def test_users_context_trim_and_delete():
    import database.users as users

    telegram_id = 100_002
    missing_id = 999_999_998

    assert await users.add_user(telegram_id) is True

    assert await users.update_context(telegram_id, "assistant", "hello") is True
    user = await users.get_user(telegram_id)
    assert user.context == []

    for i in range(users.PREMIUM_CONTEXT_LENGTH + 5):
        assert await users.update_context(telegram_id, "user", f"msg_{i}") is True

    user = await users.get_user(telegram_id)
    assert len(user.context) <= users.PREMIUM_CONTEXT_LENGTH
    assert user.context[0]["role"] != "assistant"
    assert user.context[-1]["content"].startswith("msg_")

    assert await users.delete_context(telegram_id) is True
    user = await users.get_user(telegram_id)
    assert user.context == []

    assert await users.delete_context(missing_id) is False


@pytest.mark.asyncio
async def test_users_premium_lists_and_reset_counters():
    import database.users as users

    premium_id = 100_003
    free_id = 100_004

    await users.add_user(premium_id)
    await users.add_user(free_id)

    assert await users.check_premium(premium_id) is False

    assert await users.update_premium(premium_id, 1) is True
    assert await users.check_premium(premium_id) is True

    remaining_days = await users.get_remaining_premium_days(premium_id)
    assert remaining_days >= 0

    user_before = await users.get_user(premium_id)
    until_before = user_before.premium_until
    assert await users.update_premium(premium_id, 2) is True
    user_after = await users.get_user(premium_id)
    assert user_after.premium_until == until_before + timedelta(days=2)

    premium_ids = await users.get_all_premium_users_tg_ids()
    non_premium_ids = await users.get_all_non_premium_users_tg_ids()
    assert premium_id in premium_ids
    assert free_id in non_premium_ids

    await users.update_request_cnt(premium_id)
    await users.update_request_cnt(premium_id)
    await users.update_request_cnt(free_id)

    assert await users.get_request_cnt(premium_id) == 2
    assert await users.get_request_cnt(free_id) == 1

    await users.reset_all_request_cnts()

    assert await users.get_request_cnt(premium_id) == 0
    assert await users.get_request_cnt(free_id) == 0


@pytest.mark.asyncio
async def test_payments_flow_create_attach_mark_paid_and_missing():
    from database.payments import attach_provider_payment_id, create_payment_order, mark_paid

    telegram_id = 200_001
    missing_order_id = 999_999_999

    order_id = await create_payment_order(
        telegram_id=telegram_id,
        plan_id="31",
        provider="yookassa",
        time=31,
    )
    assert isinstance(order_id, int)

    assert await attach_provider_payment_id(order_id, "prov_123") is True
    assert await attach_provider_payment_id(missing_order_id, "prov_x") is False

    payment = await mark_paid(order_id)
    assert payment is not None
    assert payment.paid is True

    payment_again = await mark_paid(order_id)
    assert payment_again is not None
    assert payment_again.paid is True

    assert await mark_paid(missing_order_id) is None


@pytest.mark.asyncio
async def test_logs_add_log_and_db_log_handler_emit(monkeypatch):
    from database.base import SessionLocal
    from database.logs import AppLog, DBLogHandler, _level, add_log

    await add_log(datetime.utcnow(), "info", "unit_test", "hello")

    async with SessionLocal() as session:
        result = await session.execute(select(AppLog).where(AppLog.name == "unit_test"))
        row = result.scalar_one()
        assert row.level == "info"
        assert row.message == "hello"

    record_err = logging.LogRecord("x", logging.ERROR, __file__, 1, "m", (), None)
    record_warn = logging.LogRecord("x", logging.WARNING, __file__, 1, "m", (), None)
    record_info = logging.LogRecord("x", logging.INFO, __file__, 1, "m", (), None)
    assert _level(record_err) == "error"
    assert _level(record_warn) == "warning"
    assert _level(record_info) == "info"

    scheduled = {"count": 0}

    def fake_run_coroutine_threadsafe(coro, loop):
        scheduled["count"] += 1
        asyncio.create_task(coro)
        return object()

    monkeypatch.setattr(asyncio, "run_coroutine_threadsafe", fake_run_coroutine_threadsafe)

    handler = DBLogHandler(loop=asyncio.get_running_loop())
    handler.setFormatter(logging.Formatter("%(message)s"))

    record = logging.LogRecord("my_app", logging.WARNING, __file__, 1, "warn_msg", (), None)
    record.created = time.time()
    handler.emit(record)

    await asyncio.sleep(0)
    assert scheduled["count"] == 1

    record_filtered = logging.LogRecord("sqlalchemy.engine", logging.WARNING, __file__, 1, "ignored", (), None)
    handler.emit(record_filtered)

    await asyncio.sleep(0)
    assert scheduled["count"] == 1
