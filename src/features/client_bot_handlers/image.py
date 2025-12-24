import logging
import base64
from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message

from src.config.const import MODELS
from src.database.users import get_model, check_premium
from src.services.response_stream import request

router = Router()
logger = logging.getLogger(__name__)


async def image_to_base64(message: Message, file_id: str) -> str:
    bot = message.bot

    tg_file = await bot.get_file(file_id)

    buf = BytesIO()
    await bot.download_file(tg_file.file_path, destination=buf)

    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    buf.close()
    return f"data:image/jpeg;base64,{b64}"


@router.message(F.photo)
async def image(message: Message):
    file_id = message.photo[-1].file_id

    logger.info("ui_image_received tg_id=%s file_id=%s", message.from_user.id, file_id)

    if not MODELS[await get_model(message.from_user.id)].file_support:
        await message.answer("😢 Эта модель не поддерживает работу с PDF и картинками")
        return

    if not await check_premium(message.from_user.id):
        await message.answer("💳 Для работы с PDF и картинками необходим премиум")
        return

    try:
        image_b64 = await image_to_base64(message, file_id)
    except Exception:
        logger.exception("image_base64_failed tg_id=%s file_id=%s", message.from_user.id, file_id)
        await message.answer("❌ Не удалось обработать картинку. Попробуй ещё раз.")
        return

    logger.info("image_base64_ready tg_id=%s b64_len=%s", message.from_user.id, len(image_b64))

    if message.caption:
        await request(message, [{"type": "text", "text": message.caption},
                                {"type": "image_url", "image_url": {"url": image_b64}}])
    else:
        await request(message, [{"type": "image_url", "image_url": {"url": image_b64}}])
