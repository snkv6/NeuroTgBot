# tngtech/deepseek-r1t-chimera:free
# gpt-4o-mini
# nvidia/nemotron-nano-9b-v2:free

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlalchemy.util import await_only

from database.users import get_user, update_context, check_premium, update_model, update_request_cnt

from config.test import PREMIUM_CONTEXT_LENGTH, FREE_CONTEXT_LENGTH, MODELS

load_dotenv("keys/.env")

key = os.getenv("OPENROUTER_API_KEY")

client = AsyncOpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
)


async def request_stream(telegram_id, text: str):
    user = await get_user(telegram_id=telegram_id)
    if not user:
        return

    if MODELS[user.cur_model].premium_only and not await check_premium(user.telegram_id):
        # !!!! надо прислать сообщение что у вас закончился премиум и модель изменена на модель по умолчанию, повторите запрос
        await update_model(user.telegram_id, list(MODELS.keys())[0])
        return

    if not await check_premium(user.telegram_id) and MODELS[user.cur_model].free_per_day <= user.request_cnt:
        # !!!! надо прислать сообщение
        # закончились бесплтаные запросы на данную модель, смените модель (на ту у которй больше запросов), купите премиум или дождитесь сдедующих суток
        return

    if await check_premium(user.telegram_id) and MODELS[user.cur_model].premium_per_day <= user.request_cnt:
        # !!!! надо прислать сообщение
        # закончились премиум запросы на данную модель, смените модель (на ту у которй больше запросов) или дождитесь сдедующих суток
        return

    messages = []

    if user.role:
        messages.append({"role": "system", "content": user.role})

    if await check_premium(user.telegram_id):
        context = user.context[-PREMIUM_CONTEXT_LENGTH:]
    else:
        context = user.context[-FREE_CONTEXT_LENGTH:]

    if context:
        if context[0]["role"] == "assistant":
            messages += context[1:]
        else:
            messages += context

    messages.append({"role": "user", "content": text})

    extra_body = None
    if MODELS[user.cur_model].reasoning:
        extra_body = {"reasoning": {"enabled": True}}

    stream = await client.chat.completions.create(
        model=MODELS[user.cur_model].openrouter_id,
        messages=messages,
        stream=True,
        extra_body=extra_body,
    )

    full = []
    async for chunk in stream:
        delta = chunk.choices[0].delta
        part = getattr(delta, "content", None)
        if part:
            full.append(part)
            yield part

    await update_context(telegram_id, "user", text)
    await update_context(telegram_id, "assistant", "".join(full))
    await update_request_cnt(telegram_id)
