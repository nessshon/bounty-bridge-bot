from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from project.bot.manager import Manager


class ManagerMiddleware(BaseMiddleware):
    """
    Middleware for handling the manager object.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Call the middleware.

        :param handler: The handler function.
        :param event: The Telegram event.
        :param data: Additional data.
        """
        # Create a new manager object
        manager = Manager("💎", data)
        # Pass the config data to the handler function
        data["manager"] = manager

        # Call the handler function with the event and data
        return await handler(event, data)
