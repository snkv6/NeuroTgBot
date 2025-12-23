import asyncio
import logging
from datetime import datetime, timedelta
from database.users import reset_all_request_cnts

logger = logging.getLogger(__name__)

async def midnight_cnt_reset():
    while True:
        now = datetime.utcnow()

        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        to_sleep = (next_midnight - now).total_seconds()

        await asyncio.sleep(to_sleep)

        await reset_all_request_cnts()