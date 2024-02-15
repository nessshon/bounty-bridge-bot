from aiogram.utils.markdown import hide_link
from sqlalchemy.ext.asyncio import async_sessionmaker

from project.db.models import TextMessageDB
from ._init_value import InitValue


class MessageCode(InitValue):
    UNKNOWN_ERROR: str

    MAIN_MENU: str
    ISSUES_LIST: str
    ISSUE_INFO: str

    WEEKLY_DIGEST: str
    ISSUE_CREATED: str
    ISSUE_CLOSING: str
    ISSUE_APPROVED: str
    ISSUE_COMPLETED: str


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
            tag_index = message.text.find('>')
            hidden_link = hide_link(message.preview_url)
            return message.text[:tag_index + 1] + hidden_link + message.text[tag_index + 1:]

        return message.text
