from __future__ import annotations

from typing import List

from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker

from . import Base


class ChatDB(Base):
    """
    Model representing Chat table.
    """
    id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )
    title = Column(
        VARCHAR(length=255),
        nullable=False,
    )
    username = Column(
        VARCHAR(length=32),
        nullable=True,
    )
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
    )

    __tablename__ = "chats"
    __admin_icon__ = "fas fa-comments"
    __admin_label__ = "Chats"
    __admin_name__ = "Chat"
    __admin_identity__ = "chat"

    @classmethod
    async def get_all(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
    ) -> List[ChatDB]:
        """Get all records from the database."""
        async with sessionmaker() as session:
            query = select(cls)
            result = await session.execute(query)
            return result.scalars().all()  # type: ignore
