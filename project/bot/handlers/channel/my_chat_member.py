import asyncio

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
)
from aiogram.types import ChatMemberUpdated

from project.bot.manager import Manager
from project.db.models import ChatDB

router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    ),
    F.chat.type == ChatType.CHANNEL,
)
async def bot_added_to_channel(event: ChatMemberUpdated, manager: Manager) -> None:
    """
    Bot was added to group.
    """
    await asyncio.sleep(1.0)
    await ChatDB.create_or_update(
        manager.sessionmaker,
        id=event.chat.id,
        type=ChatType.CHANNEL,
        title=event.chat.title,
        username=event.chat.username,
    )
