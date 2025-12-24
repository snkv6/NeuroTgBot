import logging
import base64
from io import BytesIO

from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from features.client_bot_handlers.request import request
from config.const import MODELS
from database.users import get_model, check_premium

router = Router()
logger = logging.getLogger(__name__)


async def pdf_to_base64(message: Message, file_id: str) -> str:
    bot = message.bot
    tg_file = await bot.get_file(file_id)

    buf = BytesIO()
    await bot.download_file(tg_file.file_path, destination=buf)

    data = buf.getvalue()
    buf.close()

    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:application/pdf;base64,{b64}"


@router.message(F.document)
async def document(message: Message):
    doc = message.document

    logger.info("pdf_received tg_id=%s file_id=%s name=%s size=%s", message.from_user.id, doc.file_id, doc.file_name,
                doc.file_size)

    if doc.mime_type != "application/pdf":
        await message.answer("❌ Поддерживается только работа с PDF и картинками")
        return

    if not MODELS[await get_model(message.from_user.id)].file_support:
        await message.answer("😢 Эта модель не поддерживает работу с PDF и картинками")
        return

    if not await check_premium(message.from_user.id):
        await message.answer("💳 Для работы с PDF и картинками необходим премиум")
        return

    if doc.file_size > 1024 * 1024:
        await message.answer("❌ PDF слишком большой для обработки.")
        return

    try:
        pdf_b64 = await pdf_to_base64(message, doc.file_id)
    except Exception:
        logger.exception("pdf_base64_failed tg_id=%s file_id=%s", message.from_user.id, doc.file_id)
        await message.answer("❌ Не удалось обработать PDF. Попробуй ещё раз.")
        return

    if message.caption:
        await request(message, [
            {"type": "text", "text": message.caption},
            {"type": "file", "file": {"filename": message.document.file_name, "file_data": pdf_b64}}])
    else:
        await request(message, [
            {"type": "file", "file": {"filename": message.document.file_name, "file_data": pdf_b64}}])
