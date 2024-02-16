import asyncio

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
)
from aiogram.types import ChatMemberUpdated, Message

from project.bot.manager import Manager
from project.db.models import ChatDB

router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    ),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def bot_added_to_group(event: ChatMemberUpdated, manager: Manager) -> None:
    """
    Bot was added to group.
    """
    await asyncio.sleep(1.0)
    await ChatDB.create_or_update(
        manager.sessionmaker,
        id=event.chat.id,
        type=event.chat.type,
        title=event.chat.title,
        username=event.chat.username,
    )


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(message: Message, manager: Manager) -> None:
    """
    Group was migrated to supergroup.
    """
    await ChatDB.create_or_update(
        manager.sessionmaker,
        id=message.migrate_to_chat_id,
        type=message.chat.type,
        title=message.chat.title,
        username=message.chat.username,
    )
