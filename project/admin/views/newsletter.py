import asyncio
from typing import Dict, Any, List, Union

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup as Markup
from aiogram.utils.keyboard import InlineKeyboardButton as Button
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from starlette.requests import Request

from starlette_admin import *
from starlette_admin.contrib.sqla.fields import ImageField
from starlette_admin.exceptions import ActionFailed, FormValidationError
from sulguk import SULGUK_PARSE_MODE

from ._model_view import CustomModelView
from ...db.models import NewsletterDB, ChatDB, UserDB


class NewsletterView(CustomModelView):
    """
    View for managing newsletters table in the admin panel.
    """
    fields = [
        IntegerField(
            NewsletterDB.id.name, "ID",
            read_only=True,
        ),
        ImageField(
            NewsletterDB.image.name, "Image",
            help_text="Note: Upload limit is 10MB.",
        ),
        TinyMCEEditorField(
            NewsletterDB.content.name, "Content",
            required=False,
            toolbar=(
                "undo redo | bold italic underline strikethrough | blockquote | removeformat"
            ),
            maxlength=4098,
            help_text="Note: If you create a post with an image, the text limit is 1024 characters.",
        ),
        ListField(
            CollectionField(
                NewsletterDB.buttons.name,
                fields=[
                    StringField(
                        "text",
                        required=True,
                    ),
                    URLField(
                        "url",
                        required=True,
                    ),
                ],
            ),
        ),
        EnumField(
            NewsletterDB.chat_type.name, "Chat type",
            required=True,
            choices=[
                ("all", "All"),
                ("private", "Private"),
                ("channel", "Channel"),
                ("group", "Group"),
            ],
            select2=False,
            help_text="Select the chat type to send the newsletter.",
        ),
        DateTimeField(
            NewsletterDB.created_at.name, "Created at",
            read_only=True,
        ),
    ]
    exclude_fields_from_list = [NewsletterDB.buttons.name]
    exclude_fields_from_create = [NewsletterDB.created_at.name, "user"]
    exclude_fields_from_edit = [NewsletterDB.created_at.name, "user"]

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        self.custom_validate(data)
        return await super().create(request, data)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        self.custom_validate(data)
        return await super().edit(request, pk, data)

    @row_action(
        name="send_preview",
        text="Send preview",
        action_btn_class="btn-outline-primary",
    )
    async def send_preview_action(self, request: Request, pk: int) -> str:
        """
        Row action to send a preview of the newsletter to the admin.
        """
        bot: Bot = request.state.bot
        admin_id = request.session.get("id")
        session: AsyncSession = request.state.session
        newsletter: Union[NewsletterDB, None] = await session.get(NewsletterDB, pk)

        try:
            await self.send_message(newsletter, bot, admin_id)
        except Exception as e:
            raise ActionFailed(str(e))

        return f"A message has been sent to you in chat with the bot!"

    @row_action(
        name="run_newsletter",
        text="Run newsletter",
        confirmation="Are you sure you want to run this newsletter?",
        action_btn_class="btn-outline-success",
        submit_btn_text="Continue",
        submit_btn_class="btn-outline-success",
    )
    async def run_newsletter_action(self, request: Request, pk: int) -> str:
        """
        Row action to run the newsletter and send it to the selected chat type.
        """
        bot: Bot = request.state.bot
        sessionmaker = request.state.sessionmaker
        session: AsyncSession = request.state.session

        newsletter: Union[NewsletterDB, None] = await session.get(NewsletterDB, pk)
        _ = asyncio.create_task(self.run_newsletter(newsletter, bot, sessionmaker))
        return "The newsletter is up and running!"

    @staticmethod
    def custom_validate(data: Dict[str, Any]) -> None:
        """
        Custom validation for newsletter creation and editing.
        """
        if not data.get("image")[1] and len(data.get("content")) == 0:
            raise FormValidationError({"content": "Content or image is required."})

        if len(data.get("content")) > 4096:
            raise FormValidationError({"content": "The text limit is 4096 characters."})

        if data.get("image"):
            if data.get("content") and len(data.get("content")) > 1024:
                raise FormValidationError({"content": "The text limit with image is 1024 characters."})

    @classmethod
    async def run_newsletter(cls, newsletter: NewsletterDB, bot: Bot, sessionmaker: async_sessionmaker) -> None:
        """
        Run the newsletter and send it to the selected chat type.
        """
        if newsletter.chat_type == "all":
            chats = await ChatDB.get_all_ids(sessionmaker)
        elif newsletter.chat_type == "private":
            chats = await UserDB.get_all_ids(sessionmaker)
        else:
            chats = await ChatDB.get_ids(sessionmaker, newsletter.chat_type)

        for chat_id in chats:
            try:
                await cls.send_message(newsletter, bot, chat_id)
            except TelegramRetryAfter as e:
                # If rate limited, wait and try again
                await asyncio.sleep(e.retry_after)
                await cls.send_message(newsletter, bot, chat_id)
            except (TelegramBadRequest, Exception):
                # If chat is not found, or bot is blocked, or any other error, skip.
                pass
            await asyncio.sleep(0.05)

    @classmethod
    async def send_message(cls, newsletter: NewsletterDB, bot: Bot, chat_id: int) -> None:
        """
        Send a message with the newsletter content and buttons to a chat.
        """
        if newsletter.image_path:
            await bot.send_photo(
                chat_id=chat_id,
                photo=BufferedInputFile.from_file(newsletter.image_path),
                caption=newsletter.content,
                parse_mode=SULGUK_PARSE_MODE,
                reply_markup=cls.build_buttons(newsletter.buttons),
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=newsletter.content,
                parse_mode=SULGUK_PARSE_MODE,
                reply_markup=cls.build_buttons(newsletter.buttons),
            )

    @staticmethod
    def build_buttons(buttons: List[Dict[str, str]]) -> Markup:
        """
        Build inline buttons from a list of dictionaries.
        """
        inline_keyboard = [
            [
                Button(text=button.get("text"), url=button.get("url"))
            ] for button in buttons
        ]
        return Markup(inline_keyboard=inline_keyboard)
