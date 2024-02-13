from __future__ import annotations

from typing import Union

from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker

from ._base import Base


class TextMessageDB(Base):
    """
    Model representing Message text table.
    """
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    code = Column(
        VARCHAR(length=128),
        nullable=False,
        unique=True,
    )
    text = Column(
        VARCHAR(length=1024),
        nullable=False,
    )
    preview_url = Column(
        VARCHAR(length=2048),
        nullable=True,
    )

    __tablename__ = "text_messages"
    __admin_icon__ = "fa-solid fa-message"
    __admin_label__ = "Text messages"
    __admin_name__ = "Text message"
    __admin_identity__ = "text_message"

    @classmethod
    async def get(
            cls: TextMessageDB,
            sessionmaker: async_sessionmaker,
            code: str,
    ) -> Union[TextMessageDB, None]:
        """Get a record from the database by its code."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.code == code))
            result = await session.execute(statement)
            return result.scalar() or await cls.create(sessionmaker, code)

    @classmethod
    async def create(
            cls: TextMessageDB,
            sessionmaker: async_sessionmaker,
            code: str,
    ) -> TextMessageDB:
        """Create a new record in the database."""
        async with sessionmaker() as session:
            instance = TextMessageDB(code=code, text=code)
            session.add(instance)
            await session.commit()
            return instance
