import asyncio
from datetime import datetime, timedelta
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


async def _get_stats(sessionmaker: async_sessionmaker) -> Tuple[int, int, int]:
    """
    Retrieve statistics on active, approved assignee, and suggested opinions.

    :param sessionmaker: Asyncio sessionmaker for database interaction.
    :return: Tuple of active, approved assignee, and suggested opinions.
    """
    current_date = datetime.now().date()
    start_last_week, end_last_week = _get_last_week_period(current_date)

    # Define date filters for the week
    _date_filters = and_(
        IssueDB.created_at >= start_last_week,
        IssueDB.created_at <= end_last_week,
    )
    # Filters for active issues
    active_filters = [
        _date_filters,
        and_(
            IssueDB.assignee.is_not(None),
            IssueDB.state == "open",
        )
    ]
    # Filters for approved assignee issues
    approved_filters = [
        _date_filters,
        and_(
            IssueDB.labels.contains("Approved"),
            IssueDB.assignee.is_(None),
            IssueDB.state == "open",
        )
    ]
    # Filters for suggested opinions
    suggested_filters = [
        _date_filters,
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


def _get_last_week_period(current_date: datetime.date) -> Tuple[datetime.date, datetime.date]:
    """
    Calculate the start and end dates of the previous week based on the current date.

    :param current_date: The current date.
    :return: Tuple of the start and end dates of the previous week.
    """
    start_current_week = current_date - timedelta(days=current_date.weekday())
    start_last_week = start_current_week - timedelta(days=7)
    end_last_week = start_last_week + timedelta(days=6)

    return start_last_week, end_last_week


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
    stats = await _get_stats(sessionmaker)

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
