import asyncio
import time

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.types import Message

from openroutertest import request_stream
from features.menu.keyboards import BTN_TEXTS

import re
import html

router = Router()

MESSAGE_SIZE = 3000

def to_telegram_html(text: str) -> str:
    safe = html.escape(text)

    pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    def repl(m):
        lang = m.group(1) or ""
        code = m.group(2)
        lang_attr = f" class='language-{lang}'" if lang else ""
        return f"<pre><code{lang_attr}>{code}</code></pre>"

    safe = pattern.sub(repl, safe)

    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    safe = re.sub(r"`(.+?)`", r"<code>\1</code>", safe)

    return safe


@router.message(StateFilter(None), F.text, ~F.text.startswith("/"), ~F.text.in_(BTN_TEXTS))
async def chat(message: Message):
    text = ""
    flag = True
    sent = message
    last_edit = 0.0
    last_sent_text = ""

    try:
        async for part in request_stream(message.chat.id, message.text):
            text += part

            if flag:
                sent = await message.answer(to_telegram_html(part), parse_mode=ParseMode.HTML)
                last_edit = 0.0
                last_sent_text = part
                flag = False
                continue

            if (time.monotonic() - last_edit) >= 0.7:
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
                    await asyncio.sleep(0.7)
                    sent = await message.answer(to_telegram_html(text), parse_mode=ParseMode.HTML)
                    last_sent_text = text
                elif text != last_sent_text:
                    last_edit = time.monotonic()
                    last_sent_text = text
                    await sent.edit_text(to_telegram_html(text), parse_mode=ParseMode.HTML)

        await asyncio.sleep(0.7 - time.monotonic() + last_edit)
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
            await asyncio.sleep(0.7)
            await message.answer(to_telegram_html(text), parse_mode=ParseMode.HTML)
        elif text != last_sent_text:
            await sent.edit_text(to_telegram_html(text), parse_mode=ParseMode.HTML)


    except Exception as e:
        await message.answer(f"Произошла ошибка: {e} "
                             f"Повторите запрос позже или обратитесь к администратору.")
