import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers_router import client_router, admin_router
from features.menu.setup import setup_bot
from database.base import init_db
from features.billing_service.webhook_server import run_webhook_server
from logger_config import setup_logging
from bot_instance import client_bot, admin_bot
from request_cnt_reset import midnight_cnt_reset

load_dotenv("keys/.env")


async def start_client_bot():
    client_dp = Dispatcher(storage=MemoryStorage())
    client_dp.include_router(client_router)

    await setup_bot(client_bot)
    await client_dp.start_polling(client_bot)


async def start_admin_bot():
    admin_dp = Dispatcher(storage=MemoryStorage())
    admin_dp.include_router(admin_router)

    await setup_bot(admin_bot)
    await admin_dp.start_polling(admin_bot)


async def main():
    setup_logging()
    await init_db()

    await asyncio.gather(
        start_client_bot(),
        start_admin_bot(),
        run_webhook_server(),
        midnight_cnt_reset(),
    )


if __name__ == "__main__":
    asyncio.run(main())
