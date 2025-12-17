import asyncio

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message

# from openroutertest import request
from features.menu.keyboards import BTN_TEXTS

router = Router()


@router.message(StateFilter(None), F.text, ~F.text.startswith("/"), ~F.text.in_(BTN_TEXTS))
async def chat(message: Message):
    # answer = await asyncio.to_thread(request, message.text)
    # await message.answer(answer)
    await message.answer("хуй")
