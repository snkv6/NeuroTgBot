import time
import uuid
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from src.database.users import get_user, update_context, check_premium, update_request_cnt

from src.config.const import PREMIUM_CONTEXT_LENGTH, FREE_CONTEXT_LENGTH, MODELS

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / "keys" / ".env")

key = os.getenv("OPENROUTER_API_KEY")

logger = logging.getLogger(__name__)

client = AsyncOpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
)

async def request_stream(telegram_id, content):
    req_id = uuid.uuid4()
    t0 = time.monotonic()

    user = await get_user(telegram_id=telegram_id)
    if not user:
        logger.info("llm_skip_user_not_found tg_id=%s", telegram_id)
        return

    messages = []

    has_role = False
    if user.role:
        messages.append({"role": "system", "content": user.role})
        has_role = True

    if await check_premium(user.telegram_id):
        context = user.context[-PREMIUM_CONTEXT_LENGTH:]
        ctx_limit = PREMIUM_CONTEXT_LENGTH
    else:
        context = user.context[-FREE_CONTEXT_LENGTH:]
        ctx_limit = FREE_CONTEXT_LENGTH

    if context:
        if context[0]["role"] == "assistant":
            messages += context[1:]
        else:
            messages += context

    ctx_items = len(context)

    messages.append({"role": "user", "content": content})

    extra_body = None
    if MODELS[user.cur_model].reasoning:
        extra_body = {"reasoning": {"enabled": True}}

    logger.info(
        "llm_payload req_id=%s tg_id=%s model=%s openrouter_model=%s role=%s ctx_items=%s ctx_limit=%s reasoning=%s",
        req_id,
        telegram_id,
        user.cur_model,
        MODELS[user.cur_model].openrouter_id,
        has_role,
        ctx_items,
        ctx_limit,
        bool(extra_body),
    )

    try:
        t_create = time.monotonic()
        stream = await client.chat.completions.create(
            model=MODELS[user.cur_model].openrouter_id,
            messages=messages,
            stream=True,
            extra_body=extra_body,
        )
        logger.info(
            "openrouter_create_ok req_id=%s tg_id=%s dt_ms=%s",
            req_id, telegram_id, int((time.monotonic() - t_create) * 1000)
        )
    except Exception:
        logger.exception(
            "openrouter_create_failed req_id=%s tg_id=%s model=%s dt_ms=%s",
            req_id, telegram_id, user.cur_model, int((time.monotonic() - t0) * 1000)
        )
        raise

    response = []
    chunks = 0
    out_len = 0
    first_token_at = None
    try:
        async for chunk in stream:
            chunks += 1
            delta = chunk.choices[0].delta
            part = getattr(delta, "content", None)
            if part:
                if first_token_at is None:
                    first_token_at = time.monotonic()
                    logger.info(
                        "llm_first_token req_id=%s tg_id=%s ttft_ms=%s",
                        req_id, telegram_id, int((first_token_at - t0) * 1000)
                    )
                response.append(part)
                yield part
    except Exception:
        logger.exception(
            "openrouter_stream_failed req_id=%s tg_id=%s model=%s dt_ms=%s chunks=%s out_len=%s",
            req_id, telegram_id, user.cur_model, int((time.monotonic() - t0) * 1000), chunks, out_len
        )
        raise

    try:
        await update_context(telegram_id, "user", content)
        await update_context(telegram_id, "assistant", "".join(response))
        await update_request_cnt(telegram_id)
        logger.info(
            "llm_ctx_ok req_id=%s tg_id=%s",
            req_id, telegram_id
        )
    except Exception:
        logger.exception("context_update_failed tg_id=%s", telegram_id)
        logger.exception(
            "llm_ctx_failed req_id=%s tg_id=%s",
            req_id, telegram_id
        )

    logger.info(
        "llm_ok req_id=%s tg_id=%s dt_ms=%s chunks=%s out_len=%s",
        req_id, telegram_id, int((time.monotonic() - t0) * 1000), chunks, out_len
    )
