import logging
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest


from features.menu.admin_keyboards import BTN_MESSAGE, CB_MESSAGE_ALL, CB_MESSAGE_PREMIUM, CB_MESSAGE_NON_PREMIUM, \
    CB_PREVIEW_CANCEL, CB_PREVIEW_CONFIRM, CB_MESSAGE_CANCEL, CB_MESSAGE_START, message_inline_kb, preview_inline_kb
from features.menu.admin_setup import CMD_MESSAGE
from features.menu.states import message_form
from database.users import get_all_tg_ids, get_all_premium_users_tg_ids, get_all_non_premium_users_tg_ids
from bot_instance import client_bot

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command(CMD_MESSAGE))
@router.message(F.text == BTN_MESSAGE)
async def message_msg(message: Message):
    logger.info("admin_message_open tg_id=%s", message.from_user.id)
    await message.answer(
        "Выберите, кому отправить сообщение",
        reply_markup=message_inline_kb()
    )


@router.callback_query(F.data == CB_MESSAGE_CANCEL)
async def cancel_message_cb(cb: CallbackQuery, state: FSMContext):
    logger.info("admin_message_cancel tg_id=%s", cb.from_user.id)
    await state.clear()
    await cb.answer("Отменено")
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass

@router.callback_query(F.data.startswith(CB_MESSAGE_START))
async def message_target_cb(cb: CallbackQuery, state: FSMContext):
    try:
        target = cb.data.split(":")[1]
    except (ValueError, IndexError):
        logger.warning("bad_callback tg_id=%s data=%r", cb.from_user.id, cb.data)
        await cb.message.answer("Кнопка устарела")
        return
    await state.set_state(message_form.waiting_text)
    await state.update_data(target=target)
    logger.info("admin_target_selected tg_id=%s target=%s", cb.from_user.id, target)
    await cb.message.answer("Введите сообщение")

@router.message(message_form.waiting_text, F.text)
async def message_text(message: Message, state: FSMContext):
    logger.info("admin_message_written tg_id=%s len=%s", message.from_user.id, len(message.text))
    await state.update_data(message=message.text)
    await message.answer("Превью:\n\n" + message.text, reply_markup=preview_inline_kb())


@router.callback_query(message_form.waiting_text, F.data == CB_PREVIEW_CANCEL)
async def cancel_preview_cb(cb: CallbackQuery, state: FSMContext):
    logger.info("admin_preview_cancel tg_id=%s", cb.from_user.id)
    await state.update_data(message=None)
    await cb.answer("Отменено")
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass
    await cb.message.answer("Выберите другое сообщение")

@router.callback_query(message_form.waiting_text, F.data == CB_PREVIEW_CONFIRM)
async def preview_confirm_cb(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    target = data.get("target")
    message = data.get("message")
    await state.clear()
    if target == CB_MESSAGE_ALL:
        ids = await get_all_tg_ids()
    elif target == CB_MESSAGE_PREMIUM:
        ids = await get_all_premium_users_tg_ids()
    elif target == CB_MESSAGE_NON_PREMIUM:
        ids = await get_all_non_premium_users_tg_ids()
    else:
        logger.warning("admin_unknown_target tg_id=%s target=%s data=%r", cb.from_user.id, target, cb.data)
        await cb.message.answer("Попробуйте еще раз")
        return

    if message is None:
        logger.warning("admin_empty_message tg_id=%s", cb.from_user.id)
        await cb.message.answer("Попробуйте еще раз")
        return

    sent = 0
    failed = 0
    for id in ids:
        try:
            sent += 1
            await client_bot.send_message(id, message)
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
            logger.warning("admin_wrong_target target_id=%s tg_id=%s", id, cb.from_user.id)

    logger.info("admin_message_sent tg_id=%s target=%s sent=%s failed=%s", cb.from_user.id, target, sent, failed)
    await cb.message.answer(f"Было отправлено: {sent}\nНе удалось отправить:{failed}")



