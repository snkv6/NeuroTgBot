import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from features.menu.keyboards import main_reply_kb, actions_inline_kb
from database.users import add_user

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "привет"
    )

@router.message(F.text)
async def start(message: Message):
    await message.answer(message.text)