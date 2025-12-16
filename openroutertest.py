import os
# import httpx
from openai import OpenAI

OPENROUTER_API_KEY = "govna_poeshte"

# http_client = httpx.Client(proxy=PROXY_URL)

def request(text):
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )

    resp = client.chat.completions.create(
        model="nvidia/nemotron-nano-9b-v2:free",
        messages=[{"role": "user", "content": text}],
    )

    return resp.choices[0].message.content

# tngtech/deepseek-r1t-chimera:free
# gpt-4o-mini
# nvidia/nemotron-nano-9b-v2:free