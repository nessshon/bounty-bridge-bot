from starlette.requests import Request
from starlette_admin import *

from ._model_view import CustomModelView
from ...db.models import UserDB

STATE_CHOICES = (
    ("kicked", "Kicked"),
    ("member", "Member"),
)


class UserView(CustomModelView):
    """
    View for managing users table in the admin panel.
    """
    fields = [
        IntegerField(
            UserDB.id.name, "ID",
            read_only=True,
            help_text="Unique identifier for this chat.",
        ),
        EnumField(
            UserDB.state.name, "State",
            required=False,
            read_only=True,
            choices=STATE_CHOICES,
            maxlength=6,
        ),
        BooleanField(
            UserDB.broadcast.name, "Broadcast",
            required=True,
            help_text="Enable if you want to send messages to this chat."
        ),
        StringField(
            UserDB.full_name.name, "Name",
            required=True,
            maxlength=64,
        ),
        StringField(
            UserDB.username.name, "Username",
            required=False,
            maxlength=65,
        ),
        DateTimeField(
            UserDB.created_at.name, "Created at",
            read_only=True
        ),
    ]
    form_include_pk = True
    exclude_fields_from_create = ["created_at"]
    searchable_fields = [c.name for c in UserDB.__table__.columns]  # type: ignore

    def can_create(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False
