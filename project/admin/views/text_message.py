from starlette.requests import Request
from starlette_admin import *

from ._model_view import CustomModelView
from .fields import ImageFromURLField
from ...db.models import TextMessageDB


class TextMessageView(CustomModelView):
    """
    View for managing text messages table in the admin panel.
    """
    fields = [
        IntegerField(
            TextMessageDB.id.name, "ID",
            read_only=True,
            exclude_from_edit=True,
            exclude_from_create=True,
            exclude_from_detail=True,
        ),
        StringField(
            TextMessageDB.code.name, "Code",
            read_only=True,
        ),
        TextAreaField(
            TextMessageDB.text.name, "Text",
            required=True,
            maxlength=1024,
        ),
        ImageFromURLField(
            TextMessageDB.preview_url.name, "Preview URL",
            required=False,
            maxlength=2048,
        ),
    ]
    page_size = 50
    form_include_pk = False
    fields_default_sort = [TextMessageDB.id.name]
    exclude_fields_from_list = [TextMessageDB.code.name, TextMessageDB.id.name]
    searchable_fields = [c.name for c in TextMessageDB.__table__.columns]  # type: ignore

    def can_create(self, request: Request) -> bool:
        return False
