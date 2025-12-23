import logging

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_MODEL, CB_MODEL, CB_MODEL_START, CB_CANCEL_MODEL, model_inline_kb
from features.menu.setup import CMD_MODEL
from database.users import update_model, check_premium, get_model, delete_context
from config.test import MODELS

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command(CMD_MODEL))
@router.message(F.text == BTN_MODEL)
async def model_msg(message: Message, telegram_id=None):
    logger.info("model_menu_open tg_id=%s", telegram_id)
    if telegram_id is None:
        telegram_id = message.from_user.id
    inline_kb = await model_inline_kb(telegram_id)
    text = "<b>Сменить модель 👾\n\nДоступные модели:</b>\n\n"
    premium = await check_premium(telegram_id)
    if premium:
        s_p = "✅"
        s_np = ""
    else:
        s_p = "🔒"
        s_np = "✅"
    for model, model_data in MODELS.items():
        text = text + "<b>" + model + "</b>:\n"
        if model_data.premium_only or premium:
            text = text + f"\t{s_p} Доступно {model_data.premium_per_day} запросов с подпиской\n"
        else:
            text = text + f"\t{s_np} Доступно {model_data.free_per_day} запросов без подписки\n"
            text = text + f"\t{s_p} Доступно {model_data.premium_per_day} запросов с подпиской\n"
        text = text + "\n"
    await message.answer(text,
                         parse_mode=ParseMode.HTML,
                         reply_markup=inline_kb)


@router.callback_query(F.data == CB_MODEL)
async def model_cb(cb: CallbackQuery):
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await model_msg(cb.message, cb.from_user.id)

@router.callback_query(F.data.startswith(CB_MODEL_START))
async def change_model_cb_(cb: CallbackQuery):
    await cb.answer()
    tg_id = cb.from_user.id
    try:
        model = cb.data.split(":")[1]
    except ValueError:
        logger.warning("bad_callback tg_id=%s data=%r", tg_id, cb.data)
        await cb.message.answer("Кнопка устарела. Откройте меню моделей заново.")
        return

    if model not in MODELS:
        logger.warning("unknown_model_in_callback tg_id=%s model=%r data=%r", tg_id, model, cb.data)
        await cb.message.answer("Эта модель недоступна. Откройте меню моделей заново.")
        return

    logger.info("ui_model_selected tg_id=%s plan_id=%s", cb.from_user.id, model)

    verdict = ""

    if MODELS[model].premium_only and not (await check_premium(cb.from_user.id)):
        logger.info("model_change_denied tg_id=%s model=%s reason=no_premium", tg_id, model)
        verdict = "Вы не можете выбрать эту модель без подписки"
    else:
        if MODELS[await get_model(telegram_id=cb.from_user.id)].vendor != MODELS[model].vendor:
            verdict = " и контекст очищен в связи с переходом на другого вендора"
            await delete_context(telegram_id=cb.from_user.id)
        await update_model(cb.from_user.id, model)
        try:
            await cb.message.delete()
        except TelegramBadRequest:
            pass
        verdict = "Модель изменена" + verdict
    await cb.message.answer(verdict)

@router.callback_query(F.data == CB_CANCEL_MODEL)
async def cancel_model_cb(cb: CallbackQuery):
    logger.info("ui_cansel_model tg_id=%s", cb.from_user.id)
    await cb.answer()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
