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

async def request(telegram_id, text: str):
    # print("привет")
    user = await get_user(telegram_id=telegram_id)
    if user:
        messages = []
        # print(user.role)
        # print(user.context)
        if user.role:
            messages.append({"role": "system", "content": user.role})
        if (user.context):
            if (user.context[0]["role"] == "assistant"):
                messages += user.context[1:]
            else:
                messages += user.context
        # print(messages)
        messages.append({"role": "user", "content": text})
        # print(messages)

        resp = await client.chat.completions.create(
            model=user.cur_model,
            messages=messages,
        )
        # print("привет")
        # print(resp)
        await update_context(telegram_id, "user", text)
        await update_context(telegram_id, "assistant", resp.choices[0].message.content)
        return resp.choices[0].message.content

