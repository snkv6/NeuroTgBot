import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from routers import router
from features.menu.setup import setup_bot
from database.base import init_db


async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    load_dotenv("keys/.env")

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    bot = Bot(token=token)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await setup_bot(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
