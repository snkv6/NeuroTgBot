# tests/conftest.py
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

TEST_DB_FILE = Path(tempfile.gettempdir()) / f"neuro_tg_bot_test_{os.getpid()}.sqlite3"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

os.environ.setdefault("DATABASE_URL", TEST_DB_URL)
os.environ.setdefault("DATABASE_URL_R", TEST_DB_URL)
os.environ.setdefault("DATABASE_URL_W", TEST_DB_URL)

os.environ.setdefault("CLIENT_TELEGRAM_BOT_TOKEN", "123456:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi1234567890ABCD")
os.environ.setdefault("ADMIN_TELEGRAM_BOT_TOKEN", "654321:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi1234567890ABCD")
os.environ.setdefault("OPENROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("YOOKASSA_SHOP_ID", "test-shop")
os.environ.setdefault("YOOKASSA_SECRET_KEY", "test-secret")
os.environ.setdefault("PORT", "8000")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _init_test_db():
    try:
        TEST_DB_FILE.unlink(missing_ok=True)
    except Exception:
        pass

    import database.base as db_base

    import database.logs  # noqa: F401
    import database.payments  # noqa: F401
    import database.users  # noqa: F401

    async with db_base.engine.begin() as conn:
        await conn.run_sync(db_base.Base.metadata.create_all)

    try:
        yield
    finally:
        async with db_base.engine.begin() as conn:
            await conn.run_sync(db_base.Base.metadata.drop_all)
        await db_base.engine.dispose()
        try:
            TEST_DB_FILE.unlink(missing_ok=True)
        except Exception:
            pass


@pytest.fixture()
def make_message():
    def _make(*, user_id: int = 1, chat_id: int = 1, text: str = "hi"):
        msg = AsyncMock()
        msg.text = text
        msg.from_user = SimpleNamespace(id=user_id)
        msg.chat = SimpleNamespace(id=chat_id)

        msg.answer = AsyncMock()
        msg.reply = AsyncMock()
        msg.delete = AsyncMock()
        msg.edit_text = AsyncMock()
        return msg

    return _make


@pytest.fixture()
def make_callback_query(make_message):
    def _make(*, user_id: int = 1, chat_id: int = 1, data: str = "test"):
        cb = AsyncMock()
        cb.from_user = SimpleNamespace(id=user_id)
        cb.data = data
        cb.message = make_message(user_id=user_id, chat_id=chat_id)
        cb.answer = AsyncMock()
        return cb

    return _make


@pytest.fixture()
def make_fsm_context():
    def _make(initial: dict | None = None):
        state = AsyncMock()
        state.set_state = AsyncMock()
        state.update_data = AsyncMock()
        state.clear = AsyncMock()
        state.get_data = AsyncMock(return_value=initial or {})
        return state

    return _make
