from __future__ import annotations

from datetime import datetime
from typing import List, Union, Any

from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator, Field


class Issue(BaseModel):
    """
    Model representing a GitHub issue.

    Attributes:
        number (int): Issue number.
        url (str): URL to the GitHub issue.
        title (str): Title of the issue.
        creator (Optional[str]): GitHub user login or None if not assigned.
        assignee (Optional[str]): GitHub user login or None if not assigned.
        assignees (List[Optional[str]]): List of GitHub user logins or None if not assigned.
        labels (List[Optional[str]]): List of GitHub label names or None if not assigned.
        rewards (Optional[str]): Rewards of the issue or None if not assigned.
        summary (Optional[str]): Summary of the issue or None if not assigned.
        state (str): State of the issue (e.g. open, closed).
        state_reason (Optional[str]): Reason for the state of the issue or None
         if not assigned (e.g. completed, not not_planned).
        created_at (datetime): Datetime when the issue was created.
        updated_at (Optional[datetime]): Datetime when the issue was last updated or None if not updated.
        closed_at (Optional[datetime]): Datetime when the issue was closed or None if not closed.
    """

    number: int
    url: str = Field(alias="html_url")
    title: str
    creator: Union[str, None] = Field(alias="user")
    assignee: Union[str, None]
    assignees: List[Union[str, None]]
    labels: List[Union[str, None]]
    rewards: Union[str, None] = Field(default="-", alias="body_html")
    summary: Union[str, None] = Field(default="-", alias="body_html")
    state: str
    state_reason: Union[str, None] = None
    created_at: datetime
    updated_at: Union[datetime, None]
    closed_at: Union[datetime, None]

    @field_validator("creator", mode="before")
    def extract_user_login(cls, value):  # noqa
        """Extracts GitHub user login from the given value."""
        return value["login"] if value else None

    @field_validator("assignee", mode="before")
    def extract_assignee_login(cls, value):  # noqa
        """Extracts GitHub assignee login from the given value."""
        return value["login"] if value else None

    @field_validator("assignees", mode="before")
    def extract_assignees_login(cls, values):  # noqa
        """Extracts GitHub assignees logins from the given values."""
        return [assignee["login"] if assignee else None for assignee in values]

    @field_validator("labels", mode="before")
    def extract_labels_name(cls, values):  # noqa
        """Extracts GitHub label names from the given values."""
        return [label["name"] if label else None for label in values]

    @field_validator("rewards", mode="before")
    def extract_rewards(cls, value):  # noqa
        """Extracts rewards from the given value (body)."""
        heading_patterns = ["h3", "h2", "h1"]
        rewards_patterns = ["REWARD", "Reward", "Estimate suggested reward"]
        return cls.extract_content(value, heading_patterns, rewards_patterns, 512)

    @field_validator("summary", mode="before")
    def extract_summary(cls, value):  # noqa
        """Extracts summary from the given value (body)."""
        heading_patterns = ["h3", "h2", "h1"]
        summary_patterns = ["Summary", "Introduction"]
        return cls.extract_content(value, heading_patterns, summary_patterns, 2048)

    @staticmethod
    def extract_content(
            value: Any,
            heading_patterns: List[str],
            content_patterns: List[str],
            max_length: int,
    ) -> Union[str, None]:
        """Extracts content from the given value (body)."""
        if not isinstance(value, str):
            return None

        paragraphs = []
        soup = BeautifulSoup(value, 'html.parser')

        for tag, text in [(_tag, _text) for _tag in heading_patterns for _text in content_patterns]:
            block = soup.find(tag, text=text)
            if block:
                next_element = block.find_next()
                if next_element and next_element.name in heading_patterns:
                    continue
                if max_length == 512:
                    content_elements = block.find_next(["ul", "li"])
                else:
                    content_elements = block.find_next("p")
                if content_elements:
                    paragraphs.append(str(content_elements))

        text = "".join(paragraphs)
        return None if (text is None) or (len(text) > max_length) else text
