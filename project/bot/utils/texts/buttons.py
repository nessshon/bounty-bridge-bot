from aiogram.types import (
    InlineKeyboardButton as Button,
    SwitchInlineQueryChosenChat,
    LoginUrl,
    WebAppInfo,
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from project.db.models import TextButtonDB
from ._init_value import InitValue


class ButtonCode(InitValue):
    CREATE_BOUNTY: str
    ISSUE_CREATED: str
    ISSUE_CLOSING: str
    ISSUE_APPROVED: str
    ISSUE_COMPLETED: str

    ISSUES_LIST: str
    ISSUE_INFO: str

    BACK: str
    MAIN: str


class TextButton:
    """
    Class representing a text button.
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        """
        Initialize the TextButton object.

        :param sessionmaker: An async_sessionmaker object for database operations.
        """
        self.sessionmaker = sessionmaker

    async def get(self, code: str) -> str:
        button = await TextButtonDB.get(self.sessionmaker, code)
        return button.text

    async def get_button(
            self,
            code: str,
            callback_data: str | None = None,
            url: str | None = None,
            web_app: WebAppInfo | None = None,
            login_url: LoginUrl | None = None,
            switch_inline_query: str | None = None,
            switch_inline_query_current_chat: str | None = None,
            switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = None,
    ) -> Button:
        text = await self.get(code)
        if callback_data:
            return Button(text=text, callback_data=callback_data)
        elif url:
            return Button(text=text, url=url)
        elif web_app:
            return Button(text=text, web_app=web_app)
        elif login_url:
            return Button(text=text, login_url=login_url)
        elif switch_inline_query:
            return Button(text=text, switch_inline_query=switch_inline_query)
        elif switch_inline_query_current_chat:
            return Button(text=text, switch_inline_query_current_chat=switch_inline_query_current_chat)
        elif switch_inline_query_chosen_chat:
            return Button(text=text, switch_inline_query_chosen_chat=switch_inline_query_chosen_chat)
        return Button(text=text, callback_data=code)
