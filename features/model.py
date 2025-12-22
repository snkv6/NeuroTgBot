from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_MODEL, CB_MODEL, CB_MODEL_START, model_inline_kb
from features.menu.setup import CMD_MODEL
from database.users import update_model, check_premium
from config.test import MODELS

router = Router()


@router.message(Command(CMD_MODEL))
@router.message(F.text == BTN_MODEL)
async def model_msg(message: Message, telegram_id=None):
    if telegram_id is None:
        telegram_id = message.from_user.id
    inline_kb = await model_inline_kb(telegram_id)
    text = "<b>Сменить модель 👾</b>\n\nДоступные модели:\n"
    premium = await check_premium(telegram_id)
    if premium:
        s_p = "✅"
        s_np = ""
    else:
        s_p = "🔒"
        s_np = "✅"
    for model, model_data in MODELS.items():
        text = text + model + ":\n"
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
    model = cb.data.split(":")[1]
    if MODELS[model].premium_only and not (await check_premium(cb.from_user.id)):
        await cb.message.answer("Вы не можете выбрать эту модель без подписки")
    else:
        await update_model(cb.from_user.id, model)
        try:
            await cb.message.delete()
        except TelegramBadRequest:
            pass
        await cb.message.answer("Модель изменена")
