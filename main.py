# import os
# import asyncio
# import logging
# import base
#
# from aiogram import Bot, Dispatcher, F, Router
# from aiogram.filters import CommandStart, Command
# from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BotCommand, MenuButtonCommands, \
#     BotCommandScopeDefault
# from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
# from aiogram.fsm.state import StatesGroup, State
# from aiogram.fsm.context import FSMContext
#
# # степа тестил
# from base import add_user, update_premium, update_context
# from openroutertest import request
#
# router = Router()
#
#
# def main_reply_kb():
#     kb = ReplyKeyboardBuilder()
#     kb.button(text="Помощь 🫂")
#     kb.button(text="Посмотреть профиль ℹ️")
#     kb.button(text="Задать роль 📝")
#     kb.button(text="Сменить модель 👾")
#     kb.button(text="План / оплата 💳")
#     kb.adjust(2, 2, 1)
#     return kb.as_markup(resize_keyboard=True)
#
#
# def actions_inline_kb():
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Помощь 🫂", callback_data="help")
#     kb.button(text="Посмотреть профиль ℹ️", callback_data="profile")
#     kb.button(text="Выбрать роль 📝", callback_data="role")
#     kb.button(text="Сменить модель 👾", callback_data="model")
#     kb.button(text="План / оплата 💳", callback_data="billing")
#     kb.adjust(2, 2, 1)
#     return kb.as_markup()
#
#
# @router.message(CommandStart())
# async def start(message: Message):
#     await message.answer(
#         "Привет! Я бот с нейросетями 🤖\n"
#         "Напиши запрос обычным текстом — я отвечу.\n",
#         reply_markup=main_reply_kb())
#     await message.answer("Настройки и быстрые действия:", reply_markup=actions_inline_kb())
#
#
# @router.message(Command("help"))
# @router.message(F.text == "Помощь 🫂")
# async def help_msg(message: Message):
#     await message.answer(
#         "Помощь\n\n"
#         "Как пользоваться:\n"
#         "• Просто напиши запрос обычным текстом — я отвечу.\n"
#         "• Можно просить: объяснить тему, написать/исправить код, придумать идеи, сделать конспект.\n\n"
#         "Примеры:\n"
#         "• «Объясни, что такое градиентный спуск простыми словами»\n"
#         "• «Напиши Telegram-бота на aiogram с кнопками»\n"
#         "• «Сделай краткий конспект: …»\n\n"
#         "Команды:\n"
#         "/start — запуск и меню\n"
#         "/profile — профиль\n"
#         "/role — выбрать роль\n"
#         "/model — выбрать модель\n"
#         "/billing — оплата\n"
#     )
#
#
# @router.callback_query(F.data == "help")
# async def help_cb(cb: CallbackQuery):
#     await cb.answer()
#     await help_msg(cb.message)
#
#
# @router.message(Command("profile"))
# @router.message(F.text == "Посмотреть профиль ℹ️")
# async def profile_msg(message: Message):
#     # TODO: реализовать
#     await message.answer(
#         "Ваш Профиль\n\n"
#         "Роль:\n"
#         "Модель:\n"
#         "Подписка:"
#     )
#
#
# @router.callback_query(F.data == "profile")
# async def profile_cb(cb: CallbackQuery):
#     await cb.answer()
#     await profile_msg(cb.message)
#
#
# class form_for_setting_role(StatesGroup):
#     waiting_text = State()
#
#
# def cansel_setting_role_kb():
#     kb = InlineKeyboardBuilder()
#     kb.button(text="Отмена ❌", callback_data="cansel_setting_role")
#     kb.adjust(1)
#     return kb.as_markup()
#
#
# @router.message(Command("role"))
# @router.message(F.text == "Выбрать роль 📝")
# async def role_msg(message: Message, state: FSMContext):
#     await state.set_state(form_for_setting_role.waiting_text)
#     await message.answer(
#         "Выбрать роль\n\n"
#         "Здесь можно выбрать роль, которую будет играть ИИ-агент",
#         reply_markup=cansel_setting_role_kb()
#     )
#
#
# @router.callback_query(F.data == "role")
# async def role_cb(cb: CallbackQuery):
#     await cb.answer()
#     await role_msg(cb.message)
#
#
# @router.callback_query(F.data == "cansel_setting_role")
# async def cansel_setting_role_cb(cb: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await cb.message.answer("Отменена выбора роли")
#
#
# @router.message(form_for_setting_role.waiting_text)
# async def special_handler(message: Message, state: FSMContext):
#     await state.clear()
#     await base.update_role(message.from_user.id, message.text)
#     await message.answer("Роль выбрана!")
#
#
# @router.message(Command("model"))
# @router.message(F.text == "Сменить модель 👾")
# async def model_msg(message: Message):
#     # TODO: реализовать
#     await message.answer(
#         "Сменить модель\n\n"
#         "Доступные модели:\n"
#     )
#
#
# @router.callback_query(F.data == "model")
# async def model_cb(cb: CallbackQuery):
#     await cb.answer()
#     await model_msg(cb.message)
#
#
# @router.message(Command("billing"))
# @router.message(F.text == "План / оплата 💳")
# async def billing_msg(message: Message):
#     # TODO: реализовать
#     await message.answer(
#         "План / оплата\n\n"
#         "Тут будет выбор плана и оплата.\n"
#     )
#
#
# @router.callback_query(F.data == "billing")
# async def billing_cb(cb: CallbackQuery):
#     await cb.answer()
#     await billing_msg(cb.message)
#
#
# # это писал степа надо будет причесать
# @router.message(F.text == "тест")
# async def text_msg(message: Message):
#     add_user(message.chat.id)
#     await message.answer("trjfok")
#
#
# # это писал степа надо будет причесать
# @router.message(F.text == "конт")
# async def text_msg(message: Message):
#     update_context(message.chat.id, "user", message.text)
#     await message.answer("trjfok")
#
#
# # это писал степа надо будет причесать
# @router.message(F.text == "прем")
# async def text_msg(message: Message):
#     update_premium(message.chat.id)
#     await message.answer("trjfok")
#
#
# # это писал степа надо будет причесать
# @router.message(F.text)
# async def text_msg(message: Message):
#     await message.answer(request(message.text))
#
#
# async def main():
#     logging.basicConfig(level=logging.INFO)
#
#     token = "knfleg"
#
#     bot = Bot(token=token)
#     dp = Dispatcher()
#     dp.include_router(router)
#
#     await bot.set_my_commands([
#         BotCommand(command="start", description="Запуск"),
#         BotCommand(command="help", description="Помощь"),
#         BotCommand(command="profile", description="Профиль"),
#         BotCommand(command="role", description="Выбрать роль"),
#         BotCommand(command="model", description="Сменить роль"),
#         BotCommand(command="billing", description="Оплата")
#     ],
#         scope=BotCommandScopeDefault(),
#     )
#     await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
#
#     await bot.set_my_short_description(
#         short_description="Я нейробот: отвечаю на вопросы, пишу код, объясняю темы.",
#         language_code="ru",
#     )
#     await bot.set_my_description(
#         description="Напиши запрос обычным текстом. Могу: объяснять темы, генерировать идеи, писать/править код.",
#         language_code="ru",
#     )
#
#     await dp.start_polling(bot)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
