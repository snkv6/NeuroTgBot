# tngtech/deepseek-r1t-chimera:free
# gpt-4o-mini
# nvidia/nemotron-nano-9b-v2:free

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from database.users import get_user, update_context

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

    messages = []
    if user.role:
        messages.append({"role": "system", "content": user.role})
    if user.context:
        if user.context[0]["role"] == "assistant":
            messages += user.context[1:]
        else:
            messages += user.context
    messages.append({"role": "user", "content": text})

    stream = await client.chat.completions.create(
        model=user.cur_model,
        messages=messages,
        stream=True,
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
