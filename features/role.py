from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from features.menu.keyboards import BTN_ROLE, CB_ROLE, CB_CANSEL_ROLE, cancel_role_kb
from features.menu.setup import CMD_ROLE
from features.states import role_form
from base import update_role

router = Router()

@router.message(Command(CMD_ROLE))
@router.message(F.text == BTN_ROLE)
async def role_msg(message: Message, state: FSMContext):
    await state.set_state(role_form.waiting_text)
    await message.answer(
        "Выбрать роль\n\n"
        "Здесь можно выбрать роль, которую будет играть ИИ-агент",
        reply_markup=cancel_role_kb()
    )


@router.callback_query(F.data == CB_ROLE)
async def role_cb(cb: CallbackQuery):
    await cb.answer()
    await role_msg(cb.message)


@router.callback_query(F.data == CB_CANSEL_ROLE)
async def cansel_setting_role_cb(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.answer("Отменена выбора роли")


@router.message(role_form.waiting_text)
async def special_handler(message: Message, state: FSMContext):
    await state.clear()
    update_role(message.from_user.id, message.text)
    await message.answer("Роль выбрана!")