import asyncio
from typing import Tuple, List

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup as Markup
from sqlalchemy import and_, not_
from sqlalchemy.ext.asyncio import async_sessionmaker

from ...bot.utils.formatters import format_weekly_notify_to_message
from ...bot.utils.messages import send_message
from ...bot.utils.texts.buttons import TextButton, ButtonCode
from ...bot.utils.texts.messages import TextMessage, MessageCode
from ...config import BOUNTIES_CREATOR_BOT_URL
from ...db.models import IssueDB, ChatDB


async def get_update_weekly_stats(sessionmaker: async_sessionmaker) -> Tuple[int, int, int]:
    """
    Retrieve statistics on active, approved assignee, and suggested opinions.

    :param sessionmaker: Asyncio sessionmaker for database interaction.
    :return: Tuple of active, approved assignee, and suggested opinions.
    """
    # Filters for active issues
    active_filters = [
        and_(
            IssueDB.labels.contains("Approved"),
            IssueDB.assignee.is_not(None),
            IssueDB.state == "open",
        )
    ]
    # Filters for approved assignee issues
    approved_filters = [
        and_(
            IssueDB.labels.contains("Approved"),
            IssueDB.assignee.is_(None),
            IssueDB.state == "open",
        )
    ]
    # Filters for suggested opinions
    suggested_filters = [
        and_(
            not_(IssueDB.labels.contains("Approved")),
            IssueDB.state == "open",
        )
    ]

    # Retrieve counts for each category
    num_active = await IssueDB.get_count(sessionmaker, active_filters)
    num_approved_assignee = await IssueDB.get_count(sessionmaker, approved_filters)
    num_suggested_opinions = await IssueDB.get_count(sessionmaker, suggested_filters)

    return num_active, num_approved_assignee, num_suggested_opinions


async def weekly_update_digest() -> None:
    """
    Send weekly digest updates to all chat subscribers.
    """
    loop = asyncio.get_event_loop()
    bot: Bot = loop.__getattribute__("bot")
    sessionmaker: async_sessionmaker = loop.__getattribute__("sessionmaker")

    # Retrieve all chats ids
    chats_ids: List[int, None] = await ChatDB.get_all_ids(sessionmaker)
    # Get statistics
    stats = await get_update_weekly_stats(sessionmaker)

    # Get message text and button
    message_text = await TextMessage(sessionmaker).get(MessageCode.WEEKLY_DIGEST)
    primary_button = await TextButton(sessionmaker).get_button(
        ButtonCode.CREATE_BOUNTY, url=BOUNTIES_CREATOR_BOT_URL
    )

    # Format message text and create reply markup
    text = format_weekly_notify_to_message(message_text, stats)
    reply_markup = Markup(inline_keyboard=[[primary_button]])

    # Send messages to all chats
    for chat_id in chats_ids:
        await send_message(bot, chat_id, text, reply_markup=reply_markup)
