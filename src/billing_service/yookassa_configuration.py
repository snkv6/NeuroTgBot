import os
from yookassa import Configuration


async def configure_yookassa():
    shop_id = os.getenv("YOOKASSA_SHOP_ID")
    secret_key = os.getenv("YOOKASSA_SECRET_KEY")
    if not shop_id or not secret_key:
        raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY are not set")
    Configuration.account_id = shop_id
    Configuration.secret_key = secret_key
