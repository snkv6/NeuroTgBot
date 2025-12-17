from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from features.menu.keyboards import main_reply_kb, actions_inline_kb
from base import add_user

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user.id)
    await message.answer(
        "Привет! Я бот с нейросетями 🤖\n"
        "Напиши запрос обычным текстом — я отвечу.\n",
        reply_markup=main_reply_kb(),
    )
    await message.answer("Настройки и быстрые действия:", reply_markup=actions_inline_kb())
