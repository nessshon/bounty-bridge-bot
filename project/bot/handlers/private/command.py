from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from project.bot.handlers.private.windows import Window
from project.bot.manager import Manager

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(Command("start"))
async def handler(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.main_menu(manager)
    await manager.delete_message(message)
