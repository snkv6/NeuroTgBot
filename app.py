import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from routers import router
from features.menu.setup import setup_bot
from database.base import init_db
from features.billing_service.webhook_server import run_webhook_server
from bot_instance import bot

load_dotenv("keys/.env")

async def main():
    logging.basicConfig(level=logging.INFO)

    await init_db()

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await setup_bot(bot)
    await asyncio.gather(
        dp.start_polling(bot),
        run_webhook_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
