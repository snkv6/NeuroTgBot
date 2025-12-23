import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from features.menu.keyboards import BTN_ROLE, CB_ROLE, CB_CANCEL_ROLE, CB_DELETE_ROLE, BTN_TEXTS, special_role_inline_kb
from features.menu.setup import CMD_ROLE
from features.states import role_form
from database.users import update_role

router = Router()

logger = logging.getLogger(__name__)


@router.message(Command(CMD_ROLE))
@router.message(F.text == BTN_ROLE)
async def role_msg(message: Message, state: FSMContext):
    logger.info("ui_role_menu_open tg_id=%s", message.from_user.id)
    await state.set_state(role_form.waiting_text)
    await message.answer(
        "Выбрать роль 📝\n\n"
        "Здесь можно выбрать роль, которую будет играть ИИ-агент\n"
        "Чтобы удалить ранее выбранную роль просто нажми на кнопку",
        reply_markup=special_role_inline_kb()
    )


@router.callback_query(F.data == CB_ROLE)
async def role_cb(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await role_msg(cb.message, state=state)
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == CB_CANCEL_ROLE)
async def cancel_setting_role_cb(cb: CallbackQuery, state: FSMContext):
    logger.info("ui_role_cancel tg_id=%s", cb.from_user.id)
    await cb.answer("Отменено")
    await state.clear()
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass


@router.callback_query(F.data == CB_DELETE_ROLE)
async def delete_role_cb(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    logger.info("ui_role_deleted tg_id=%s", cb.from_user.id)
    await update_role(cb.from_user.id, None)
    await cb.answer("Роль удалена")
    try:
        await cb.message.delete()
    except TelegramBadRequest:
        pass

@router.message(role_form.waiting_text, F.text.in_(BTN_TEXTS))
async def btn_texts_in_role(message: Message, state: FSMContext):
    logger.info("ui_wrong_role tg_id=%s", message.from_user.id)
    await message.answer(
        "Вы не можете выбрать эту роль.\n"
        "Пожалуйста, введите роль обычным текстом или нажмите «Отмена»."
    )

@router.message(role_form.waiting_text, F.text, ~F.text.in_(BTN_TEXTS))
async def special_handler(message: Message, state: FSMContext):
    logger.info("ui_model_selected tg_id=%s len=%s", message.from_user.id, len(message.text))
    await state.clear()
    await update_role(message.from_user.id, message.text)
    await message.answer("Роль выбрана!")
