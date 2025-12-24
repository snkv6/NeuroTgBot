from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

def test_load_models_returns_dict_and_models_are_parsed():
    from src.config import load_models1, Model

    yaml_path = Path("../src/config/models.yaml")
    models = load_models1(str(yaml_path))

    assert isinstance(models, dict)
    assert models, "Ожидаем, что в models.yaml есть хотя бы одна модель"

    any_model = next(iter(models.values()))
    assert isinstance(any_model, Model)
    assert isinstance(any_model.title, str) and any_model.title
    assert isinstance(any_model.openrouter_id, str) and any_model.openrouter_id
    assert isinstance(any_model.vendor, str) and any_model.vendor
    assert isinstance(any_model.reasoning, bool)
    assert isinstance(any_model.premium_only, bool)
    assert isinstance(any_model.free_per_day, int)
    assert isinstance(any_model.premium_per_day, int)


@pytest.mark.asyncio
async def test_setup_bot_calls_aiogram_bot_methods():
    from src.features.menu import setup

    bot = pytest.importorskip("aiogram").Bot

    fake_bot = AsyncMock()

    await setup.setup_bot(fake_bot)

    assert fake_bot.set_my_commands.await_count == 1
    args, kwargs = fake_bot.set_my_commands.call_args
    commands = args[0]
    assert isinstance(commands, list)
    assert len(commands) > 0


    fake_bot.set_chat_menu_button.assert_awaited_once()
    fake_bot.set_my_short_description.assert_awaited_once()
    fake_bot.set_my_description.assert_awaited_once()


def test_setup_logging_calls_basicConfig_and_uses_DBLogHandler(monkeypatch):
    from src.core import logger_config as lc

    captured = {}

    class TestConsoleHandler:
        def __init__(self, *_args, **_kwargs):
            self.formatter_set = False

        def setFormatter(self, _fmt):
            self.formatter_set = True

    class TestDBHandler:
        def __init__(self, loop):
            captured["loop"] = loop
            self.formatter_set = False

        def setFormatter(self, _fmt):
            self.formatter_set = True

    def fake_basicConfig(**kwargs):
        captured["basicConfig_kwargs"] = kwargs

    # правильные подмены:
    monkeypatch.setattr(logging, "StreamHandler", TestConsoleHandler)
    monkeypatch.setattr(lc, "DBLogHandler", TestDBHandler)
    monkeypatch.setattr(logging, "basicConfig", fake_basicConfig)

    loop = asyncio.new_event_loop()
    try:
        lc.setup_logging(loop)
    finally:
        loop.close()

    kwargs = captured["basicConfig_kwargs"]
    assert kwargs["level"] == "INFO"
    assert kwargs["force"] is True
    assert len(kwargs["handlers"]) == 2

    console_h, db_h = kwargs["handlers"]
    assert isinstance(console_h, TestConsoleHandler)
    assert isinstance(db_h, TestDBHandler)
    assert console_h.formatter_set is True
    assert db_h.formatter_set is True
    assert captured["loop"] is loop

