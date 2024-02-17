from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
)


async def bot_commands_setup(bot: Bot) -> None:
    """
    Setup bot commands.

    :param bot: The Bot object.
    """
    commands = [
        BotCommand(command="start", description="Restart bot"),
        BotCommand(command="top", description="Top contributors"),
    ]

    # Set commands
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeAllPrivateChats(),
    )


async def bot_commands_delete(bot: Bot) -> None:
    """
    Delete bot commands.

    :param bot: The Bot object.
    """
    # Delete commands
    await bot.delete_my_commands(
        scope=BotCommandScopeAllPrivateChats(),
    )
