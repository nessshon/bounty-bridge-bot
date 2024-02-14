from aiogram import Dispatcher, Bot
from sulguk import AiogramSulgukMiddleware

from .database import DBSessionMiddleware
from .manager import ManagerMiddleware
from .throttling import ThrottlingMiddleware


def bot_middlewares_register(dp: Dispatcher, bot: Bot, **kwargs) -> None:
    """
    Register bot middlewares.
    """
    bot.session.middleware(AiogramSulgukMiddleware())

    dp.update.outer_middleware.register(DBSessionMiddleware(kwargs["sessionmaker"]))
    dp.update.outer_middleware.register(ThrottlingMiddleware())
    dp.update.outer_middleware.register(ManagerMiddleware())


__all__ = [
    "bot_middlewares_register",
]
