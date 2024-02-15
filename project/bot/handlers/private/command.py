from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from project.bot.handlers.private.windows import Window

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(Command("start"))
async def handler(message: Message, manager) -> None:
    await Window.main_menu(manager)
    await manager.delete_message(message)


@router.message(Command("weekly_digest"))
async def handler(message: Message, manager) -> None:
    from ....scheduler.tasks.weekly_update_digest import weekly_update_digest
    await weekly_update_digest()
    await manager.delete_message(message)
