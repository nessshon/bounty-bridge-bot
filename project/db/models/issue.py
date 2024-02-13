from __future__ import annotations

from typing import Union, List, Sequence

from sqlalchemy import *
from sqlalchemy import Row, RowMapping
from sqlalchemy.ext.asyncio import async_sessionmaker

from . import Base
from ...github.models import Issue


class IssueDB(Base):
    """
    Model representing Issue table.
    """
    number = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
    )
    """Issue number."""

    url = Column(
        VARCHAR(255),
        nullable=False,
    )
    """URL to the GitHub issue."""

    title = Column(
        VARCHAR(512),
        nullable=False,
    )
    """Title of the issue."""

    creator = Column(
        VARCHAR(128),
        nullable=True,
    )
    """GitHub user login or None if not assigned."""

    assignee = Column(
        VARCHAR(64),
        nullable=True,
    )
    """GitHub user login or None if not assigned."""

    assignees = Column(
        JSON,
        nullable=True,
    )
    """List of GitHub user logins or None if not assigned."""

    labels = Column(
        JSON,
        nullable=True,
        default=[],
    )
    """List of GitHub label names or None if not assigned."""

    rewards = Column(
        VARCHAR(4096),
        nullable=True,
    )
    """Rewards of the issue or None if not assigned."""

    summary = Column(
        VARCHAR(2048),
        nullable=True,
    )
    """Summary of the issue or None if not assigned."""

    state = Column(
        VARCHAR(32),
        nullable=False,
    )
    """State of the issue (e.g. open, closed)."""

    state_reason = Column(
        VARCHAR(32),
        nullable=True,
    )
    """Reason for the state of the issue or None if not assigned (e.g. completed, not not_planned)."""

    created_at = Column(
        DateTime,
        nullable=False,
    )
    """Datetime when the issue was created."""

    updated_at = Column(
        DateTime,
        nullable=True,
    )
    """Datetime when the issue was last updated or None if not updated."""

    closed_at = Column(
        DateTime,
        nullable=True,
    )
    """Datetime when the issue was closed or None if not closed."""

    __tablename__ = "issues"
    __admin_icon__ = "fa-solid fa-circle-exclamation"
    __admin_label__ = "Issues"
    __admin_name__ = "Issue"
    __admin_identity__ = "issue"

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "url": self.url,
            "title": self.title,
            "creator": self.creator,
            "assignee": self.assignee,
            "assignees": ", ".join(self.assignees),  # noqa
            "labels": ", ".join(self.labels),  # noqa
            "rewards": self.rewards,
            "summary": self.summary,
            "state": self.state,
            "state_reason": self.state_reason,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None,
            "closed_at": self.closed_at.strftime("%Y-%m-%d %H:%M:%S") if self.closed_at else None,
        }

    def to_repr_dict(self) -> dict:
        def get_github_user_url(username: Any) -> str:
            return f"<a href='https://github.com/{username}'>{username}</a>"

        return {
            "frmt_number": f"#{self.number}",
            "frmt_title": f"<b>{self.title}</b>",
            "frmt_title_url": f"<a href='{self.url}'>{self.title}</a>",
            "frmt_creator": get_github_user_url(self.creator) if self.creator else "-",
            "frmt_assignee": get_github_user_url(self.assignee) if self.assignee else "-",
            "frmt_assignees": ", ".join(
                get_github_user_url(assignee) for assignee in self.assignees) if self.assignees else "-",
            "frmt_labels": ", ".join(self.labels) if self.labels else "-",  # noqa
            "frmt_rewards": self.rewards if self.rewards else "-",
            "frmt_summary": f"<blockquote>{self.summary}</blockquote>" if self.summary else "-",
            "frmt_state": f"<b>{self.state}" if self.state else "-",
            "frmt_state_reason": f"<b>{self.state_reason}</b>" if self.state_reason else "-",
            "frmt_created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "frmt_updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "-",
            "frmt_closed_at": self.closed_at.strftime("%Y-%m-%d %H:%M:%S") if self.closed_at else "-",
        }

    @classmethod
    async def get(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            number: int,
    ) -> Union[IssueDB, None]:
        """Get a record from the database by its primary key."""
        async with sessionmaker() as session:
            statement = select(cls).where(and_(cls.number == number))
            result = await session.execute(statement)
            return result.scalar()

    @classmethod
    async def update(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> Union[IssueDB, None]:
        """Update a record in the database."""
        async with sessionmaker() as session:
            instance = await session.get(cls, kwargs["number"])
            if instance:
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await session.commit()
                return instance
            return None

    @classmethod
    async def create(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> IssueDB:
        """Create a new record in the database."""
        async with sessionmaker() as session:
            instance = IssueDB(**kwargs)
            session.add(instance)
            await session.commit()
            return instance

    @classmethod
    async def create_or_update(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            **kwargs,
    ) -> IssueDB:
        """Get and update a record from the database by its primary key."""
        instance = await cls.get(sessionmaker, kwargs["number"])
        if instance:
            return await cls.update(sessionmaker, **kwargs)
        return await cls.create(sessionmaker, **kwargs)

    @classmethod
    async def get_all(cls, sessionmaker: async_sessionmaker) -> List[IssueDB]:
        """Get all records from the database."""
        async with sessionmaker() as session:
            statement = select(cls).order_by(cls.number.desc())
            result = await session.execute(statement)
            return result.scalars().all()  # type: ignore

    @classmethod
    async def update_all(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            issues: List[Issue],
    ) -> None:
        """Update all records in the database."""
        async with sessionmaker() as session:
            for issue in issues:
                await cls.create_or_update(sessionmaker, **issue.model_dump())
            await session.commit()

    @classmethod
    async def paginate(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            page_number: int,
            page_size: int = 10,
            filters: List[Any] = None,
            order_by: Union[Column, None] = None,
    ) -> Sequence[Row[Any] | RowMapping | Any]:
        """Get paginated records from the database by a filter."""
        async with sessionmaker() as async_session:
            statement = (
                select(cls)
                .limit(page_size).offset((page_number - 1) * page_size)
            )
            if filters is not None:
                statement = statement.filter(*filters)
            if order_by is not None:
                statement = statement.order_by(order_by)
            result = await async_session.execute(statement)
            return result.scalars().all()

    @classmethod
    async def total_pages(
            cls: IssueDB,
            sessionmaker: async_sessionmaker,
            page_size: int = 7,
            filters: List[Any] = None,
    ) -> int:
        """Get the total number of pages for a paginated query."""
        async with sessionmaker() as async_session:
            statement = select(func.count(cls.__table__.primary_key.columns[0]))
            if filters is not None:
                statement = statement.filter(*filters)
            query = await async_session.execute(statement)
            return (query.scalar() + page_size - 1) // page_size
