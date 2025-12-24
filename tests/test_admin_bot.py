import pytest


def _reply_texts(markup):
    # ReplyKeyboardMarkup.keyboard -> list[list[KeyboardButton]]
    return [btn.text for row in getattr(markup, "keyboard", []) for btn in row]


def _inline_callbacks(markup):
    # InlineKeyboardMarkup.inline_keyboard -> list[list[InlineKeyboardButton]]
    return [btn.callback_data for row in getattr(markup, "inline_keyboard", []) for btn in row]


def test_admin_main_reply_kb_has_required_buttons():
    from src.features.menu import admin_keyboards as ak

    kb = ak.main_reply_kb()
    texts = _reply_texts(kb)

    assert ak.BTN_STAT in texts
    assert ak.BTN_MESSAGE in texts


def test_admin_message_inline_kb_has_targets_and_cancel():
    from src.features.menu import admin_keyboards as ak

    kb = ak.message_inline_kb()
    cbs = _inline_callbacks(kb)

    # должно быть что-то вроде: "message_start:all" / "...:premium" / "...:non_premium"
    assert any(cb == ak.CB_MESSAGE_CANCEL for cb in cbs)
    assert any(cb.startswith(ak.CB_MESSAGE_START + ":") for cb in cbs)

    assert any(cb == f"{ak.CB_MESSAGE_START}:{ak.CB_MESSAGE_ALL}" for cb in cbs)
    assert any(cb == f"{ak.CB_MESSAGE_START}:{ak.CB_MESSAGE_PREMIUM}" for cb in cbs)
    assert any(cb == f"{ak.CB_MESSAGE_START}:{ak.CB_MESSAGE_NON_PREMIUM}" for cb in cbs)


def test_admin_preview_inline_kb_has_confirm_and_cancel():
    from src.features.menu import admin_keyboards as ak

    kb = ak.preview_inline_kb()
    cbs = _inline_callbacks(kb)

    assert ak.CB_PREVIEW_CONFIRM in cbs
    assert ak.CB_PREVIEW_CANCEL in cbs


import importlib
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class FakeMessage:
    def __init__(self, user_id=1, text="hi"):
        self.from_user = FakeUser(user_id)
        self.text = text
        self.answer = AsyncMock()
        self.delete = AsyncMock()


class FakeCallback:
    def __init__(self, user_id=1, data="x", message=None):
        self.from_user = FakeUser(user_id)
        self.data = data
        self.message = message or FakeMessage(user_id=user_id)
        self.answer = AsyncMock()


class FakeState:
    def __init__(self):
        self.clear = AsyncMock()
        self.set_state = AsyncMock()
        self.update_data = AsyncMock()
        self.get_data = AsyncMock(return_value={})


@pytest.fixture()
def import_admin(monkeypatch):
    """
    Стабим bot_instance.client_bot (чтобы импорт admin_message не тянул реального бота)
    и даём способ импортить модули заново.
    """
    bot_instance = types.ModuleType("bot_instance")
    bot_instance.client_bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setitem(sys.modules, "bot_instance", bot_instance)

    def _import(name: str):
        sys.modules.pop(name, None)
        return importlib.import_module(name)

    return _import


@pytest.mark.asyncio
async def test_admin_start_sends_main_kb(import_admin, monkeypatch):
    mod = import_admin("admin_bot_handlers.admin_start")

    # подменим main_reply_kb на маркер, чтобы проверить что он реально используется
    monkeypatch.setattr(mod, "main_reply_kb", lambda: "ADMIN_MAIN_KB", raising=True)

    msg = FakeMessage(user_id=10)
    await mod.start(msg)

    msg.answer.assert_awaited_once()
    assert "администратора" in msg.answer.await_args.args[0]
    assert msg.answer.await_args.kwargs["reply_markup"] == "ADMIN_MAIN_KB"


@pytest.mark.asyncio
async def test_admin_stat_formats_numbers(import_admin, monkeypatch):
    mod = import_admin("admin_bot_handlers.admin_stat")

    monkeypatch.setattr(mod, "get_total_users_count", AsyncMock(return_value=10), raising=True)
    monkeypatch.setattr(mod, "get_premium_users_count", AsyncMock(return_value=3), raising=True)

    msg = FakeMessage(user_id=1)
    await mod.stat_msg(msg)

    msg.answer.assert_awaited_once()
    text = msg.answer.await_args.args[0]
    assert "Всего пользователей: 10" in text
    assert "С подпиской: 3" in text
    assert "Без подписки: 7" in text


@pytest.mark.asyncio
async def test_admin_message_open_shows_inline_kb(import_admin, monkeypatch):
    mod = import_admin("admin_bot_handlers.admin_message")

    monkeypatch.setattr(mod, "message_inline_kb", lambda: "MSG_KB", raising=True)

    msg = FakeMessage(user_id=1)
    await mod.message_msg(msg)

    msg.answer.assert_awaited_once()
    assert "Выберите" in msg.answer.await_args.args[0]
    assert msg.answer.await_args.kwargs["reply_markup"] == "MSG_KB"


@pytest.mark.asyncio
async def test_admin_message_target_bad_callback(import_admin):
    mod = import_admin("admin_bot_handlers.admin_message")

    cb = FakeCallback(user_id=1, data="bad", message=FakeMessage(user_id=1))
    state = FakeState()

    await mod.message_target_cb(cb, state)

    cb.message.answer.assert_awaited_once()
    assert "Кнопка устарела" in cb.message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_admin_message_target_sets_state_and_data(import_admin):
    mod = import_admin("admin_bot_handlers.admin_message")

    cb = FakeCallback(user_id=1, data=f"{mod.CB_MESSAGE_START}:{mod.CB_MESSAGE_ALL}")
    state = FakeState()

    await mod.message_target_cb(cb, state)

    state.set_state.assert_awaited()
    state.update_data.assert_awaited_once_with(target=mod.CB_MESSAGE_ALL)
    cb.message.answer.assert_awaited_once()
    assert "Введите сообщение" in cb.message.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_admin_preview_confirm_sends_messages(import_admin, monkeypatch):
    mod = import_admin("admin_bot_handlers.admin_message")

    # IMPORTANT: эти функции должны быть await-нуты в коде (иначе тест упадёт)
    monkeypatch.setattr(mod, "get_all_tg_ids", AsyncMock(return_value=[101, 102]), raising=True)
    monkeypatch.setattr(mod, "asyncio", SimpleNamespace(sleep=AsyncMock()), raising=True)

    # бот уже стабнут в фикстуре import_admin: mod.client_bot.send_message
    mod.client_bot.send_message = AsyncMock()

    state = FakeState()
    state.get_data = AsyncMock(return_value={"target": mod.CB_MESSAGE_ALL, "message": "HELLO"})

    cb = FakeCallback(user_id=1, data=mod.CB_PREVIEW_CONFIRM, message=FakeMessage(user_id=1))

    await mod.preview_confirm_cb(cb, state)

    mod.get_all_tg_ids.assert_awaited_once()
    assert mod.client_bot.send_message.await_count == 2
    cb.message.answer.assert_awaited()
    out = cb.message.answer.await_args.args[0]
    assert "Было отправлено: 2" in out
