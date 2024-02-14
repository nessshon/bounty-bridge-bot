from starlette.requests import Request
from starlette_admin import *

from ._model_view import CustomModelView
from ...db.models import TextButtonDB


class TextButtonView(CustomModelView):
    """
    View for managing text buttons table in the admin panel.
    """
    fields = [
        IntegerField(
            TextButtonDB.id.name, "ID",
            read_only=True,
            exclude_from_edit=True,
            exclude_from_create=True,
            exclude_from_detail=True,
        ),
        StringField(
            TextButtonDB.code.name, "Code",
            read_only=True,
        ),
        StringField(
            TextButtonDB.text.name, "Text",
            required=True,
            maxlength=1024,
        ),
    ]
    page_size = 50
    form_include_pk = False
    fields_default_sort = [TextButtonDB.id.name]
    exclude_fields_from_list = [TextButtonDB.code.name, TextButtonDB.id.name]
    searchable_fields = [c.name for c in TextButtonDB.__table__.columns]  # type: ignore

    def can_create(self, request: Request) -> bool:
        return False
