import asyncio

from aiogram import Bot, html, Router, F
from aiogram.enums import ChatType
from aiogram.filters.chat_member_updated import (
    ChatMemberUpdatedFilter,
    JOIN_TRANSITION,
)
from aiogram.types import ChatMemberUpdated, Message
from aiogram.utils.markdown import hcode

router = Router()


@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=JOIN_TRANSITION
    ),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP})
)
async def bot_added_to_group(event: ChatMemberUpdated, bot: Bot):
    """
    Bot was added to group.

    :param event: an event from Telegram of type "my_chat_member"
    :param bot: bot who message was addressed to
    """
    await asyncio.sleep(1.0)
    await bot.send_message(event.chat.id, text=hcode(event.chat.id))


@router.message(F.migrate_to_chat_id)
async def group_to_supergroup_migration(message: Message, bot: Bot):
    """
    Group was migrated to supergroup.

    :param message: an event from Telegram of type "migrate_to_chat_id"
    :param bot: bot who message was addressed to
    """
    await bot.send_message(message.migrate_to_chat_id, text=hcode(message.migrate_to_chat_id))
