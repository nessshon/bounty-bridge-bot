from __future__ import annotations

from typing import Union

from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker

from ._base import Base


class TextButtonDB(Base):
    """
    Model representing Button text table.
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

    __tablename__ = "text_buttons"
    __admin_icon__ = "fa-solid fa-circle-dot"
    __admin_label__ = "Text buttons"
    __admin_name__ = "Text button"
    __admin_identity__ = "text_button"

    @classmethod
    async def get(
            cls: TextButtonDB,
            sessionmaker: async_sessionmaker,
            code: str,
    ) -> Union[TextButtonDB, None]:
        """Get a record from the database by its code."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.code == code))
            result = await session.execute(statement)
            return result.scalar() or await cls.create(sessionmaker, code)

    @classmethod
    async def create(
            cls: TextButtonDB,
            sessionmaker: async_sessionmaker,
            code: str,
    ) -> TextButtonDB:
        """Create a new record in the database."""
        async with sessionmaker() as session:
            instance = TextButtonDB(code=code, text=code)
            session.add(instance)
            await session.commit()
            return instance
