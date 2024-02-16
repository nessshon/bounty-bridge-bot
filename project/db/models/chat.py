from __future__ import annotations

from typing import List, Union

from aiogram.enums import ChatMemberStatus
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
    broadcast = Column(
        BOOLEAN,
        nullable=False,
        default=False,
    )
    type = Column(
        VARCHAR(length=32),
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
    async def create(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> ChatDB:
        """Create a record in the database."""
        async with sessionmaker() as session:
            chat = ChatDB(**kwargs)
            session.add(chat)
            await session.commit()
            return chat

    @classmethod
    async def update(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> Union[ChatDB, None]:
        """Update a record in the database."""
        async with sessionmaker() as session:
            instance = await session.get(cls, kwargs["id"])
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                return instance
            return None

    @classmethod
    async def create_or_update(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> ChatDB:
        """Get and update a record from the database by its primary key."""
        instance = await cls.get(sessionmaker, kwargs["id"])
        if instance:
            return await cls.update(sessionmaker, **kwargs)
        return await cls.create(sessionmaker, **kwargs)

    @classmethod
    async def get(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
            chat_id: int,
    ) -> ChatDB:
        """Get a record from the database."""
        async with sessionmaker() as session:
            query = select(cls).where(and_(cls.id == chat_id))
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_all_ids(
            cls: ChatDB,
            sessionmaker: async_sessionmaker,
    ) -> List[int, None]:
        """Get all records from the database."""
        from .user import UserDB

        async with sessionmaker() as session:
            query = (
                select(ChatDB.id)
                .where(ChatDB.broadcast.is_(True))
                .union_all(
                    select(UserDB.id)
                    .where(
                        and_(
                            UserDB.broadcast.is_(True),
                            UserDB.state == ChatMemberStatus.MEMBER,
                        )
                    )
                )
            )
            result = await session.execute(query)
            return result.scalars().all()  # type: ignore
