import os
from aiogram import Bot

client_token = os.getenv("CLIENT_TELEGRAM_BOT_TOKEN")
admin_token = os.getenv("ADMIN_TELEGRAM_BOT_TOKEN")
if not client_token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
if not admin_token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
client_bot = Bot(token=client_token)
admin_bot = Bot(token=admin_token)