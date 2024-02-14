from aiogram.utils.markdown import hide_link
from sqlalchemy.ext.asyncio import async_sessionmaker

from project.db.models import TextMessageDB
from ._init_value import InitValue


class MessageCode(InitValue):
    ISSUE_CREATED: str
    ISSUE_CLOSING: str
    ISSUE_APPROVED: str
    ISSUE_COMPLETED: str

    MAIN_MENU: str
    ISSUES_LIST: str
    ISSUE_INFO: str

    UNKNOWN_ERROR: str


class TextMessage:
    """
    Class representing a text message.
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        """
        Initialize the TextMessage object.

        :param sessionmaker: An async_sessionmaker object for database operations.
        """
        self.sessionmaker = sessionmaker

    async def get(self, code: str) -> str:
        message = await TextMessageDB.get(self.sessionmaker, code)

        if message.preview_url:
            hidden_link = hide_link(message.preview_url)
            return message.text[:3] + hidden_link + message.text[3:]

        return message.text
