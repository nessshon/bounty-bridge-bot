from starlette_admin.contrib.sqla import Admin

from ._model_view import AdminRoles

from .admin import AdminView
from .newsletter import NewsletterView
from .user import UserView
from .chat import ChatView
from .issue import IssueView
from .text_button import TextButtonView
from .text_message import TextMessageView

from ...db import models


def admin_views_add(admin: Admin) -> None:  # noqa
    """
    Add views to admin panel.
    """
    admin.add_view(
        AdminView(
            models.AdminDB,
            icon=models.AdminDB.__admin_icon__,
            label=models.AdminDB.__admin_name__,
            name=models.AdminDB.__admin_label__,
            identity=models.AdminDB.__admin_identity__,
        ),
    )
    admin.add_view(
        UserView(
            models.UserDB,
            icon=models.UserDB.__admin_icon__,
            label=models.UserDB.__admin_label__,
            name=models.UserDB.__admin_name__,
            identity=models.UserDB.__admin_identity__,
        ),
    )
    admin.add_view(
        ChatView(
            models.ChatDB,
            icon=models.ChatDB.__admin_icon__,
            label=models.ChatDB.__admin_label__,
            name=models.ChatDB.__admin_name__,
            identity=models.ChatDB.__admin_identity__,
        )
    )
    admin.add_view(
        IssueView(
            models.IssueDB,
            icon=models.IssueDB.__admin_icon__,
            label=models.IssueDB.__admin_label__,
            name=models.IssueDB.__admin_name__,
            identity=models.IssueDB.__admin_identity__,
        )
    )
    admin.add_view(
        NewsletterView(
            models.NewsletterDB,
            icon=models.NewsletterDB.__admin_icon__,
            label=models.NewsletterDB.__admin_label__,
            name=models.NewsletterDB.__admin_name__,
            identity=models.NewsletterDB.__admin_identity__,
        )
    )
    admin.add_view(
        TextButtonView(
            models.TextButtonDB,
            icon=models.TextButtonDB.__admin_icon__,
            label=models.TextButtonDB.__admin_label__,
            name=models.TextButtonDB.__admin_name__,
            identity=models.TextButtonDB.__admin_identity__,
        )
    ),
    admin.add_view(
        TextMessageView(
            models.TextMessageDB,
            icon=models.TextMessageDB.__admin_icon__,
            label=models.TextMessageDB.__admin_label__,
            name=models.TextMessageDB.__admin_name__,
            identity=models.TextMessageDB.__admin_identity__,
        )
    )


__all__ = [
    "admin_views_add",
    "AdminRoles"
]
