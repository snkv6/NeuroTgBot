import asyncio
import time
import logging

from aiogram.enums import ParseMode
from aiogram.types import Message

from openroutertest import request_stream
from config.const import MODELS, EDIT_TIMING, MESSAGE_SIZE
from database.users import get_user, check_premium, update_model

import re
import html

logger = logging.getLogger(__name__)

PATTERN_CODEBLOCK = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
PATTERN_BOLD = re.compile(r"\*\*(.+?)\*\*")
PATTERN_INLINE = re.compile(r"`(.+?)`")

def to_telegram_html(text: str) -> str:
    formatted = html.escape(text)

    def repl(m):
        lang = m.group(1) or ""
        code = m.group(2)
        lang_attr = f" class='language-{lang}'" if lang else ""
        return f"<pre><code{lang_attr}>{code}</code></pre>"

    formatted = PATTERN_CODEBLOCK.sub(repl, formatted)
    formatted = PATTERN_BOLD.sub(r"<b>\1</b>", formatted)
    formatted = PATTERN_INLINE.sub(r"<code>\1</code>", formatted)
    return formatted


async def checks(message: Message):
    user = await get_user(message.from_user.id)
    premium = await check_premium(message.from_user.id)
    model = MODELS[user.cur_model]
    if model.premium_only and not premium:
        await update_model(user.telegram_id, list(MODELS.keys())[0])
        logger.info("llm_skip_premium_model tg_id=%s model=%s", message.from_user.id, user.cur_model)
        await message.answer(
            f"🥲 Ваша подписка закончилась, поэтому модель была изменена на модель по умолчанию: {list(MODELS.keys())[0]}")
        return False

    if (not premium and model.free_per_day <= user.request_cnt) or (
            premium and model.premium_per_day <= user.request_cnt):
        logger.info("llm_skip_limit tg_id=%s model=%s cnt=%s", message.from_user.id, user.cur_model, user.request_cnt)
        await message.answer(
            "🥲 У вас закончились запросы к этой модели, выберите другую, с большим колчеством запросов, или попробуйте завтра")
        return False

    return True


async def request(message: Message, content):
    # logger.info("ui_chat_start tg_id=%s msg_len=%s", message.from_user.id, len(message.text))
    if not await checks(message):
        return

    try:
        sent = await message.answer("<code>⏳ Модель обрабатывает ваш запрос. Пожалуйста, подождите немного ...</code>",
                                    parse_mode=ParseMode.HTML)
        text = ""
        last_edit = 0.0
        last_sent_text = sent.text
        async for part in request_stream(message.chat.id, content):
            text += part

            if (time.monotonic() - last_edit) >= EDIT_TIMING:
                if len(text) > MESSAGE_SIZE:
                    separator = MESSAGE_SIZE
                    while separator > 0 and not (
                            text[separator] == " " and text[separator - 1].isalpha() and text[separator + 1].isalpha()
                    ):
                        separator -= 1
                    if separator == 0:
                        separator = MESSAGE_SIZE
                    await sent.edit_text(to_telegram_html(text[:separator]), parse_mode=ParseMode.HTML)
                    text = text[separator + 1:]
                    await asyncio.sleep(EDIT_TIMING)
                    sent = await message.answer(to_telegram_html(text), parse_mode=ParseMode.HTML)
                    last_sent_text = text
                elif text != last_sent_text:
                    last_edit = time.monotonic()
                    last_sent_text = text
                    await sent.edit_text(to_telegram_html(text), parse_mode=ParseMode.HTML)

        await asyncio.sleep(max(0.0, EDIT_TIMING - time.monotonic() + last_edit))
        if len(text) > MESSAGE_SIZE:
            separator = MESSAGE_SIZE
            while separator > 0 and not (
                    text[separator] == " " and text[separator - 1].isalpha() and text[separator + 1].isalpha()
            ):
                separator -= 1
            if separator == 0:
                separator = MESSAGE_SIZE
            await sent.edit_text(to_telegram_html(text[:separator]), parse_mode=ParseMode.HTML)
            text = text[separator + 1:]
            await asyncio.sleep(EDIT_TIMING)
            await message.answer(to_telegram_html(text), parse_mode=ParseMode.HTML)
        elif text != last_sent_text:
            await sent.edit_text(to_telegram_html(text), parse_mode=ParseMode.HTML)


    except Exception:
        logger.exception("chat_failed tg_id=%s", message.chat.id)
        await message.answer(
            "Произошла ошибка. Повторите запрос позже или обратитесь к администратору."
        )
