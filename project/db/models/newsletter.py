from __future__ import annotations

from typing import Union

from sqlalchemy import *
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy_file import ImageField
from sqlalchemy_file.validators import SizeValidator

from . import Base


class NewsletterDB(Base):
    """
    Model representing Newsletter table.
    """
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )
    image = Column(
        ImageField(
            upload_storage="image",
            thumbnail_size=(50, 50),
            validators=[SizeValidator("10M")],
        )
    )
    content = Column(
        VARCHAR(4096),
        nullable=False,
    )
    buttons = Column(
        JSON,
        nullable=True,
        default=None,
    )
    chat_type = Column(
        VARCHAR(8),
        nullable=False,
        default="all",
    )
    start_date = Column(
        DateTime,
        nullable=True,
        default=None,
    )
    start_cron = Column(
        VARCHAR(128),
        nullable=True,
        default=None,
    )
    broadcast = Column(
        BOOLEAN,
        nullable=False,
        default=False,
    )
    job_id = Column(
        VARCHAR(36),
        nullable=False,
        unique=True,
    )
    created_at = Column(
        DateTime,
        default=func.now(),
    )

    __tablename__ = "newsletters"
    __admin_icon__ = "fas fa-bullhorn"
    __admin_label__ = "Newsletters"
    __admin_name__ = "Newsletter"
    __admin_identity__ = "newsletter"

    @property
    def image_path(self) -> Union[str, None]:
        """Get the path to the image."""
        return self.image.get("url") if self.image and "url" in self.image else None

    @classmethod
    async def get(
            cls: NewsletterDB,
            sessionmaker: async_sessionmaker,
            id_: int,
    ) -> Union[NewsletterDB, None]:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.id == id_))
            result = await session.execute(statement)
            return result.scalar()

    @classmethod
    async def get_by_job_id(
            cls: NewsletterDB,
            sessionmaker: async_sessionmaker,
            job_id: str,
    ) -> Union[NewsletterDB, None]:
        """Get a record from the database by its job_id."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.job_id == job_id))
            result = await session.execute(statement)
            return result.scalar()

    @classmethod
    async def update(
            cls: NewsletterDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> Union[NewsletterDB, None]:
        """Update a record in the database."""
        async with sessionmaker() as session:
            instance = await session.get(cls, kwargs["id"])
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                return instance
            return instance
