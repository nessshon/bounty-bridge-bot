from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup as Markup

from project.bot.handlers.private.windows import Window
from project.bot.manager import Manager
from project.bot.utils.formatters import format_weekly_notify_to_message
from project.bot.utils.texts.buttons import ButtonCode
from project.bot.utils.texts.messages import MessageCode
from project.config import BOUNTIES_CREATOR_BOT_URL
from project.scheduler.tasks.weekly_update_digest import get_update_weekly_stats

router = Router()
router.message.filter(F.chat.type == "private")


@router.message(Command("start"))
async def start_command(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.main_menu(manager)
    await manager.delete_message(message)


@router.message(Command("top"))
async def top_command(message: Message, manager: Manager) -> None:
    await manager.state.update_data(page=1)  # Set default page
    await Window.top_contributors(manager)
    await manager.delete_message(message)


@router.message(Command("weekly_digest"))
async def weekly_digest_command(message: Message, manager: Manager) -> None:
    stats = await get_update_weekly_stats(manager.sessionmaker)

    message_text = await manager.text_message.get(MessageCode.WEEKLY_DIGEST)
    primary_button = await manager.text_button.get_button(
        ButtonCode.CREATE_BOUNTY, url=BOUNTIES_CREATOR_BOT_URL
    )
    text = format_weekly_notify_to_message(message_text, stats)
    reply_markup = Markup(inline_keyboard=[[primary_button]])

    await manager.send_message(text, reply_markup=reply_markup)
    await manager.delete_message(message)
