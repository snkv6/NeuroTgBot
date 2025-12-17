import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from routers import router
from features.menu.setup import setup_bot


async def main():
    logging.basicConfig(level=logging.INFO)

    token = "8570005846:AAFLN9CUao0UsPdjqtx6v4COwtSWuYXQjgg"
    bot = Bot(token=token)

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await setup_bot(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
