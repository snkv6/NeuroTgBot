import os
from aiogram import Bot

token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
bot = Bot(token=token)
