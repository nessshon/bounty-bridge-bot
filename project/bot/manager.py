from contextlib import suppress
from typing import Any, Dict

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
    User,
)
from aiogram.types.base import (
    UNSET_DISABLE_WEB_PAGE_PREVIEW,
)
from sqlalchemy.ext.asyncio import async_sessionmaker
from sulguk import SULGUK_PARSE_MODE

from project.bot.utils.texts.buttons import TextButton
from project.bot.utils.texts.messages import TextMessage
from project.config import Config
from project.db.models import UserDB

MESSAGE_EDIT_ERRORS = [
    "no text in the message",
    "message can't be edited",
    "message is not modified",
    "message to edit not found",
]
MESSAGE_DELETE_ERRORS = [
    "message can't be deleted",
    "message to delete not found",
]


class Manager:
    """
    Manager class for handling various tasks in a Telegram bot.

    Args:
        emoji (str): The emoji string.
        data (Dict[str, Any]): Dictionary containing various data needed for bot operations.
    """

    def __init__(self, emoji: str, data: Dict[str, Any]) -> None:
        self.config: Config = data.get("config")

        self.bot: Bot = data.get("bot")
        self.state: FSMContext = data.get("state")
        self.sessionmaker: async_sessionmaker = data.get("sessionmaker")

        self.user: User = data.get("event_from_user")
        self.user_db: UserDB = data.get("user_db")

        self.text_button: TextButton = TextButton(self.sessionmaker)
        self.text_message: TextMessage = TextMessage(self.sessionmaker)

        self.__emoji = emoji
        self.__data = data

    @property
    def middleware_data(self) -> Dict[str, Any]:
        """
        Get middleware data.
        :return: The middleware data.
        """
        return self.__data

    async def get_old_message_id(self) -> int:
        """
        Get the ID of the old message from the state data.
        :return: The message ID.
        """
        data = await self.state.get_data()
        return data.get("message_id", -1)

    async def send_message(
            self,
            text: str,
            parse_mode: str | None = SULGUK_PARSE_MODE,
            disable_web_page_preview: bool | None = UNSET_DISABLE_WEB_PAGE_PREVIEW,
            disable_notification: bool | None = None,
            reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
    ) -> Message:
        """
        Send a formatted message using the specified parameters.

        :param text: The text of the message.
        :param parse_mode: The parse mode of the message (optional).
        :param disable_web_page_preview: Disable web page preview for links (optional).
        :param disable_notification: Disable notification for the message (optional).
        :param reply_markup: InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, None
        :return: The send or edited Message object.
        """
        message_id = await self.get_old_message_id()

        try:
            message = await self.bot.edit_message_text(
                text=text,
                chat_id=self.state.key.chat_id,
                message_id=message_id,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                reply_markup=reply_markup,
            )
        except TelegramBadRequest as ex:
            if not any(e in ex.message for e in MESSAGE_EDIT_ERRORS):
                raise ex
            message = await self.bot.send_message(
                text=text,
                chat_id=self.state.key.chat_id,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_web_page_preview,
                disable_notification=disable_notification,
                reply_markup=reply_markup,
            )
            await self.delete_previous_message()
            await self.state.update_data(message_id=message.message_id)

        return message

    @staticmethod
    async def delete_message(message: Message) -> None:
        """
        Delete a message.

        :param message: The message to be deleted.
        :return: None
        """
        with suppress(TelegramBadRequest):
            await message.delete()

    async def delete_previous_message(self) -> None | Message:
        """
        Delete the previous message.

        This method attempts to delete the previous message identified by the stored message ID. If deletion is not
        possible (e.g., due to a message not found error), it attempts to edit the previous message with a placeholder
        __emoji. If editing is also not possible, it raises TelegramBadRequest with the appropriate error message.

        :return: The edited Message object or None if no previous message was found.
        :raises TelegramBadRequest: If there is an issue with deleting or editing the previous message.
        """
        message_id = await self.get_old_message_id()
        if not message_id: return  # noqa:E701

        try:
            await self.bot.delete_message(
                message_id=message_id,
                chat_id=self.user.id,
            )
        except TelegramBadRequest as ex:
            if any(e in ex.message for e in MESSAGE_DELETE_ERRORS):
                try:
                    return await self.bot.edit_message_text(
                        message_id=message_id,
                        chat_id=self.user.id,
                        text=self.__emoji,
                    )
                except TelegramBadRequest as ex:
                    if not any(e in ex.message for e in MESSAGE_EDIT_ERRORS):
                        raise ex
