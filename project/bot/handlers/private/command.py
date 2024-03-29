from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from project.bot.handlers.private.windows import Window
from project.bot.manager import Manager

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(Command("start"))
async def start_command(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.main_menu(manager, send_mode="send")
    await manager.delete_message(message)


@router.message(Command("top"))
async def top_command(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.top_contributors(manager, send_mode="send")
    await manager.delete_message(message)


@router.message(Command("weekly_digest"))
async def weekly_digest_command(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.weekly_digest(manager, send_mode="send")
    await manager.delete_message(message)
