from aiogram.types import BotCommand, BotCommandScopeDefault, MenuButtonCommands

CMD_STAT = "stat"
CMD_MESSAGE = "message"


async def admin_setup_bot(bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command=CMD_STAT, description="Статистика"),
            BotCommand(command=CMD_MESSAGE, description="Отправить сообщение")
        ],
        scope=BotCommandScopeDefault(),
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    await bot.set_my_short_description(
        short_description="Админ-бот LLMs HSE",
        language_code="ru",
    )
    await bot.set_my_description(
        description="Админ-бот LLMs HSE",
        language_code="ru",
    )
