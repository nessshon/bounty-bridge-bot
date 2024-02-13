from __future__ import annotations

from typing import Union

from aiogram.enums import ChatMemberStatus
from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker

from . import Base


class UserDB(Base):
    """
    Model representing User table.
    """
    id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )
    state = Column(
        VARCHAR(length=6),
        nullable=False,
        default=ChatMemberStatus.MEMBER,
    )
    full_name = Column(
        VARCHAR(length=128),
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

    __tablename__ = "users"
    __admin_icon__ = "fas fa-user"
    __admin_label__ = "Users"
    __admin_name__ = "User"
    __admin_identity__ = "user"

    @classmethod
    async def get(
            cls,
            sessionmaker: async_sessionmaker,
            id_: int,
    ) -> Union[UserDB, None]:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as session:
            return await session.get(cls, id_)

    @classmethod
    async def update(
            cls: UserDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> Union[UserDB, None]:
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
    async def create(
            cls: UserDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> UserDB:
        """Create a new record in the database."""
        async with sessionmaker() as session:
            instance = UserDB(**kwargs)
            session.add(instance)
            await session.commit()
            return instance

    @classmethod
    async def create_or_update(
            cls: UserDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> UserDB:
        """Get and update a record from the database by its primary key."""
        instance = await cls.get(sessionmaker, kwargs["id"])
        if instance:
            return await cls.update(sessionmaker, **kwargs)
        return await cls.create(sessionmaker, **kwargs)

    async def __admin_repr__(self, _) -> str:
        """
        Get the string representation of a user for admin panel.
        """
        return f"{self.username or self.full_name} [{self.id}]"

    async def __admin_select2_repr__(self, _) -> str:
        """
        Get the HTML representation of a user for admin panel.
        """
        return f"<span>{self.username or self.full_name} [{self.id}]</span>"
