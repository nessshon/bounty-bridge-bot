from typing import Dict, Any

from aiogram import Bot
from aiogram.types import Chat
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette_admin import *
from starlette_admin.exceptions import FormValidationError

from ._model_view import CustomModelView
from ...db.models import ChatDB


class ChatView(CustomModelView):
    """
    View for managing chats table in the admin panel.
    """
    fields = [
        IntegerField(
            ChatDB.id.name, "ID",
            required=True,
            help_text="Unique identifier for this chat.",
        ),
        BooleanField(
            ChatDB.broadcast.name, "Broadcast",
            required=True,
            help_text="Enable if you want to send messages to this chat."
        ),
        StringField(
            ChatDB.type.name, "Type",
            read_only=True,
            help_text="Chat type (private, group, channel, etc.)",
        ),
        StringField(
            ChatDB.title.name, "Title",
            required=True,
        ),
        StringField(
            ChatDB.username.name, "Username",
            required=False,
        ),
        DateTimeField(
            ChatDB.created_at.name, "Created at",
            read_only=True,
        ),
    ]
    form_include_pk = True
    search_builder = True
    exclude_fields_from_create = [
        ChatDB.created_at.name,
        ChatDB.username.name,
        ChatDB.title.name,
        ChatDB.type.name,
    ]
    searchable_fields = [c.name for c in ChatDB.__table__.columns]  # type: ignore

    @staticmethod
    async def get_chat(bot: Bot, chat_id: int) -> Chat:
        """
        Validate the chat by its ID.
        """
        try:
            return await bot.get_chat(chat_id)
        except Exception as e:
            raise FormValidationError({"id": str(e)})

    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        try:
            bot: Bot = request.state.bot
            chat = await self.get_chat(bot, data["id"])
            data = await self._arrange_data(request, data)

            await self.validate(request, data)
            session: AsyncSession = request.state.session
            obj = await self._populate_obj(request, self.model(), data)
            obj.type = chat.type
            if chat.type == "private":
                obj.title = chat.full_name
            else:
                obj.title = chat.title
            obj.username = chat.username
            session.add(obj)
            await self.before_create(request, data, obj)
            if isinstance(session, AsyncSession):
                await session.commit()
                await session.refresh(obj)
            else:
                await anyio.to_thread.run_sync(session.commit)  # type: ignore[arg-type]
                await anyio.to_thread.run_sync(session.refresh, obj)  # type: ignore[arg-type]
            await self.after_create(request, obj)
            return obj
        except Exception as e:
            return self.handle_exception(e)
