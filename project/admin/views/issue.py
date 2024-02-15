from starlette.requests import Request
from starlette_admin import *

from ._model_view import CustomModelView
from ...db.models import IssueDB


class IssueView(CustomModelView):
    """
    View for managing issues table in the admin panel.
    """
    fields = [
        IntegerField(
            IssueDB.number.name, "Number",
            read_only=True,
            required=True,
        ),
        URLField(
            IssueDB.url.name, "URL",
            read_only=True,
            required=True,
        ),
        StringField(
            IssueDB.title.name, "Title",
            required=True,
        ),
        StringField(
            IssueDB.creator.name, "Creator",
            required=False,
        ),
        StringField(
            IssueDB.assignee.name, "Assignee",
            required=False,
        ),
        JSONField(
            IssueDB.assignees.name, "Assignees",
            required=False,
        ),
        JSONField(
            IssueDB.labels.name, "Labels",
            required=False,
        ),
        TextAreaField(
            IssueDB.rewards.name, "Rewards",
            required=False,
        ),
        TextAreaField(
            IssueDB.summary.name, "Summary",
            required=False,
        ),
        StringField(
            IssueDB.state.name, "State",
            required=True,
        ),
        StringField(
            IssueDB.state_reason.name, "State reason",
            required=False,
        ),
        DateTimeField(
            IssueDB.created_at.name, "Created at",
            read_only=True,
        ),
        DateTimeField(
            IssueDB.updated_at.name, "Updated at",
            read_only=True,
        ),
        DateTimeField(
            IssueDB.closed_at.name, "Closed at",
            read_only=True,
        ),
    ]
    page_size = 50
    search_builder = True
    fields_default_sort = (IssueDB.number, (IssueDB.number.name, True))
    searchable_fields = [c.name for c in IssueDB.__table__.columns]  # type: ignore

    def can_create(self, request: Request) -> bool:
        return False

    def can_edit(self, request: Request) -> bool:
        return False

    def can_delete(self, request: Request) -> bool:
        return False
