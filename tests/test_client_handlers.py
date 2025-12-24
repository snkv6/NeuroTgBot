from __future__ import annotations

import importlib
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


# ----------------------------
# Fakes (Message / Callback / FSM)
# ----------------------------

class FakeUser:
    def __init__(self, user_id: int):
        self.id = user_id


class FakeChat:
    def __init__(self, chat_id: int):
        self.id = chat_id


class FakeSentMessage:
    def __init__(self, text: str = ""):
        self.text = text
        self.edit_text = AsyncMock(side_effect=self._edit_side_effect)

    async def _edit_side_effect(self, new_text: str, **_kwargs):
        self.text = new_text
        return None


class FakeMessage:
    def __init__(self, user_id: int = 1, chat_id: int = 10, text: str = "hi"):
        self.from_user = FakeUser(user_id)
        self.chat = FakeChat(chat_id)
        self.text = text
        self.delete = AsyncMock()

        async def _answer_side_effect(text: str, **_kwargs):
            return FakeSentMessage(text=text)

        self.answer = AsyncMock(side_effect=_answer_side_effect)


class FakeCallbackQuery:
    def __init__(self, user_id: int = 1, data: str = "x", message: FakeMessage | None = None):
        self.from_user = FakeUser(user_id)
        self.data = data
        self.message = message or FakeMessage(user_id=user_id)
        self.answer = AsyncMock()


class FakeFSMContext:
    def __init__(self):
        self.set_state = AsyncMock()
        self.clear = AsyncMock()


# ----------------------------
# Import helper with stubs
# ----------------------------

@pytest.fixture()
def stubs(monkeypatch):
    """
    Стабим внешние зависимости ДО импорта handler-модулей:
      - database.users
      - features.menu.keyboards
      - openroutertest (request_stream)
    """

    # --- database.users ---
    users_mod = types.ModuleType("database.users")
    users_mod.add_user = AsyncMock(return_value=True)
    users_mod.delete_context = AsyncMock(return_value=True)

    users_mod.update_role = AsyncMock(return_value=True)
    users_mod.update_model = AsyncMock(return_value=True)

    users_mod.get_role = AsyncMock(return_value=None)
    users_mod.get_model = AsyncMock(return_value=None)
    users_mod.get_request_cnt = AsyncMock(return_value=0)
    users_mod.check_premium = AsyncMock(return_value=False)
    users_mod.get_remaining_premium_days = AsyncMock(return_value=0)
    users_mod.get_user = AsyncMock(return_value=None)

    monkeypatch.setitem(sys.modules, "database.users", users_mod)

    # --- features.menu.keyboards ---
    kb_mod = types.ModuleType("features.menu.keyboards")

    kb_mod.BTN_HELP = "HELP_BTN"
    kb_mod.CB_HELP = "help_cb"

    kb_mod.BTN_PROFILE = "PROFILE_BTN"
    kb_mod.CB_PROFILE = "profile_cb"

    kb_mod.BTN_ROLE = "ROLE_BTN"
    kb_mod.CB_ROLE = "role_cb"
    kb_mod.CB_CANCEL_ROLE = "role_cancel_cb"
    kb_mod.CB_DELETE_ROLE = "role_delete_cb"

    kb_mod.BTN_MODEL = "MODEL_BTN"
    kb_mod.CB_MODEL = "model_cb"
    kb_mod.CB_MODEL_START = "model:"
    kb_mod.CB_CANCEL_MODEL = "model_cancel_cb"

    kb_mod.BTN_DELETE_CONTEXT = "DEL_CTX_BTN"
    kb_mod.CB_DELETE_CONTEXT = "del_ctx_cb"

    # эти кнопки запрещены как "роль" в role.py
    kb_mod.BTN_TEXTS = [
        kb_mod.BTN_HELP,
        kb_mod.BTN_PROFILE,
        kb_mod.BTN_ROLE,
        kb_mod.BTN_MODEL,
        kb_mod.BTN_DELETE_CONTEXT,
    ]

    kb_mod.main_reply_kb = lambda: "MAIN_REPLY_KB"
    kb_mod.actions_inline_kb = lambda: "ACTIONS_INLINE_KB"
    kb_mod.special_role_inline_kb = lambda: "ROLE_INLINE_KB"

    async def _model_inline_kb(_tg_id: int):
        return "MODEL_INLINE_KB"

    kb_mod.model_inline_kb = _model_inline_kb

    monkeypatch.setitem(sys.modules, "features.menu.keyboards", kb_mod)

    # --- openroutertest.request_stream ---
    openrouter_mod = types.ModuleType("openroutertest")

    async def _empty_stream(_chat_id: int, _text: str):
        if False:
            yield ""  # pragma: no cover

    openrouter_mod.request_stream = _empty_stream
    monkeypatch.setitem(sys.modules, "openroutertest", openrouter_mod)

    return SimpleNamespace(users=users_mod, kb=kb_mod, openrouter=openrouter_mod)


@pytest.fixture()
def import_fresh(stubs):
    """
    Импортим модуль заново, чтобы он взял зависимости из sys.modules (наши стабы).
    """
    def _import(module_name: str):
        sys.modules.pop(module_name, None)
        return importlib.import_module(module_name)

    return _import


# ----------------------------
# start.py
# ----------------------------

@pytest.mark.asyncio
async def test_start_sends_two_messages_and_calls_add_user(import_fresh, stubs):
    mod = import_fresh("features.client_bot_handlers.start")

    msg = FakeMessage(user_id=123)
    await mod.start(msg)

    stubs.users.add_user.assert_awaited_once_with(123)

    assert msg.answer.await_count == 2
    first_call = msg.answer.await_args_list[0]
    second_call = msg.answer.await_args_list[1]

    assert "Привет" in first_call.args[0]
    assert first_call.kwargs["reply_markup"] == "MAIN_REPLY_KB"

    assert "Настройки" in second_call.args[0]
    assert second_call.kwargs["reply_markup"] == "ACTIONS_INLINE_KB"


# ----------------------------
# help.py
# ----------------------------

@pytest.mark.asyncio
async def test_help_msg_answers_html(import_fresh):
    mod = import_fresh("features.client_bot_handlers.help")

    msg = FakeMessage(user_id=10)
    await mod.help_msg(msg)

    msg.answer.assert_awaited_once()
    text = msg.answer.await_args.args[0]
    assert "/start" in text
    assert "Помощь" in text
    assert mod.ParseMode.HTML == msg.answer.await_args.kwargs["parse_mode"]


@pytest.mark.asyncio
async def test_help_cb_deletes_message_and_calls_help(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.help")

    # чтобы не зависеть от реального конструктора TelegramBadRequest
    class DummyBadRequest(Exception):
        pass

    monkeypatch.setattr(mod, "TelegramBadRequest", DummyBadRequest, raising=True)

    msg = FakeMessage(user_id=7)
    cb = FakeCallbackQuery(user_id=7, data=mod.CB_HELP, message=msg)

    await mod.help_cb(cb)

    cb.answer.assert_awaited_once()
    msg.delete.assert_awaited_once()
    msg.answer.assert_awaited_once()


@pytest.mark.asyncio
async def test_help_cb_ignores_bad_request_on_delete(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.help")

    class DummyBadRequest(Exception):
        pass

    monkeypatch.setattr(mod, "TelegramBadRequest", DummyBadRequest, raising=True)

    msg = FakeMessage(user_id=7)
    msg.delete = AsyncMock(side_effect=DummyBadRequest("nope"))
    cb = FakeCallbackQuery(user_id=7, data=mod.CB_HELP, message=msg)

    await mod.help_cb(cb)

    cb.answer.assert_awaited_once()
    msg.answer.assert_awaited_once()


# ----------------------------
# profile.py
# ----------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role, model, cnt, premium, days, expected_parts",
    [
        (None, None, 0, False, 0, ["нет роли", "нет действующей модели", "нет премиум"]),
        ("dev", "M1", 5, False, 0, ["dev", "M1", "5", "запрос", "нет премиум"]),
        ("dev", "M1", 5, True, 12, ["dev", "M1", "5", "запрос", "12"]),
    ],
)
async def test_profile_msg_renders_fields(import_fresh, stubs, role, model, cnt, premium, days, expected_parts):
    mod = import_fresh("features.client_bot_handlers.profile")

    stubs.users.get_role.return_value = role
    stubs.users.get_model.return_value = model
    stubs.users.get_request_cnt.return_value = cnt
    stubs.users.check_premium.return_value = premium
    stubs.users.get_remaining_premium_days.return_value = days

    msg = FakeMessage(user_id=99)
    await mod.profile_msg(msg)

    msg.answer.assert_awaited_once()
    text = msg.answer.await_args.args[0]
    for part in expected_parts:
        assert part in text
    assert mod.ParseMode.HTML == msg.answer.await_args.kwargs["parse_mode"]


# ----------------------------
# role.py
# ----------------------------

@pytest.mark.asyncio
async def test_role_msg_sets_state_and_sends_menu(import_fresh):
    mod = import_fresh("features.client_bot_handlers.role")

    msg = FakeMessage(user_id=1)
    state = FakeFSMContext()

    await mod.role_msg(msg, state)

    state.set_state.assert_awaited_once()
    msg.answer.assert_awaited_once()
    assert msg.answer.await_args.kwargs["reply_markup"] == "ROLE_INLINE_KB"


@pytest.mark.asyncio
async def test_cancel_setting_role_cb_clears_state(import_fresh):
    mod = import_fresh("features.client_bot_handlers.role")

    msg = FakeMessage(user_id=2)
    cb = FakeCallbackQuery(user_id=2, data=mod.CB_CANCEL_ROLE, message=msg)
    state = FakeFSMContext()

    await mod.cancel_setting_role_cb(cb, state)

    cb.answer.assert_awaited_once()
    assert cb.answer.await_args.args[0] == "Отменено"
    state.clear.assert_awaited_once()
    msg.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_role_cb_updates_role_to_none(import_fresh, stubs):
    mod = import_fresh("features.client_bot_handlers.role")

    msg = FakeMessage(user_id=3)
    cb = FakeCallbackQuery(user_id=3, data=mod.CB_DELETE_ROLE, message=msg)
    state = FakeFSMContext()

    await mod.delete_role_cb(cb, state)

    state.clear.assert_awaited_once()
    stubs.users.update_role.assert_awaited_once_with(3, None)
    cb.answer.assert_awaited_once()
    assert cb.answer.await_args.args[0] == "Роль удалена"
    msg.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_btn_texts_in_role_rejects_menu_buttons(import_fresh):
    mod = import_fresh("features.client_bot_handlers.role")

    msg = FakeMessage(user_id=4, text="HELP_BTN")
    state = FakeFSMContext()

    await mod.btn_texts_in_role(msg, state)

    msg.answer.assert_awaited_once()
    assert "не можете выбрать" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_special_handler_sets_role_and_clears_state(import_fresh, stubs):
    mod = import_fresh("features.client_bot_handlers.role")

    msg = FakeMessage(user_id=5, text="Я строгий ревьюер кода")
    state = FakeFSMContext()

    await mod.special_handler(msg, state)

    state.clear.assert_awaited_once()
    stubs.users.update_role.assert_awaited_once_with(5, "Я строгий ревьюер кода")
    msg.answer.assert_awaited_once()
    assert msg.answer.await_args.args[0] == "Роль выбрана!"


# ----------------------------
# model.py
# ----------------------------

@pytest.mark.asyncio
async def test_model_msg_builds_text_and_uses_inline_kb(import_fresh, stubs, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.model")

    # Делаем маленький MODELS, чтобы текст был предсказуемым
    mod.MODELS = {
        "FreeModel": SimpleNamespace(premium_only=False, free_per_day=1, premium_per_day=10, vendor="V1"),
        "PremModel": SimpleNamespace(premium_only=True, free_per_day=0, premium_per_day=10, vendor="V2"),
    }
    stubs.users.check_premium.return_value = False

    msg = FakeMessage(user_id=11)
    await mod.model_msg(msg, telegram_id=11)

    msg.answer.assert_awaited_once()
    text = msg.answer.await_args.args[0]
    assert "FreeModel" in text
    assert "PremModel" in text
    assert msg.answer.await_args.kwargs["reply_markup"] == "MODEL_INLINE_KB"
    assert mod.ParseMode.HTML == msg.answer.await_args.kwargs["parse_mode"]


@pytest.mark.asyncio
async def test_change_model_cb_bad_callback_shows_stale_button(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.model")

    # мокнем MODELS и зависимости (чтобы не дошло до них)
    mod.MODELS = {"A": SimpleNamespace(premium_only=False, vendor="V", free_per_day=1, premium_per_day=1)}
    monkeypatch.setattr(mod, "check_premium", AsyncMock(return_value=True), raising=True)

    msg = FakeMessage(user_id=1)
    cb = FakeCallbackQuery(user_id=1, data="model_without_colon", message=msg)

    await mod.change_model_cb_(cb)

    msg.answer.assert_awaited_once()
    assert "Кнопка устарела" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_change_model_cb_unknown_model(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.model")
    mod.MODELS = {"A": SimpleNamespace(premium_only=False, vendor="V", free_per_day=1, premium_per_day=1)}
    monkeypatch.setattr(mod, "check_premium", AsyncMock(return_value=True), raising=True)

    msg = FakeMessage(user_id=1)
    cb = FakeCallbackQuery(user_id=1, data="model:UNKNOWN", message=msg)

    await mod.change_model_cb_(cb)

    msg.answer.assert_awaited_once()
    assert "недоступна" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_change_model_cb_denied_without_premium(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.model")

    mod.MODELS = {
        "Free": SimpleNamespace(premium_only=False, vendor="V", free_per_day=1, premium_per_day=1),
        "Prem": SimpleNamespace(premium_only=True, vendor="V", free_per_day=0, premium_per_day=1),
    }

    monkeypatch.setattr(mod, "check_premium", AsyncMock(return_value=False), raising=True)
    monkeypatch.setattr(mod, "get_model", AsyncMock(return_value="Free"), raising=True)
    monkeypatch.setattr(mod, "update_model", AsyncMock(), raising=True)
    monkeypatch.setattr(mod, "delete_context", AsyncMock(), raising=True)

    msg = FakeMessage(user_id=1)
    cb = FakeCallbackQuery(user_id=1, data="model:Prem", message=msg)

    await mod.change_model_cb_(cb)

    msg.answer.assert_awaited_once()
    assert "не можете выбрать" in msg.answer.await_args.args[0]
    mod.update_model.assert_not_awaited()


@pytest.mark.asyncio
async def test_change_model_cb_vendor_change_clears_context(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.model")

    mod.MODELS = {
        "Old": SimpleNamespace(premium_only=False, vendor="V1", free_per_day=1, premium_per_day=1),
        "New": SimpleNamespace(premium_only=False, vendor="V2", free_per_day=1, premium_per_day=1),
    }

    monkeypatch.setattr(mod, "check_premium", AsyncMock(return_value=True), raising=True)
    monkeypatch.setattr(mod, "get_model", AsyncMock(return_value="Old"), raising=True)
    monkeypatch.setattr(mod, "update_model", AsyncMock(), raising=True)
    monkeypatch.setattr(mod, "delete_context", AsyncMock(), raising=True)

    msg = FakeMessage(user_id=10)
    cb = FakeCallbackQuery(user_id=10, data="model:New", message=msg)

    await mod.change_model_cb_(cb)

    mod.delete_context.assert_awaited_once_with(telegram_id=10)
    mod.update_model.assert_awaited_once_with(10, "New")
    msg.delete.assert_awaited_once()
    msg.answer.assert_awaited_once()
    ans = msg.answer.await_args.args[0]
    assert "Модель изменена" in ans
    assert "контекст очищен" in ans


# ----------------------------
# delete_context.py
# ----------------------------

@pytest.mark.asyncio
async def test_delete_context_msg_deletes_and_answers(import_fresh, stubs):
    mod = import_fresh("features.client_bot_handlers.delete_context")

    msg = FakeMessage(user_id=50)
    await mod.delete_context_msg(msg)

    stubs.users.delete_context.assert_awaited_once_with(50)
    msg.answer.assert_awaited_once()
    assert "Контекст удален" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_delete_context_cb_calls_delete_context_msg(import_fresh, stubs, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.delete_context")

    class DummyBadRequest(Exception):
        pass

    monkeypatch.setattr(mod, "TelegramBadRequest", DummyBadRequest, raising=True)

    msg = FakeMessage(user_id=51)
    cb = FakeCallbackQuery(user_id=51, data=mod.CB_DELETE_CONTEXT, message=msg)

    await mod.delete_context_cb(cb)

    cb.answer.assert_awaited_once()
    msg.delete.assert_awaited_once()
    # ожидаем, что именно telegram_id уйдет в delete_context
    stubs.users.delete_context.assert_awaited_once_with(51)
    msg.answer.assert_awaited_once()



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "src, must_contain",
    [
        ("**bold**", "<b>bold</b>"),
        ("`x`", "<code>x</code>"),
        ("1 < 2", "1 &lt; 2"),
        ("```python\nprint(1)\n```", "<pre><code class='language-python'>"),
    ],
)
async def test_to_telegram_html_transforms(import_fresh, src, must_contain):
    mod = import_fresh("features.client_bot_handlers.request")
    html = mod.to_telegram_html(src)
    assert must_contain in html


@pytest.mark.asyncio
async def test_checks_denies_premium_only_model_without_premium(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.request")

    mod.MODELS = {
        "Free": SimpleNamespace(premium_only=False, free_per_day=10, premium_per_day=10),
        "Prem": SimpleNamespace(premium_only=True, free_per_day=0, premium_per_day=10),
    }

    fake_user = SimpleNamespace(telegram_id=1, cur_model="Prem", request_cnt=0)
    monkeypatch.setattr(mod, "get_user", AsyncMock(return_value=fake_user), raising=True)
    monkeypatch.setattr(mod, "check_premium", AsyncMock(return_value=False), raising=True)
    monkeypatch.setattr(mod, "update_model", AsyncMock(), raising=True)

    msg = FakeMessage(user_id=1)

    ok = await mod.checks(msg)
    assert ok is False

    mod.update_model.assert_awaited_once_with(1, "Free")
    msg.answer.assert_awaited_once()
    assert "подписка закончилась" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_request_simple_stream_edits_message(import_fresh, monkeypatch):
    mod = import_fresh("features.client_bot_handlers.request")

    # checks -> True
    monkeypatch.setattr(mod, "checks", AsyncMock(return_value=True), raising=True)

    # stream -> "hi"
    async def stream(_chat_id: int, _content):
        yield "hi"

    monkeypatch.setattr(mod, "request_stream", stream, raising=True)

    # не спим в тестах
    monkeypatch.setattr(mod.asyncio, "sleep", AsyncMock(), raising=True)

    # чтобы (time.monotonic() - last_edit) >= 0.7 точно сработало
    t = {"v": 0.0}
    def monotonic():
        t["v"] += 1.0
        return t["v"]

    monkeypatch.setattr(mod.time, "monotonic", monotonic, raising=True)

    msg = FakeMessage(user_id=1, chat_id=100, text="hello")

    # ловим sent, который возвращает message.answer(...)
    sent_holder = {}

    async def answer_side_effect(text: str, **_kwargs):
        sent = FakeSentMessage(text=text)
        sent_holder.setdefault("sent", sent)  # первый ответ (⏳)
        return sent

    msg.answer = AsyncMock(side_effect=answer_side_effect)

    await mod.request(msg, [{"type": "text", "text": "hello"}])

    # 1) сначала "⏳ ..."
    assert msg.answer.await_count >= 1
    assert "⏳" in msg.answer.await_args_list[0].args[0]

    # 2) потом edit_text на "hi"
    sent = sent_holder["sent"]
    sent.edit_text.assert_awaited()
    assert "hi" in sent.text
