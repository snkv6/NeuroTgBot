from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonCommands

CMD_START = "start"
CMD_HELP = "help"
CMD_PROFILE = "profile"
CMD_ROLE = "role"
CMD_MODEL = "model"
CMD_BILLING = "billing"
CMD_DELETE_CONTEXT = "delete_context"


async def setup_bot(bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command=CMD_START, description="Запуск"),
            BotCommand(command=CMD_HELP, description="Помощь"),
            BotCommand(command=CMD_PROFILE, description="Профиль"),
            BotCommand(command=CMD_ROLE, description="Выбрать / удалить роль"),
            BotCommand(command=CMD_MODEL, description="Сменить модель"),
            BotCommand(command=CMD_BILLING, description="Оплата"),
            BotCommand(command=CMD_DELETE_CONTEXT, description="Удалить контекст")
        ],
        scope=BotCommandScopeDefault(),
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.set_my_short_description(
        short_description="Я нейробот: отвечаю на вопросы, пишу код, объясняю темы.\n\nАдминистратор: @snkv6",
        language_code="ru",
    )
    await bot.set_my_description(
        description="Напиши запрос обычным текстом. Могу: объяснять темы, генерировать идеи, писать/править код.",
        language_code="ru",
    )
