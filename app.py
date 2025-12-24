import asyncio
import logging
from pyexpat import features

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers_router import client_router, admin_router
from features.menu.setup import setup_bot
from database.base import init_db
from bot_instance import client_bot, admin_bot
from request_cnt_reset import midnight_cnt_reset
from logger_config import setup_logging
from aiogram_errors import router as client_error_router
from features.billing_service.webhook_server import run_webhook_server


load_dotenv("keys/.env")

logger = logging.getLogger(__name__)


async def start_client_bot():
    client_dp = Dispatcher(storage=MemoryStorage())
    client_dp.include_router(client_router)
    client_dp.include_router(client_error_router)

    await setup_bot(client_bot)
    await client_dp.start_polling(client_bot)


async def start_admin_bot():
    admin_dp = Dispatcher(storage=MemoryStorage())
    admin_dp.include_router(admin_router)

    await setup_bot(admin_bot)
    await admin_dp.start_polling(admin_bot)


async def main():
    setup_logging(asyncio.get_running_loop())
    await init_db()

    try:
        logger.info("client_bot_polling_started")
        logger.info("admin_bot_polling_started")
        logger.info("webhook server started")
        await asyncio.gather(
            start_client_bot(),
            start_admin_bot(),
            run_webhook_server(),
            midnight_cnt_reset(),
        )
    except Exception:
        logger.exception("fatal error in main")
        raise


if __name__ == "__main__":
    asyncio.run(main())
