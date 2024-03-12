import asyncio
import re
from contextlib import suppress
from datetime import datetime
from typing import Dict, Any, List, Union, Optional, Sequence
from uuid import uuid4

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from aiogram.types import BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup as Markup
from aiogram.utils.keyboard import InlineKeyboardButton as Button
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.requests import Request

from starlette_admin import *
from starlette_admin.contrib.sqla.fields import ImageField
from starlette_admin.exceptions import ActionFailed, FormValidationError
from sulguk import SULGUK_PARSE_MODE

from ._model_view import CustomModelView
from .fields.tiny_mceeditor import TINY_TOOLBAR, TINY_EXTRA_OPTIONS
from ...bot.utils.formatters import format_weekly_notify_to_message
from ...config import Config
from ...db.models import NewsletterDB, ChatDB, UserDB, AdminDB
from ...scheduler.tasks.weekly_update_digest import get_update_weekly_stats


class NewsletterView(CustomModelView):
    """
    View for managing newsletters table in the admin panel.
    """
    fields = [
        IntegerField(
            NewsletterDB.id.name, "ID",
            read_only=True,
        ),
        StringField(
            NewsletterDB.job_id.name, "Job ID",
            read_only=True,
            exclude_from_list=True,
            exclude_from_detail=True,
            help_text="Unique identifier for job in the scheduler. (auto generated)",
        ),
        ImageField(
            NewsletterDB.image.name, "Image",
            help_text="Note: Upload limit is 10MB.",
        ),
        TinyMCEEditorField(
            NewsletterDB.content.name, "Content",
            required=False,
            toolbar=TINY_TOOLBAR,
            extra_options=TINY_EXTRA_OPTIONS,
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
                ("admin", "Admin"),
                ("private", "Private"),
                ("channel", "Channel"),
                ("group", "Group"),
            ],
            select2=False,
            help_text="Select the chat type to send the newsletter.",
        ),
        BooleanField(
            NewsletterDB.broadcast.name, "Broadcast",
            required=False,
            help_text="Enable to schedule sending the newsletter.",
        ),
        DateTimeField(
            NewsletterDB.start_date.name, "Start date",
            required=False,
            help_text="Select the date to send the newsletter.",
        ),
        StringField(
            NewsletterDB.start_cron.name, "Start cron",
            required=False,
            help_text="Enter the cron expression to send the newsletter. "
                      "Format: minute, hour, day, month, day of week.",
            placeholder="*/5 * * * *",
        ),
        DateTimeField(
            NewsletterDB.created_at.name, "Created at",
            read_only=True,
        ),
    ]
    exclude_fields_from_list = [NewsletterDB.buttons.name]
    exclude_fields_from_create = [NewsletterDB.created_at.name]
    exclude_fields_from_edit = [NewsletterDB.created_at.name]
    fields_default_sort = (NewsletterDB.id, (NewsletterDB.created_at.name, True))

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        self._custom_validate(request, data)
        return await super().create(request, data)

    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        self._custom_validate(request, data)
        return await super().edit(request, pk, data)

    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        scheduler: AsyncIOScheduler = request.state.scheduler
        objs: Sequence[NewsletterDB] = await self.find_by_pks(request, pks)
        for obj in objs:
            with suppress(JobLookupError):
                scheduler.remove_job(obj.job_id)
        return await super().delete(request, pks)

    @row_action(
        name="send_preview",
        text="Send preview",
        action_btn_class="btn-outline-primary",
    )
    async def send_preview_action(self, request: Request, pk: int) -> str:
        """
        Row action to send a preview of the newsletter to the admin.
        """
        # Accessing the session and retrieving the newsletter by primary key
        session: AsyncSession = request.state.session
        newsletter: Union[NewsletterDB, None] = await session.get(NewsletterDB, pk)

        # Formatting the newsletter using a helper method
        newsletter = await self.newsletter_format(newsletter, request.state.sessionmaker)

        try:
            # Sending the formatted newsletter to the admin
            await self._send_message(newsletter, request.state.bot, request.session.get("id"))
        except Exception as e:
            # Handling exceptions if the message sending fails
            raise ActionFailed(str(e))

        return "A message has been sent to you in chat with the bot!"

    @row_action(
        name="run_newsletter",
        text="Run newsletter",
        confirmation="Are you sure you want to run this newsletter?",
        action_btn_class="btn-outline-success",
        submit_btn_text="Continue",
        submit_btn_class="btn-outline-success",
    )
    async def run_newsletter_action(self, _: Request, pk: int) -> str:
        """
        Row action to run the newsletter and send it to the selected chat type.
        """
        # Creating a background task to run the newsletter
        loop = asyncio.get_event_loop()
        _ = loop.create_task(self.run_newsletter(int(pk)))

        return "The newsletter is up and running!"

    @classmethod
    async def run_newsletter(cls, newsletter_id: Union[int, str]) -> None:
        """
        Run the newsletter and send it to the selected chat type.
        """
        # Getting the current event loop and retrieving necessary components
        loop = asyncio.get_running_loop()
        bot: Bot = getattr(loop, "bot", None)
        config: Config = getattr(loop, "config", None)
        sessionmaker = getattr(loop, "sessionmaker", None)

        # Checking if essential components are set up in the event loop
        if not bot or not config or not sessionmaker:
            raise RuntimeError("Bot, config, or sessionmaker not properly set up in the event loop.")

        # Retrieving the newsletter based on its ID or job ID
        if isinstance(newsletter_id, str):
            # If the newsletter ID is a string (job ID), retrieve the newsletter by job ID
            newsletter = await NewsletterDB.get_by_job_id(sessionmaker, newsletter_id)
            # If the newsletter is not found, or it's not meant for broadcast, skip further processing
            if not newsletter or not newsletter.broadcast:
                return
        else:
            # If the newsletter ID is an integer, retrieve the newsletter by ID
            newsletter = await NewsletterDB.get(sessionmaker, newsletter_id)

        # Retrieving the chat IDs based on the newsletter's chat type
        chats = await cls._get_chat_ids(sessionmaker, newsletter, config)
        # Formatting the newsletter using a helper method
        newsletter = await cls.newsletter_format(newsletter, sessionmaker)

        for chat_id in chats:
            try:
                # Sending the formatted newsletter to each chat
                await cls._send_message(newsletter, bot, chat_id)
            except TelegramRetryAfter as e:
                # If rate limited, wait and try again
                await asyncio.sleep(e.retry_after)
                await cls._send_message(newsletter, bot, chat_id)
            except (TelegramBadRequest, Exception):
                # If chat is not found, or bot is blocked, or any other error, skip.
                pass
            await asyncio.sleep(0.05)

        if newsletter.start_date:
            # Updating the newsletter's broadcast status if it has a start date
            await NewsletterDB.update(sessionmaker, id=newsletter.id, broadcast=False)

    @staticmethod
    async def newsletter_format(newsletter: NewsletterDB, sessionmaker: async_sessionmaker) -> NewsletterDB:
        """
        Format the content of a newsletter by updating weekly statistics.
        """
        # Suppressing exceptions during the formatting process to ensure graceful handling
        with suppress(Exception):
            # Retrieve and update weekly stats for the newsletter content
            stats = await get_update_weekly_stats(sessionmaker)
            newsletter.content = format_weekly_notify_to_message(newsletter.content, stats)
        return newsletter

    @staticmethod
    async def _get_chat_ids(sessionmaker: async_sessionmaker, newsletter: NewsletterDB, config: Config):
        if newsletter.chat_type == "all":
            chats = await ChatDB.get_all_ids(sessionmaker)
        elif newsletter.chat_type == "admin":
            chats = await AdminDB.get_all_ids(sessionmaker)
            chats += [config.bot.DEV_ID, config.bot.ADMIN_ID]
        elif newsletter.chat_type == "private":
            chats = await UserDB.get_all_ids(sessionmaker)
        else:
            chats = await ChatDB.get_ids(sessionmaker, newsletter.chat_type)
        return chats

    @classmethod
    async def _send_message(cls, newsletter: NewsletterDB, bot: Bot, chat_id: int) -> None:
        """
        Send a message with the newsletter content and buttons to a chat.
        """
        message_params = {
            "chat_id": chat_id,
            "parse_mode": SULGUK_PARSE_MODE,
            "reply_markup": cls._build_buttons(newsletter.buttons),
        }

        if newsletter.image_path:
            message_params["photo"] = BufferedInputFile.from_file(newsletter.image_path)
            message_params["caption"] = newsletter.content
            await bot.send_photo(**message_params)
        else:
            message_params["text"] = newsletter.content
            await bot.send_message(**message_params)

    @staticmethod
    def _build_buttons(buttons: List[Dict[str, str]]) -> Markup:
        """
        Build inline buttons from a list of dictionaries.
        """
        inline_keyboard = [
            [Button(text=button.get("text"), url=button.get("url"))] for button in buttons
        ]
        return Markup(inline_keyboard=inline_keyboard)

    @classmethod
    def _get_trigger(cls, data: Dict[str, Any]) -> Union[DateTrigger, CronTrigger]:
        start_date = data.get("start_date")
        start_cron = data.get("start_cron")

        if start_date:
            try:
                return DateTrigger(start_date)
            except Exception as e:
                raise FormValidationError({"start_date": str(e)})
        else:
            values = start_cron.split()
            try:
                return CronTrigger(
                    minute=values[0], hour=values[1],
                    day=values[2], month=values[3],
                    day_of_week=values[4],
                )
            except Exception as e:
                raise FormValidationError({"start_cron": str(e)})

    @classmethod
    def _custom_validate(cls, request: Request, data: Dict[str, Any]) -> None:
        """
        Custom validation for newsletter creation and editing.
        """
        scheduler: AsyncIOScheduler = request.state.scheduler

        # Check if either content or image is provided
        if not data.get("image")[1] and len(data.get("content")) == 0:
            raise FormValidationError({"content": "Content or image is required."})

        # Check if content length is within limits
        cls.__validate_content_length(data.get("content"), 4096)

        # Check content length if image is provided
        if data.get("image"):
            cls.__validate_content_length(data.get("content"), 1024)

        # Validate start date and cron
        cls.__validate_date_and_cron(data.get("start_date"), data.get("start_cron"))

        # Validate broadcast checkbox
        cls.__validate_broadcast_checkbox(data, scheduler)

    @classmethod
    def __validate_broadcast_checkbox(cls, data: Dict[str, Any], scheduler: AsyncIOScheduler) -> None:
        job_id = data.get("job_id") if data.get("job_id") != "" else str(uuid4())
        data["job_id"] = job_id

        if data.get("broadcast"):
            trigger = cls._get_trigger(data)
            with suppress(JobLookupError):
                scheduler.remove_job(job_id)
            scheduler.add_job(cls.run_newsletter, trigger=trigger, args=[job_id], id=job_id)
        else:
            with suppress(JobLookupError):
                scheduler.remove_job(job_id)

    @staticmethod
    def __validate_content_length(content: str, limit: int) -> None:
        if len(content) > limit:
            raise FormValidationError({"content": f"The text limit is {limit} characters."})

    @staticmethod
    def __validate_date_and_cron(start_date: Optional[datetime], start_cron: Optional[str]) -> None:
        if not start_date and not start_cron:
            raise FormValidationError({"start_date": "Date or cron is required.",
                                       "start_cron": "Date or cron is required."})

        if start_date and start_cron:
            raise FormValidationError({"start_date": "Date and cron cannot be used at the same time.",
                                       "start_cron": "Date and cron cannot be used at the same time."})

        if start_date and start_date <= datetime.now():
            raise FormValidationError({"start_date": "Date cannot be in the past."})

        if start_cron and not bool(re.match(r"^(\*|\d+|\*/\d+)(\s+(\*|\d+|\*/\d+)){4}$", start_cron)):
            raise FormValidationError({"start_cron": "Invalid cron expression. "
                                                     "Example: 10 0 * * 1 - every Monday at 10."})
