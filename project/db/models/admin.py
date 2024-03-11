from __future__ import annotations

from typing import Union, List

from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import relationship

from . import Base


class AdminDB(Base):
    """
    Model representing Admin table.
    """
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    user_id = Column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    roles = Column(
        JSON,
        nullable=False,
        default=[],
    )
    created_at = Column(
        DateTime,
        default=func.now(),
    )
    user = relationship("UserDB", backref="admin_users")

    __tablename__ = "admins"
    __admin_icon__ = "fas fa-user-tie"
    __admin_label__ = "Admin"
    __admin_name__ = "Admins"
    __admin_identity__ = "admin"

    @classmethod
    async def get(
            cls: AdminDB,
            sessionmaker: async_sessionmaker,
            id_: int,
    ) -> Union[AdminDB, None]:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.id == id_))
            result = await session.execute(statement)
            return result.scalar()

    @classmethod
    async def get_by_user_id(
            cls: AdminDB,
            sessionmaker: async_sessionmaker,
            user_id: int,
    ) -> Union[AdminDB, None]:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.user_id == user_id))
            result = await session.execute(statement)
            return result.scalar()

    @classmethod
    async def get_all_ids(
            cls: AdminDB,
            sessionmaker: async_sessionmaker,
    ) -> List[int]:
        """Get all ids from the database."""
        async with sessionmaker() as session:
            query = select(cls.user_id)
            result = await session.execute(query)
            return result.scalars().all()  # type: ignore
