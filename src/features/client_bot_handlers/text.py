import logging

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message

from src.features.menu.keyboards import BTN_TEXTS
from src.services.response_stream import request

router = Router()

logger = logging.getLogger(__name__)

@router.message(StateFilter(None), F.text, ~F.text.startswith("/"), ~F.text.in_(BTN_TEXTS))
async def chat(message: Message):
    logger.info("ui_chat_start tg_id=%s msg_len=%s", message.from_user.id, len(message.text))

    await request(message, [{"type": "text", "text": message.text}])
