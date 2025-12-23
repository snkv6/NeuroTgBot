import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers_router import router as handlers_router
from features.menu.setup import setup_bot
from database.base import init_db
from features.billing_service.webhook_server import run_webhook_server
from bot_instance import bot
from aiogram_errors import router as error_aiogram_router
from logger_config import setup_logging
load_dotenv("keys/.env")

logger = logging.getLogger(__name__)

async def main():
    setup_logging()

    logger.info("startup")
    await init_db()
    logger.info("database initialized")

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers_router)
    dp.include_router(error_aiogram_router)

    await setup_bot(bot)
    try:
        logger.info("polling started")
        logger.info("webhook server started")
        await asyncio.gather(
            dp.start_polling(bot),
            run_webhook_server(),
        )
    except Exception:
        logger.exception("fatal error in main")
        raise


if __name__ == "__main__":
    asyncio.run(main())
