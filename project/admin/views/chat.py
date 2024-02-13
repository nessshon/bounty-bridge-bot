from starlette_admin import *

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
    exclude_fields_from_create = ["created_at"]
    searchable_fields = [c.name for c in ChatDB.__table__.columns]  # type: ignore
