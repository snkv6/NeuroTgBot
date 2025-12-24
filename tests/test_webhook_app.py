from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio


@pytest_asyncio.fixture()
async def webhook_app_module(monkeypatch):

    yookassa_mod = types.ModuleType("yookassa")

    class Configuration:
        account_id = None
        secret_key = None

    class Payment:

        @staticmethod
        def find_one(_payment_id: str):
            raise RuntimeError("Payment.find_one is not configured in the test")

    yookassa_mod.Configuration = Configuration
    yookassa_mod.Payment = Payment
    monkeypatch.setitem(sys.modules, "yookassa", yookassa_mod)

    bot_instance_mod = types.ModuleType("bot_instance")
    fake_bot = SimpleNamespace(
        send_message=AsyncMock(),
        session=SimpleNamespace(close=AsyncMock()),
    )
    bot_instance_mod.client_bot = fake_bot
    monkeypatch.setitem(sys.modules, "bot_instance", bot_instance_mod)


    sys.modules.pop("features.billing_service.webhook_app", None)

    mod = importlib.import_module("features.billing_service.webhook_app")

    async def _direct_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr(mod.asyncio, "to_thread", _direct_to_thread, raising=True)

    return mod


@pytest_asyncio.fixture()
async def http_client(webhook_app_module):
    import httpx

    transport = httpx.ASGITransport(app=webhook_app_module.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_webhook_app_root(http_client):
    resp = await http_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


@pytest.mark.asyncio
async def test_yookassa_webhook_bad_json_returns_ok_false(webhook_app_module, http_client, monkeypatch):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "mark_paid", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock())

    resp = await http_client.post(
        "/yookassa/webhook",
        content="{not-json}",
        headers={"content-type": "application/json"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": False}
    webhook_app_module.configure_yookassa.assert_not_awaited()
    webhook_app_module.mark_paid.assert_not_awaited()
    webhook_app_module.update_premium.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"event": "payment.waiting_for_capture", "object": {"id": "p_1"}},
        {"event": "payment.succeeded", "object": {}},
        {"event": "payment.succeeded"},
    ],
)
async def test_yookassa_webhook_ignores_non_target_events(webhook_app_module, http_client, monkeypatch, payload):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "mark_paid", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock())

    resp = await http_client.post("/yookassa/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    webhook_app_module.configure_yookassa.assert_not_awaited()
    webhook_app_module.mark_paid.assert_not_awaited()
    webhook_app_module.update_premium.assert_not_awaited()


@pytest.mark.asyncio
async def test_yookassa_webhook_returns_ok_false_when_fetch_fails(webhook_app_module, http_client, monkeypatch):
    monkeypatch.setattr(webhook_app_module, "mark_paid", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock())

    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock(side_effect=RuntimeError("boom")))

    resp = await http_client.post(
        "/yookassa/webhook",
        json={"event": "payment.succeeded", "object": {"id": "p_1"}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": False}
    webhook_app_module.mark_paid.assert_not_awaited()
    webhook_app_module.update_premium.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status, paid",
    [
        ("canceled", True),
        ("succeeded", False),
        (None, True),
    ],
)
async def test_yookassa_webhook_returns_ok_true_when_payment_not_confirmed(
    webhook_app_module, http_client, monkeypatch, status, paid
):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "mark_paid", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock())

    webhook_app_module.Payment = SimpleNamespace(
        find_one=lambda _pid: SimpleNamespace(status=status, paid=paid, metadata={"order_id": 10})
    )

    resp = await http_client.post(
        "/yookassa/webhook",
        json={"event": "payment.succeeded", "object": {"id": "p_1"}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    webhook_app_module.mark_paid.assert_not_awaited()
    webhook_app_module.update_premium.assert_not_awaited()


@pytest.mark.asyncio
async def test_yookassa_webhook_returns_ok_true_when_no_order_id(webhook_app_module, http_client, monkeypatch):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "mark_paid", AsyncMock())
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock())

    webhook_app_module.Payment = SimpleNamespace(
        find_one=lambda _pid: SimpleNamespace(status="succeeded", paid=True, metadata={})
    )

    resp = await http_client.post(
        "/yookassa/webhook",
        json={"event": "payment.succeeded", "object": {"id": "p_1"}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    webhook_app_module.mark_paid.assert_not_awaited()
    webhook_app_module.update_premium.assert_not_awaited()


@pytest.mark.asyncio
async def test_yookassa_webhook_happy_path_marks_paid_updates_premium_and_notifies(
    webhook_app_module, http_client, monkeypatch
):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())

    webhook_app_module.Payment = SimpleNamespace(
        find_one=lambda _pid: SimpleNamespace(
            status="succeeded",
            paid=True,
            metadata={"order_id": 777},
        )
    )

    paid_row = SimpleNamespace(paid=True, telegram_id=42, duration=31)
    mark_paid = AsyncMock(return_value=paid_row)
    update_premium = AsyncMock(return_value=True)
    monkeypatch.setattr(webhook_app_module, "mark_paid", mark_paid)
    monkeypatch.setattr(webhook_app_module, "update_premium", update_premium)

    resp = await http_client.post(
        "/yookassa/webhook",
        json={"event": "payment.succeeded", "object": {"id": "p_1"}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}

    mark_paid.assert_awaited_once_with(777)
    update_premium.assert_awaited_once_with(42, 31)
    webhook_app_module.client_bot.send_message.assert_awaited()
    args, _kwargs = webhook_app_module.client_bot.send_message.await_args
    assert args[0] == 42
    assert "Премиум" in args[1]
    assert "31" in args[1]


@pytest.mark.asyncio
async def test_yookassa_webhook_returns_ok_false_when_update_fails(webhook_app_module, http_client, monkeypatch):
    monkeypatch.setattr(webhook_app_module, "configure_yookassa", AsyncMock())

    webhook_app_module.Payment = SimpleNamespace(
        find_one=lambda _pid: SimpleNamespace(status="succeeded", paid=True, metadata={"order_id": 1})
    )

    monkeypatch.setattr(
        webhook_app_module,
        "mark_paid",
        AsyncMock(return_value=SimpleNamespace(paid=True, telegram_id=1, duration=1)),
    )
    monkeypatch.setattr(webhook_app_module, "update_premium", AsyncMock(side_effect=RuntimeError("db down")))

    resp = await http_client.post(
        "/yookassa/webhook",
        json={"event": "payment.succeeded", "object": {"id": "p_1"}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": False}


@pytest.mark.asyncio
async def test_webhook_app_shutdown_closes_bot_session(webhook_app_module):
    await webhook_app_module.shutdown()
    webhook_app_module.client_bot.session.close.assert_awaited_once()
