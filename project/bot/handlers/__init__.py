from aiogram import Dispatcher

from . import channel
from . import group
from . import private
from . import errors


def bot_routers_include(dp: Dispatcher) -> None:
    """
    Include bot routers.
    """
    dp.include_routers(
        *[
            errors.router,
            private.command.router,
            private.callback_query.router,
            private.message.router,
            private.my_chat_member.router,
            channel.my_chat_member.router,
            group.my_chat_member.router,
        ]
    )


__all__ = [
    "bot_routers_include",
]
